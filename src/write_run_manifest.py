#!/usr/bin/env python3
"""Write a small provenance record beside an experiment's outputs."""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def git_value(args):
    try:
        return subprocess.check_output(["git", *args], text=True).strip()
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/workspace/outputs/run_manifest.json")
    parser.add_argument("--stage", choices=["smoke", "pilot", "final", "pruning", "quantization"], required=True)
    parser.add_argument("--command", nargs="*", default=sys.argv)
    parser.add_argument("--model-revision")
    parser.add_argument("--dataset")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stage": args.stage,
        "command": args.command,
        "model_revision": args.model_revision,
        "dataset": args.dataset,
        "seed": args.seed,
        "python": sys.version,
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_status": git_value(["status", "--short"]),
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
