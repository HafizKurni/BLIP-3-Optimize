#!/usr/bin/env python3
"""Run one LM-FFN pruning experiment without retaining temporary checkpoints."""

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import torch

from prune_model import collect_activation_importance, find_language_ffns, prune_ffns, update_intermediate_size
from vqa_runtime import load_rows, load_runtime, load_split, infer, mean_ci, select_rows, vqa_score, write_jsonl


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def evaluate(model, tokenizer, processor, base, rows, output_path, timed=False):
    result = []
    for index, row in enumerate(rows, 1):
        raw, prediction, latency = infer(model, tokenizer, processor, base, row, timed=timed)
        result.append({
            "question_id": row["question_id"],
            "image_id": row["image_id"],
            "answer_type": row["answer_type"],
            "question": row["question"],
            "raw_output": raw,
            "prediction": prediction,
            "vqa_accuracy": vqa_score(prediction, row["answers"]),
            "latency_s": latency,
        })
        if index % 100 == 0:
            print(f"evaluation {index}/{len(rows)}", flush=True)
    write_jsonl(output_path, result)
    return result


def stats(rows):
    values = [row["vqa_accuracy"] for row in rows]
    accuracy, ci = mean_ci(values)
    by_type = {}
    for row in rows:
        by_type.setdefault(row["answer_type"], []).append(row["vqa_accuracy"])
    return {
        "n": len(rows),
        "accuracy": accuracy,
        "accuracy_95_ci": ci,
        "accuracy_by_answer_type": {key: sum(value) / len(value) for key, value in by_type.items()},
        "answers_longer_than_3_words": sum(len(row["prediction"].split()) > 3 for row in rows) / len(rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-dir", default="/workspace/models/xgen-mm-phi3-mini-instruct-interleave-r-v1.5")
    parser.add_argument("--dataset-root", default="/workspace/data/vqav2/5k")
    parser.add_argument("--cache-dir", default="/workspace/models/huggingface")
    parser.add_argument("--save-temp-checkpoint", action="store_true")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    try:
        config = json.loads(Path(args.config).read_text())
        study, experiment = config["study"], config["experiment"]
        if experiment.get("method") != "structured_pruning" or experiment.get("component") != "language_model":
            raise ValueError("This worker currently supports language-model structured pruning only")
        if experiment.get("unit") != "ffn_intermediate_channel":
            raise ValueError("This worker currently supports FFN intermediate channels only")

        base = Path(args.dataset_root)
        rows = load_rows(base)
        pilot = select_rows(rows, load_split(base, study["dataset"]["question_id_files"]["pilot"]))
        calibration = select_rows(rows, load_split(base, study["dataset"]["question_id_files"]["calibration"]))
        evaluation_rows = select_rows(rows, load_split(base, study["dataset"]["question_id_files"]["evaluation"]))
        timing_rows = select_rows(rows, load_split(base, study["dataset"]["question_id_files"]["timing"]))
        write(out / "dataset_counts.json", {"pilot": len(pilot), "calibration": len(calibration), "evaluation": len(evaluation_rows), "timing": len(timing_rows)})

        model, tokenizer, processor = load_runtime(args.model_dir, args.cache_dir)
        specs = find_language_ffns(model)
        write(out / "model_layout.json", {"ffn_layers": [spec.name for spec in specs], "old_intermediate_size": specs[0].old_size})

        def run_infer(row, timed=False):
            return infer(model, tokenizer, processor, base, row, timed=timed)

        importance = collect_activation_importance(model, specs, calibration, run_infer)
        write(out / "importance_summary.json", {name: {"mean_activation": float(values.mean()), "max_activation": float(values.max()), "min_activation": float(values.min())} for name, values in importance.items()})
        pruning_records, new_width = prune_ffns(specs, importance, float(experiment["fraction"]))
        write(out / "pruning_summary.json", {"records": pruning_records, "new_intermediate_size": new_width, "updated_config_objects": update_intermediate_size(model, new_width)})

        temp_checkpoint = out / "_temporary_checkpoint"
        if args.save_temp_checkpoint:
            model.save_pretrained(temp_checkpoint, safe_serialization=True)
            tokenizer.save_pretrained(temp_checkpoint)
            write(out / "temporary_checkpoint.json", {"path": str(temp_checkpoint), "status": "saved", "note": "Delete after reload validation."})

        torch.cuda.reset_peak_memory_stats()
        pilot_rows = evaluate(model, tokenizer, processor, base, pilot, out / "predictions_pilot.jsonl")
        pilot_metrics = stats(pilot_rows)
        write(out / "pilot_metrics.json", pilot_metrics)

        if pilot_metrics["accuracy"] < float(study["measurement"]["accuracy_retention_threshold"]) * float(study["baseline_accuracy"]):
            write(out / "gate.json", {"status": "pilot_failed_accuracy_gate", "pilot_accuracy": pilot_metrics["accuracy"]})
            raise RuntimeError("Pilot accuracy gate failed; full evaluation was not run")

        evaluation_result = evaluate(model, tokenizer, processor, base, evaluation_rows, out / "predictions_evaluation.jsonl")
        full_metrics = stats(evaluation_result)
        full_metrics["accuracy_retention"] = full_metrics["accuracy"] / float(study["baseline_accuracy"])
        write(out / "accuracy_metrics.json", {"pilot": pilot_metrics, "evaluation": full_metrics})

        passes = []
        torch.cuda.reset_peak_memory_stats()
        for pass_index in range(int(study["measurement"]["timed_passes"])):
            timed_rows = evaluate(model, tokenizer, processor, base, timing_rows, out / f"timing_pass_{pass_index + 1:02d}.jsonl", timed=True)
            passes.append([row["latency_s"] for row in timed_rows])
        latencies = [value for current in passes for value in current]
        efficiency = {
            "timed_question_count": len(timing_rows),
            "timed_passes": len(passes),
            "latency_mean_s": sum(latencies) / len(latencies),
            "latency_sd_s": float(torch.tensor(latencies).std(unbiased=True)),
            "throughput_qps": len(latencies) / sum(latencies),
            "peak_allocated_gb": torch.cuda.max_memory_allocated() / 1024**3,
            "peak_reserved_gb": torch.cuda.max_memory_reserved() / 1024**3,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
            "estimated_bfloat16_model_size_gb": sum(parameter.numel() for parameter in model.parameters()) * 2 / 1024**3,
            "temporary_checkpoint_retained": False,
        }
        write(out / "efficiency_metrics.json", efficiency)
        write(out / "environment.json", {
            "model_dir": args.model_dir,
            "dataset_root": args.dataset_root,
            "model_revision": study.get("model_revision"),
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "gpu": [torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())],
        })
        write(out / "gate.json", {"status": "passed", "pilot_accuracy": pilot_metrics["accuracy"]})
        print(json.dumps({"status": "completed", "experiment": experiment["id"], "accuracy": full_metrics["accuracy"]}, indent=2))
    except Exception as exc:
        write(out / "failure.json", {"status": "failed", "started_at_utc": started, "error": repr(exc)})
        raise
    finally:
        if "temp_checkpoint" in locals() and temp_checkpoint.exists() and not args.save_temp_checkpoint:
            shutil.rmtree(temp_checkpoint, ignore_errors=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
