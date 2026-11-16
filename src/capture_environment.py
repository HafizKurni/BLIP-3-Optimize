#!/usr/bin/env python3
import argparse, json, platform, subprocess, sys
from importlib.metadata import version, PackageNotFoundError

def pkg(name):
    try: return version(name)
    except PackageNotFoundError: return None

def command(cmd):
    try: return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc: return f"unavailable: {exc}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--model-revision", default=None)
    args = ap.parse_args()
    data = {
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {n: pkg(n) for n in ["torch", "torchvision", "torchaudio", "transformers", "accelerate", "datasets", "safetensors", "torchao", "Pillow", "numpy", "pandas"]},
        "nvidia_smi": command(["nvidia-smi"]),
        "cuda_toolkit": command(["nvcc", "--version"]),
        "model_revision": args.model_revision,
    }
    try:
        import torch
        data["torch_cuda"] = torch.version.cuda
        data["gpu_count"] = torch.cuda.device_count()
        data["gpus"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
    except Exception as exc:
        data["torch_runtime_error"] = str(exc)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(json.dumps(data, indent=2, default=str))

if __name__ == "__main__": main()
