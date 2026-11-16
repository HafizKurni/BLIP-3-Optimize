#!/usr/bin/env bash
set -euo pipefail

# Vast.ai connection details
SSH_KEY="${HOME}/.ssh/id_ed25519"
SSH_PORT="33233"
SSH_HOST="ssh1.vast.ai"
REMOTE_BASE="/workspace"
LOCAL_BASE="$(pwd)/baseline_results"

mkdir -p "${LOCAL_BASE}/outputs/metrics" \
         "${LOCAL_BASE}/outputs/predictions" \
         "${LOCAL_BASE}/data"

echo "Downloading baseline metrics..."
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/outputs/metrics/baseline_pilot.json" \
  "${LOCAL_BASE}/outputs/metrics/"

echo "Downloading baseline predictions..."
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/outputs/predictions/baseline_pilot.json" \
  "${LOCAL_BASE}/outputs/predictions/"

echo "Downloading pilot question IDs and notebook..."
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/data/vqav2/pilot_questions.json" \
  "${LOCAL_BASE}/data/"
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/baseline_results.ipynb" \
  "${LOCAL_BASE}/"

echo "Downloading reproducibility scripts..."
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/src/baseline_one_sample.py" \
  "root@${SSH_HOST}:${REMOTE_BASE}/src/baseline_pilot.py" \
  "${LOCAL_BASE}/"

echo
echo "Baseline files downloaded to: ${LOCAL_BASE}"
find "${LOCAL_BASE}" -type f -maxdepth 4 -print
