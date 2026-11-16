#!/usr/bin/env python3
"""Create deterministic, recorded question-ID partitions for compression runs."""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def find_json(base, kind):
    exact = base / f"{kind}.json"
    if exact.exists():
        return exact
    matches = sorted(p for p in base.glob(f"*{kind}.json") if "pilot_" not in p.name)
    if not matches:
        raise FileNotFoundError(f"Could not find {kind}.json under {base}")
    return matches[0]


def write_ids(path, rows):
    path.write_text(json.dumps([int(row["question_id"]) for row in rows], indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Directory containing VQAv2 questions/annotations")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--pilot-counts", default="other=49,yes/no=38,number=13")
    parser.add_argument("--calibration-count", type=int, default=256)
    parser.add_argument("--timing-count", type=int, default=500)
    args = parser.parse_args()

    base = Path(args.base)
    questions = json.loads(find_json(base, "questions").read_text())["questions"]
    annotations = json.loads(find_json(base, "annotations").read_text())["annotations"]
    by_id = {int(row["question_id"]): row for row in annotations}
    rows = [{**question, **by_id[int(question["question_id"])]} for question in questions]
    rng = random.Random(args.seed)

    counts = {}
    for item in args.pilot_counts.split(","):
        key, value = item.split("=", 1)
        counts[key] = int(value)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["answer_type"]].append(row)
    pilot = []
    for answer_type, count in counts.items():
        pilot.extend(rng.sample(grouped[answer_type], count))
    pilot_ids = {int(row["question_id"]) for row in pilot}

    remaining = [row for row in rows if int(row["question_id"]) not in pilot_ids]
    rng.shuffle(remaining)
    calibration = remaining[: args.calibration_count]
    calibration_ids = {int(row["question_id"]) for row in calibration}
    remaining = [row for row in remaining if int(row["question_id"]) not in calibration_ids]
    timing = remaining[: args.timing_count]

    write_ids(base / "pilot_question_ids.json", pilot)
    write_ids(base / "calibration_question_ids.json", calibration)
    write_ids(base / "timing_question_ids.json", timing)
    write_ids(base / "evaluation_question_ids.json", rows)

    summary = {
        "seed": args.seed,
        "total_questions": len(rows),
        "pilot_count": len(pilot),
        "calibration_count": len(calibration),
        "timing_count": len(timing),
        "pilot_answer_types": counts,
        "disjoint_pilot_calibration": not (pilot_ids & calibration_ids),
        "disjoint_calibration_timing": not (calibration_ids & {int(row["question_id"]) for row in timing}),
    }
    (base / "question_splits.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
