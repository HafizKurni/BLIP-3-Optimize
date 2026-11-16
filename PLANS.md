# Baseline Testing Plan for BLIP-3

## Purpose

Run a small, reproducible baseline experiment before revising the proposal. The goal is to verify that the selected BLIP-3 checkpoint can load, process VQA data, generate answers, and produce measurable accuracy, latency, and GPU-memory results.

This pilot is not the final thesis experiment. It is preliminary work used to confirm technical feasibility and provide real evidence for the proposal.

## Recommended pilot scope

- Model: `Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5`.
- Precision: BF16 if the GPU supports it; otherwise document the fallback precision.
- Dataset: VQAv2 validation subset.
- Pilot size: approximately 100 questions, proportionally sampled by answer type.
- Random seed: `42`.
- Batch size: `1`.
- Decoding: greedy decoding, maximum 10 new tokens.
- Prompt: fixed across all runs; record the exact prompt in the experiment log.
- Warm-up: 10 inferences before timing.
- Timed passes: 3 passes over the pilot timing subset.

## Phase 0 — Select and control the GPU

1. Prefer a GPU with 8–12 GB VRAM for the deployment-validity check, ideally RTX 3060 12 GB or RTX 3060 Ti/RTX 4060 8 GB.
2. Record GPU model, VRAM, CUDA version, driver version, CPU, RAM, operating system, and region/provider.
3. Set a hard spending limit and delete the instance when it is not being used.
4. Store code, logs, question IDs, predictions, and summary results outside the temporary GPU instance.

## Phase 1 — Prepare the environment

1. Create a clean Linux GPU instance with Python, PyTorch, CUDA, Transformers, and the BLIP-3 checkpoint dependencies.
2. Pin package versions in a requirements file.
3. Verify the GPU with `nvidia-smi`.
4. Run a small tensor test in PyTorch and confirm that CUDA is available.
5. Record the exact environment before loading BLIP-3.

## Phase 2 — Load and smoke-test BLIP-3

1. Download or load the checkpoint.
2. Load one image and one VQAv2 question.
3. Run one forward/generation pass.
4. Confirm that the output is a non-empty answer and that no tensor-shape, tokenizer, image-processor, or CUDA error occurs.
5. Save the model-loading log and the first generated answer.

## Phase 3 — Create the pilot subsets

1. Load the VQAv2 validation annotations and questions.
2. Sample approximately 100 questions using proportional stratification across `yes/no`, `number`, and `other` answer types.
3. Use seed `42` and save the exact question IDs.
4. Check that every selected question has its image, question text, answer type, and ten reference answers.
5. Freeze the IDs so that the baseline and later pilot comparisons use exactly the same questions.

## Phase 4 — Run the baseline accuracy pilot

1. Use the fixed prompt and deterministic greedy decoding.
2. Generate one answer for each pilot question.
3. Save question ID, predicted answer, reference answers, answer type, and inference status.
4. Score the predictions with the official VQAv2 accuracy procedure or a checked reimplementation.
5. Report overall accuracy and accuracy separately for each answer type.

## Phase 5 — Measure baseline efficiency

1. Reset GPU peak-memory statistics.
2. Run 10 warm-up inferences and exclude them from the reported timing.
3. Run 3 timed passes over the same pilot questions.
4. Synchronize CUDA immediately before and after each inference.
5. Measure end-to-end latency from image preprocessing through answer generation.
6. Record mean latency, standard deviation, throughput, peak allocated memory, and peak reserved memory.
7. Record the saved checkpoint size on disk and the total parameter count.

## Phase 6 — Minimal pruning feasibility test

1. Select one component only; start with the language model or visual encoder.
2. Implement a 10% structural pruning test on one clearly defined unit type.
3. Verify that coupled QKV/output projections or feed-forward projections remain shape-compatible.
4. Save and reload the pruned checkpoint.
5. Run a forward pass on one sample and then on the 100-question pilot.
6. Do not claim successful pruning until the model saves, reloads, generates answers, and completes the pilot without errors.
7. Record the number of removed units, parameter count, accuracy, latency, and memory.

## Phase 7 — Decision gate

Proceed to full proposal revisions only if:

- the baseline loads and generates answers reliably;
- the baseline pilot produces a valid VQAv2 score;
- latency and memory measurements are repeatable;
- the exact GPU specification and access source are recorded; and
- at least one 10% component-pruning configuration completes a forward pass.

If pruning fails, keep the baseline results, document the failure, and revise the methodology before attempting all 15 configurations. Do not invent pilot values or present a failed feasibility test as a successful result.

## Minimum pilot evidence to insert into the proposal

Add a short `Preliminary Work` subsection containing:

1. GPU model, VRAM, provider, and access status.
2. BLIP-3 checkpoint and software versions.
3. Number of pilot questions and sampling method.
4. Baseline accuracy, mean latency, standard deviation, peak memory, and model size.
5. Result of the 10% pruning smoke test.
6. Any implementation limitation or unresolved issue.

## Suggested output files

- `pilot_environment.txt`
- `pilot_question_ids.json`
- `baseline_predictions.jsonl`
- `baseline_metrics.json`
- `pruning_smoke_test_metrics.json`
- `timing_log.csv`
- `PLANS.md`

## Cost-control rule

Run the 100-question baseline and one pruning smoke test first. Only rent longer or run the full experiment after the feasibility gate is passed. Shut down or delete the GPU instance immediately after exporting the logs and results.

## Starter environment and storage strategy

The recommended workflow is an ephemeral GPU instance plus persistent files stored outside the instance. The GPU VPS is treated as temporary compute, not as the permanent home of the model or results.

### Recommended folder structure

```text
rcvqa-blip3/
├── Dockerfile
├── requirements.txt
├── docker-compose.yml
├── data/
│   ├── raw/
│   ├── pilot/
│   └── question_ids.json
├── models/
│   └── blip3/
├── src/
├── configs/
├── outputs/
│   ├── predictions/
│   ├── metrics/
│   └── logs/
└── README.md
```

### Docker recommendation

Use Docker with an NVIDIA CUDA base image and mount `models`, `data`, and `outputs` as external volumes. This keeps the Python and CUDA environment reproducible while allowing the large model and results to survive container deletion.

The exact BLIP-3 loading code should be tested separately because xGen-MM may require checkpoint-specific model code and compatible versions of Transformers. Do not assume that the latest package versions will work.

Suggested first build sequence:

```bash
docker build -t rcvqa-blip3:pilot .
docker run --rm --gpus all \
  -v "$PWD/models:/workspace/models" \
  -v "$PWD/data:/workspace/data" \
  -v "$PWD/outputs:/workspace/outputs" \
  rcvqa-blip3:pilot nvidia-smi
```

The first successful container test should only verify CUDA and package imports. The second should load BLIP-3 and answer one question. The third should run the 100-question baseline.

### What to persist before deleting the VPS

At minimum, download or copy these files from the instance:

- exact pilot question IDs;
- baseline and pruning predictions;
- metrics JSON files;
- timing CSV files;
- environment information and package lock/requirements file;
- Dockerfile and source code;
- the compressed checkpoints created by the experiment;
- a short README recording the GPU and command used.

The raw VQAv2 images and annotations should be retained only if their license and storage requirements are acceptable. Otherwise, keep the dataset acquisition script and the frozen question IDs so the data can be reconstructed.

### Storage estimate

The following estimates include working overhead rather than only the final file size:

| Item | Smoke test | 100-question pilot | Full experiment |
|---|---:|---:|---:|
| BLIP-3 BF16 checkpoint and Hugging Face cache | 10–16 GB | 10–16 GB | 10–16 GB |
| Docker image and package layers | 5–8 GB | 5–8 GB | 5–8 GB |
| VQAv2 annotations and metadata | <1 GB | <1 GB | <1 GB |
| Pilot images and outputs | <1 GB | 1–2 GB | 2–5 GB |
| Full VQAv2 validation images, if downloaded | — | — | approximately 8–15 GB |
| Temporary files and safety margin | 5 GB | 8 GB | 10–15 GB |
| Recommended minimum working space | 20–25 GB | 25–35 GB | 40–55 GB |

The exact size depends on checkpoint file format, whether the model is downloaded more than once, Docker layer caching, and whether all VQAv2 validation images are retained. A compressed 4-billion-parameter BF16 model is theoretically around 8 GB for weights alone, but the practical working requirement is higher because of configuration files, tokenizer files, cache metadata, temporary downloads, and possible duplicate copies.

### Recommended allocation for this laptop

Because the laptop has approximately 60 GB free:

- Keep source code, Docker files, question IDs, metrics, predictions, and compressed archives on the laptop; these should normally remain below 5 GB.
- Store the BLIP-3 model cache, VQAv2 images, Docker image data, and intermediate checkpoints on the external SSD.
- Use a dedicated SSD folder such as `RCVQA_STORAGE/models`, `RCVQA_STORAGE/data`, and `RCVQA_STORAGE/outputs`.
- Keep at least 15 GB free on the SSD after copying the model and dataset.
- Do not keep duplicate model caches on both the laptop and SSD unless a backup is intended.

For the 100-question pilot, a 32 GB external SSD workspace is usually sufficient. For the full experiment with validation images, intermediate compressed checkpoints, and Docker caches, use at least 64 GB; 128 GB is more comfortable.

The safest arrangement is to mount the SSD folders into the project rather than copying them into the laptop disk:

```bash
mkdir -p /Volumes/RCVQA_SSD/RCVQA_STORAGE/{models,data,outputs}
```

Then point the Docker bind mounts to those folders. Before deleting the VPS, download only the outputs and checkpoints that are needed; the original model can be redownloaded from its recorded checkpoint revision if local space is limited.

### Local storage versus cloud storage

Use local storage as the primary working copy when possible because it avoids repeated download costs and is fastest for iteration. Use Google Drive, OneDrive, or another cloud drive as a backup for logs, question IDs, predictions, metrics, Docker files, and compressed checkpoints.

For the 4-billion-parameter baseline, keep at least 20–30 GB free locally or on the persistent volume for the model, cache, dataset subset, Docker layers, and outputs. A full dataset copy may require substantially more space. Do not store only the model cache; also export the exact checkpoint revision and configuration files.

### Cheap and safe VPS lifecycle

1. Prepare the Docker files, pilot IDs, and upload archive locally before renting the GPU.
2. Create the cheapest suitable GPU instance.
3. Upload the starter archive and restore the model/dataset from persistent storage.
4. Run `nvidia-smi`, the one-sample smoke test, and then the 100-question baseline.
5. Compress and download outputs immediately after each completed stage.
6. Keep a local copy and a cloud backup of the outputs.
7. Stop the instance when pausing briefly; delete the instance and attached disk when the work is finished.
8. Check the provider billing page after deletion to confirm that compute and storage charges have stopped.

Do not leave an instance running overnight. On marketplace providers, deleting the instance may also delete its local disk, so export results before deletion. If persistent volumes are used, delete unused volumes separately because they may continue to incur storage charges.

### Archive commands

Before deleting the VPS, create a portable archive:

```bash
tar -czf rcvqa-pilot-$(date +%Y%m%d).tar.gz \
  Dockerfile requirements.txt docker-compose.yml data outputs src configs README.md
```

Download the archive to the local computer and upload a second copy to cloud storage. Never rely on the temporary VPS disk as the only copy.

## Baseline protocol correction for future experiments

The first pilot revealed that prompt format and scoring protocol materially affect VQAv2 results. The first pilot is therefore treated as a pipeline test, not as the final baseline measurement.

All future baseline and compression experiments must use the following fixed protocol:

- Prompt instruction: `Answer the question using a single word or phrase.`
- Deterministic greedy decoding with a fixed maximum output length.
- Save both the raw model output and the cleaned answer used for scoring.
- Use the official VQAv2 normalization, including number-word conversion, article removal, punctuation handling, and contractions.
- Use official leave-one-out VQAv2 scoring across the ten human reference answers.
- Run 10 warm-up inferences before recording latency.
- Measure latency end-to-end from image preprocessing through answer decoding.
- Report mean latency, standard deviation, peak allocated memory, peak reserved memory, parameter count, and actual saved-weight size.
- Record the number of outputs longer than three words as a prompt-compliance diagnostic.

The corrected sequence is:

1. Rescore the original pilot with the official VQAv2 evaluator without rerunning the model.
2. Run the corrected baseline pilot with the short-answer prompt and corrected latency protocol.
3. Inspect raw outputs and prompt-compliance diagnostics.
4. Freeze the corrected script, prompt, seed, question IDs, and environment before testing pruning or quantization.

Do not compare compression results with the original pilot's accuracy unless the scoring and prompt protocol are identical. The original pilot may be reported as preliminary pipeline validation; the corrected pilot is the baseline for subsequent experiments.
