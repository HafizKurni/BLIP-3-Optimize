#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${1:-/workspace}"
cd "$ROOT_DIR"
mkdir -p logs manifests
PYTHON_BIN="${PYTHON_BIN:-/venv/main/bin/python}"
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install --no-cache-dir -r requirements-reproducible.txt
"$PYTHON_BIN" src/capture_environment.py --output logs/environment_reference.json
"$PYTHON_BIN" -m pip freeze > logs/pip_freeze_reference.txt
nvidia-smi -q > logs/nvidia_smi_reference.txt
sha256sum requirements-reproducible.txt > manifests/requirements-reproducible.sha256
echo "Environment capture complete. Review logs before running inference."
