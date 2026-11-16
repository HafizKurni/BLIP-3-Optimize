# BLIP-3 RCVQA Compression Study

Reproducible code for the BLIP-3 resource-constrained VQA study. The repository contains the baseline pipeline used previously, environment capture, VQAv2 scoring, latency and GPU-memory measurement, and the initial pruning proof of concept.

The repository intentionally does not contain model weights, VQAv2 images, generated predictions, or credentials. Those files are mounted into the container or stored in persistent Vast.ai storage.

## What is recorded

Every baseline run should preserve these files under `outputs/`:

- `environment.json`: Python, package versions, GPU, CUDA, driver, and model revision;
- `predictions/`: one record per question, including prediction, references, answer type, score, and latency;
- `metrics/`: accuracy, bootstrap confidence interval, accuracy by answer type, latency statistics, throughput, peak allocated/reserved memory, and run settings;
- `run_manifest.json`: command, timestamp, dataset/model locations, seed, and git commit, if available.

Do not report a result unless the environment record, frozen question IDs, predictions, and metrics are saved together.

## Local preparation

Create the folders before building:

```bash
mkdir -p models data outputs src configs
```

Build and open the container:

```bash
docker compose build
docker compose run --rm rcvqa bash
```

Inside the container, verify the GPU:

```bash
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

Do not run the full experiment until the checkpoint loads and one image-question pair produces an answer. Record the exact model revision and package versions in `outputs/logs/`.

## Vast.ai workflow

On the Vast.ai instance:

```bash
git clone <PRIVATE_OR_PUBLIC_REPOSITORY_URL> rcvqa-blip3
cd rcvqa-blip3
mkdir -p models data outputs configs
docker compose build
docker compose run --rm rcvqa nvidia-smi
```

Put the model at:

```text
models/xgen-mm-phi3-mini-instruct-interleave-r-v1.5/
```

Put the prepared VQAv2 subset at:

```text
data/vqav2/5k/
├── questions.json
├── annotations.json
└── images/val2014/*.jpg
```

Capture the environment before loading the model:

```bash
docker compose run --rm rcvqa python3 src/capture_environment.py \
  --output /workspace/outputs/environment.json \
  --model-revision "<HUGGING_FACE_COMMIT_OR_TAG>"
```

Run the one-sample smoke test first. The smoke-test script expects `data/vqav2/pilot_questions.json`; create it from the frozen pilot question file or use `src/baseline_final.py` for the standard run.

Run the 100-question pilot:

```bash
docker compose run --rm rcvqa python3 src/baseline_final.py \
  --mode pilot \
  --base /workspace/data/vqav2/5k \
  --model-dir /workspace/models/xgen-mm-phi3-mini-instruct-interleave-r-v1.5 \
  --output-dir /workspace/outputs
```

Run the full 5,040-question baseline only after the pilot succeeds:

```bash
docker compose run --rm rcvqa python3 src/baseline_final.py \
  --mode final \
  --base /workspace/data/vqav2/5k \
  --model-dir /workspace/models/xgen-mm-phi3-mini-instruct-interleave-r-v1.5 \
  --output-dir /workspace/outputs \
  --timing-count 500
```

The baseline uses seed 42, deterministic greedy decoding, BF16 inference, ten warm-up inferences, a fixed 500-question timing subset for the full run, and the official-style VQAv2 leave-one-out score implemented in `src/baseline_final.py`.

## Compression work order

1. Prune the language-model FFN channels at 10%, 20%, and 30%.
2. Prune the visual encoder at 10%, 20%, and 30%.
3. Prune the connector at 10%, 20%, and 30%.
4. Prune all three components together at 10%, 20%, and 30%.
5. Test INT8 quantization on the whole model.
6. Apply 30% full-model pruning followed by INT8 quantization.

The existing `src/pruning_poc.py` is an exploratory visual-tokenizer test. It is not yet a validated thesis configuration; preserve its output as a feasibility record and do not present it as a completed pruning result.

## Prepared experiment grid

The cost-controlled grid is defined in `configs/experiment_grid.json` and matches the fifteen-configuration thesis design: one baseline plus fourteen compressed configurations. Only `prune_lm_10` is enabled initially; other configurations are opened after their worker and pilot gate are validated.

Prepare a local or Vast.ai workspace with:

```bash
bash scripts/prepare_workspace.sh
python3 src/run_experiment_grid.py \
  --config configs/experiment_grid.json \
  --plan
```

The grid runner is resumable. Once the architecture-specific worker is validated, start it with:

```bash
python3 scripts/prepare_question_splits.py \
  --base /workspace/data/vqav2/5k

python3 src/run_experiment_grid.py \
  --config configs/experiment_grid.json \
  --output-root /workspace/outputs \
  --run --resume
```

The pruning worker is separate from the grid runner because BLIP-3's fused projections require architecture-specific slicing. It currently supports language-model FFN intermediate-channel pruning using activation-times-weight-norm importance. It writes one `completion.json` marker per configuration, so a restarted session skips configurations that already completed.

Read `EXPERIMENT_PROTOCOL.md` before enabling the remaining grid. It defines the frozen data partitions, output contract, pilot gate, and the no-temporary-checkpoint storage policy.

## Download model and VQAv2 assets on Vast.ai

The model weights and VQAv2/COCO data are downloaded outside GitHub. The helper first downloads the public BLIP-3 checkpoint, then VQAv2 validation questions and annotations, then COCO `val2014.zip`. It copies only the images referenced by the evaluation questions into the working dataset directory.

Run this after cloning the repository and installing the requirements:

```bash
export MODEL_REVISION=main  # replace with the exact baseline revision when recorded
export CLEANUP_RAW=1        # remove temporary full COCO archive and extracted folder after copying
bash scripts/download_assets.sh /workspace
```

The official VQAv2 download page provides the validation questions, annotations, and COCO validation images. The BLIP-3 model is downloaded from the Salesforce Hugging Face repository. The model is about 8.7 GB, so use persistent storage and allow enough disk space for the temporary COCO archive. The raw downloads are not committed to Git.

The repository also contains the previously prepared 5,040-question metadata under `data/metadata/`. Because that subset matches the completed baseline, `download_assets.sh` uses it automatically when present. It still downloads COCO images, but copies only the 4,584 referenced images instead of the entire validation image set.

After the download, verify:

```bash
test -f /workspace/models/xgen-mm-phi3-mini-instruct-interleave-r-v1.5/config.json
test -f /workspace/data/vqav2/5k/v2_OpenEnded_mscoco_val2014_questions.json
test -f /workspace/data/vqav2/5k/v2_mscoco_val2014_annotations.json
test -f /workspace/data/vqav2/5k/question_splits.json
find /workspace/data/vqav2/5k/images/val2014 -type f | wc -l
```

## VPS use

Upload this folder to the temporary GPU instance, run the pilot, download `outputs/`, and delete the instance. Keep `models/` on local storage or a persistent cloud-backed volume; do not assume the VPS disk survives deletion.

## Important compatibility note

The BLIP-3/xGen-MM checkpoint may require checkpoint-specific modeling code and a compatible Transformers version. If loading fails, preserve the error log and adjust the pinned versions deliberately; do not silently use a different model checkpoint.

## Vast.ai data safety

Use a persistent volume for `models/`, `data/`, and `outputs/`. Before stopping or deleting the instance, copy the complete `outputs/` directory and the exact environment record to local storage. Never commit those files if they contain large datasets, generated outputs, or credentials.
