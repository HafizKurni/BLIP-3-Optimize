# Experiment Run Notes

This file records changes and additions applied during the Vast.ai baseline and
pruning run relative to the default repository checkout.

## Repository state

- Repository was fast-forwarded from `9a707d7` to `63639eb`.
- The working tree was clean after the pull.
- The new repository asset script is `scripts/download_assets.sh`.

## Runtime and assets

- Experiments run on Vast.ai with an NVIDIA GeForce RTX 3090 (24 GB VRAM).
- Python environment: `/venv/main`.
- Repository dependencies were installed from `requirements-reproducible.txt`.
- `pyarrow<19` was installed to resolve the image's preinstalled PyArrow versus
  pinned NumPy 1.26.4 ABI mismatch.
- The BLIP-3 checkpoint was downloaded to:
  `/workspace/models/xgen-mm-phi3-mini-instruct-interleave-r-v1.5/`.
- The required SigLIP visual encoder was populated in the Hugging Face cache
  during the first local model load.
- Frozen VQAv2 metadata and splits are under:
  `/workspace/data/vqav2/5k/`.
- The public `val2014.zip` supplied through Google Drive was downloaded to
  `/workspace/data/raw_vqav2/val2014.zip` after the original COCO URL failed
  certificate validation.
- Only the 4,584 images referenced by the 5,040-question evaluation set were
  copied to `/workspace/data/vqav2/5k/images/val2014/`.
- `/workspace` is not persistent; output backup is required before the instance
  is stopped or destroyed.

## Baseline result

- The 100-question pilot completed successfully.
- Pilot accuracy: `0.831`.
- Pilot 95% bootstrap CI: `0.764–0.892`.
- Mean latency: `0.2739 s/question`.
- Throughput: `3.6511 question/s`.
- Peak allocated GPU memory: `8.7339 GiB`.

## Pruning scope

- Current pruning target is the LLM language-model FFN intermediate channels.
- Importance method: activation times weight norm.
- Attention projections, token embeddings, output head, LayerNorm, residuals,
  visual encoder, and connector are not changed by the current worker.
- `prune_lm_10` passed the 100-question pilot gate with accuracy `0.833`.
- `prune_lm_20` and `prune_lm_30` are scheduled sequentially after the 10%
  run, because concurrent model loads would compete for GPU memory and make
  latency/memory comparisons invalid.

## Added run artifacts

- Per-configuration outputs are written under:
  `/workspace/outputs/experiments/prune_lm_10/`, and subsequently the 20% and
  30% directories.
- Each pruning summary records the affected module names, selected channels,
  original intermediate width, and new intermediate width.
- The planned combined summary is:
  `/workspace/outputs/pruning_parts_summary.json`.
- The planned compressed backup is:
  `/workspace/outputs/lm_pruning_results.tar.gz`.

## Local recovery copies

- Local copies of all three completed runs are stored as:
  `outputs/downloads/prune_lm_10.tar.gz`,
  `outputs/downloads/prune_lm_20.tar.gz`, and
  `outputs/downloads/prune_lm_30.tar.gz`.
- The files were originally named `.zip` by the remote shell command, but the
  actual format is gzip-compressed tar; the local copies were renamed to the
  correct `.tar.gz` extension.
- Extracted recovery contents are under:
  `outputs/downloads/pruning_results/`.
- Each archive contains the per-run configuration, model layout, pruning
  summary, pilot/evaluation predictions and metrics, timing passes,
  environment record, run log, and completion marker.
- Original model weights and VQAv2 images were not retained in these archives;
  a future GPU run must restore or redownload those assets.

## Operational notes

- The first direct call to `run_single_pruning_experiment.py` was rejected with
  `KeyError('experiment')` because it received the full grid instead of a
  per-experiment config. The corrected run uses `run_experiment_grid.py`.
- A stale `failure.json` from that rejected call may remain in the 10% output
  directory; the corrected grid-run process is the authoritative run.
- The first legacy smoke-test script used the old `/workspace/data/vqav2` path.
  The official pilot was run with the corrected `/workspace/data/vqav2/5k` path
  and the local checkpoint.
