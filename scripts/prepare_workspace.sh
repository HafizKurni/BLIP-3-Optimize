#!/usr/bin/env bash
set -euo pipefail

mkdir -p models data outputs configs
mkdir -p outputs/experiments outputs/logs outputs/predictions outputs/metrics

echo "Workspace directories are ready."
echo "Next: place the model under models/, place VQAv2 under data/, then run:"
echo "  python3 src/run_experiment_grid.py --config configs/experiment_grid.json --plan"
