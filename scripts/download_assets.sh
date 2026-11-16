#!/usr/bin/env bash
set -euo pipefail

# Download public assets outside Git. Run this on Vast.ai or another persistent
# Linux volume. The model revision should be pinned to the revision used for
# the completed baseline when that value is available.
ROOT_DIR="${1:-/workspace}"
MODEL_ID="Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5"
MODEL_REVISION="${MODEL_REVISION:-main}"
MODEL_DIR="${ROOT_DIR}/models/xgen-mm-phi3-mini-instruct-interleave-r-v1.5"
DATA_DIR="${ROOT_DIR}/data/vqav2/5k"
RAW_DIR="${ROOT_DIR}/data/raw_vqav2"
CLEANUP_RAW="${CLEANUP_RAW:-0}"

QUESTIONS_URL="https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Val_mscoco.zip"
ANNOTATIONS_URL="https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Annotations_Val_mscoco.zip"
IMAGES_URL="https://images.cocodataset.org/zips/val2014.zip"

mkdir -p "${MODEL_DIR}" "${DATA_DIR}" "${RAW_DIR}"

echo "[1/5] Downloading model ${MODEL_ID}@${MODEL_REVISION}"
python3 - "${MODEL_ID}" "${MODEL_REVISION}" "${MODEL_DIR}" <<'PY'
import sys
from huggingface_hub import snapshot_download

repo_id, revision, local_dir = sys.argv[1:]
snapshot_download(
    repo_id=repo_id,
    revision=revision,
    local_dir=local_dir,
    local_dir_use_symlinks=False,
)
print(f"Model saved to {local_dir}")
PY

download() {
  local url="$1"
  local output="$2"
  if [[ -s "$output" ]]; then
    echo "Using existing $output"
  else
    curl --fail --location --retry 3 --continue-at - "$url" --output "$output"
  fi
}

echo "[2/5] Downloading VQAv2 questions and annotations"
download "${QUESTIONS_URL}" "${RAW_DIR}/questions_val.zip"
download "${ANNOTATIONS_URL}" "${RAW_DIR}/annotations_val.zip"
unzip -o "${RAW_DIR}/questions_val.zip" -d "${RAW_DIR}"
unzip -o "${RAW_DIR}/annotations_val.zip" -d "${RAW_DIR}"
cp "${RAW_DIR}/v2_OpenEnded_mscoco_val2014_questions.json" "${DATA_DIR}/"
cp "${RAW_DIR}/v2_mscoco_val2014_annotations.json" "${DATA_DIR}/"

echo "[3/5] Creating frozen question splits"
python3 "${ROOT_DIR}/scripts/prepare_question_splits.py" --base "${DATA_DIR}"

echo "[4/5] Downloading COCO validation images"
download "${IMAGES_URL}" "${RAW_DIR}/val2014.zip"
if [[ ! -d "${RAW_DIR}/val2014" ]]; then
  unzip -q "${RAW_DIR}/val2014.zip" -d "${RAW_DIR}"
fi

echo "[5/5] Keeping only images referenced by the evaluation questions"
python3 "${ROOT_DIR}/select_vqa_images.py" \
  --source-images "${RAW_DIR}/val2014" \
  --dataset-dir "${DATA_DIR}" \
  --questions "${DATA_DIR}/v2_OpenEnded_mscoco_val2014_questions.json" \
  --annotations "${DATA_DIR}/v2_mscoco_val2014_annotations.json"

if [[ "${CLEANUP_RAW}" == "1" ]]; then
  rm -rf "${RAW_DIR}/val2014"
  rm -f "${RAW_DIR}/val2014.zip" "${RAW_DIR}/questions_val.zip" "${RAW_DIR}/annotations_val.zip"
  echo "Removed raw archives and the temporary full COCO image directory."
fi

echo
echo "Assets ready."
echo "Model: ${MODEL_DIR}"
echo "Dataset: ${DATA_DIR}"
echo "Model revision recorded in this run: ${MODEL_REVISION}"
echo "Next: python3 src/run_experiment_grid.py --config configs/experiment_grid.json --plan"
