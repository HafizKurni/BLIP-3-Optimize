# Reproducing the baseline environment

Start the same Vast.ai PyTorch/CUDA template, copy this file, the requirements file, the setup script, and `src/capture_environment.py` into `/workspace`, then run:

```bash
bash setup_reproducible_env.sh /workspace
```

Compare the captured environment files with the archived baseline records before loading the model. Load the model using its recorded Hugging Face revision/commit hash, not a moving `main` revision.

The base image digest, GPU, driver, CUDA, PyTorch, and torchao are recorded from the running instance because they are supplied by the Vast.ai image and host. They are intentionally not replaced by pip versions.
