#!/usr/bin/env python3
"""Plan and resume a cost-controlled compression experiment grid.

The actual model transformation/evaluation worker is intentionally injected with
--worker. This keeps orchestration separate from architecture-specific pruning
code and prevents accidental expensive runs before that worker is validated.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_config(path):
    with open(path, encoding="utf-8") as handle:
        config = json.load(handle)
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported experiment grid schema_version")
    ids = set()
    for experiment in config.get("experiments", []):
        experiment_id = experiment.get("id")
        if not experiment_id or experiment_id in ids:
            raise ValueError(f"Missing or duplicate experiment id: {experiment_id!r}")
        ids.add(experiment_id)
    return config


def output_dir(root, experiment_id):
    return Path(root) / "experiments" / experiment_id


def completed(path):
    marker = path / "completion.json"
    if not marker.exists():
        return False
    try:
        return json.loads(marker.read_text(encoding="utf-8")).get("status") == "completed"
    except (OSError, json.JSONDecodeError):
        return False


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiment_grid.json")
    parser.add_argument("--output-root", default="/workspace/outputs")
    parser.add_argument("--plan", action="store_true", help="Validate and print enabled experiments")
    parser.add_argument("--run", action="store_true", help="Run enabled experiments through --worker")
    parser.add_argument("--resume", action="store_true", help="Skip experiments with completed markers")
    parser.add_argument("--only", action="append", help="Run only these experiment IDs")
    parser.add_argument("--worker", default="src/run_single_experiment.py")
    args = parser.parse_args()
    if not args.plan and not args.run:
        parser.error("choose --plan or --run")

    config = load_config(args.config)
    selected = set(args.only or [])
    experiments = sorted(
        [x for x in config["experiments"] if x.get("enabled") and (not selected or x["id"] in selected)],
        key=lambda x: (x.get("priority", 9999), x["id"]),
    )

    if args.plan:
        print("id\tmethod\tcomponent\tfraction\tquantization\tenabled")
        for experiment in sorted(config["experiments"], key=lambda x: (x.get("priority", 9999), x["id"])):
            print("\t".join([
                experiment["id"],
                experiment.get("method", ""),
                experiment.get("component", "-"),
                str(experiment.get("fraction", "-")),
                experiment.get("quantization", "-"),
                str(bool(experiment.get("enabled"))),
            ]))
        if not args.run:
            return

    worker = Path(args.worker)
    if not worker.exists():
        raise SystemExit(
            f"Worker not found: {worker}. Validate the architecture-specific worker before starting a paid run."
        )

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    for experiment in experiments:
        exp_dir = output_dir(output_root, experiment["id"])
        if args.resume and completed(exp_dir):
            print(f"SKIP completed {experiment['id']}", flush=True)
            continue
        exp_dir.mkdir(parents=True, exist_ok=True)
        write_json(exp_dir / "config.json", {"study": config["study"], "experiment": experiment})
        start = datetime.now(timezone.utc).isoformat()
        command = [
            sys.executable,
            str(worker),
            "--config", str(exp_dir / "config.json"),
            "--output-dir", str(exp_dir),
        ]
        write_json(exp_dir / "started.json", {
            "status": "running",
            "started_at_utc": start,
            "command": command,
            "pid": os.getpid(),
        })
        print(f"RUN {experiment['id']}", flush=True)
        with open(exp_dir / "run.log", "a", encoding="utf-8") as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
        status = "completed" if result.returncode == 0 else "failed"
        write_json(exp_dir / "completion.json", {
            "status": status,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "return_code": result.returncode,
        })
        if result.returncode != 0:
            print(f"FAILED {experiment['id']} (see {exp_dir / 'run.log'})", flush=True)
        else:
            print(f"DONE {experiment['id']}", flush=True)


if __name__ == "__main__":
    main()
