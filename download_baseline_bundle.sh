#!/usr/bin/env bash
set -euo pipefail

SSH_KEY="${HOME}/.ssh/id_ed25519"
SSH_PORT="33233"
SSH_HOST="ssh1.vast.ai"
REMOTE_BASE="/workspace"
LOCAL_BASE="$(pwd)/baseline_download"

mkdir -p "${LOCAL_BASE}/model_blip3_original" \
         "${LOCAL_BASE}/data" \
         "${LOCAL_BASE}/outputs" \
         "${LOCAL_BASE}/notebooks" \
         "${LOCAL_BASE}/scripts" \
         "${LOCAL_BASE}/logs"

echo "Downloading baseline metrics and predictions..."
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/outputs/metrics/baseline_pilot.json" \
  "root@${SSH_HOST}:${REMOTE_BASE}/outputs/predictions/baseline_pilot.json" \
  "${LOCAL_BASE}/outputs/"

echo "Downloading pilot data and notebooks..."
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/data/vqav2/pilot_questions.json" \
  "${LOCAL_BASE}/data/"
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/baseline_results.ipynb" \
  "root@${SSH_HOST}:${REMOTE_BASE}/baseline_demo_visualization.ipynb" \
  "root@${SSH_HOST}:${REMOTE_BASE}/baseline_demo_visualization_executed.ipynb" \
  "${LOCAL_BASE}/notebooks/"

echo "Downloading reproducibility scripts..."
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/src/baseline_one_sample.py" \
  "root@${SSH_HOST}:${REMOTE_BASE}/src/baseline_pilot.py" \
  "root@${SSH_HOST}:${REMOTE_BASE}/src/pruning_poc.py" \
  "${LOCAL_BASE}/scripts/"

echo "Downloading original BLIP-3 model cache; this may take several minutes..."
scp -r -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/.hf_home/hub/models--Salesforce--xgen-mm-phi3-mini-instruct-interleave-r-v1.5/" \
  "${LOCAL_BASE}/model_blip3_original/"

echo "Downloading environment and run logs if available..."
scp -i "${SSH_KEY}" -P "${SSH_PORT}" \
  "root@${SSH_HOST}:${REMOTE_BASE}/outputs/preliminary_work/environment_and_baseline.json" \
  "root@${SSH_HOST}:${REMOTE_BASE}/outputs/preliminary_work/baseline_run.log" \
  "${LOCAL_BASE}/logs/" 2>/dev/null || true

echo "Backup completed: ${LOCAL_BASE}"
du -sh "${LOCAL_BASE}"/* 2>/dev/null || true
