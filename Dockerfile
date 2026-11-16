FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/workspace/models/huggingface \
    TRANSFORMERS_CACHE=/workspace/models/huggingface

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git git-lfs libgl1 libglib2.0-0 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install --index-url https://download.pytorch.org/whl/cu124 torch torchvision \
    && python3 -m pip install -r /workspace/requirements.txt

COPY . /workspace
CMD ["bash"]
