import json
import re
import string
import time
from collections import defaultdict
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForVision2Seq, AutoTokenizer

MODEL_ID = "Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5"
BASE = Path("/workspace/data/vqav2")
OUT = Path("/workspace/outputs")
CACHE = "/workspace/.hf_home"


def normalize(text):
    text = text.lower().strip()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text)
    return text


def score(prediction, answers):
    pred = normalize(prediction)
    refs = [normalize(x["answer"]) for x in answers]
    return min(1.0, sum(pred == x for x in refs) / 3.0)


def prompt(question):
    return (
        "<|system|>\nA chat between a curious user and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the user's questions."
        "<|end|>\n<|user|>\n<image>\n" + question +
        "<|end|>\n<|assistant|>\n"
    )


rows = json.loads((BASE / "pilot_questions.json").read_text())["questions"]
model = AutoModelForVision2Seq.from_pretrained(
    MODEL_ID, trust_remote_code=True, torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True, cache_dir=CACHE,
).cuda().eval()
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID, trust_remote_code=True, use_fast=False, legacy=False, cache_dir=CACHE
)
processor = AutoImageProcessor.from_pretrained(
    MODEL_ID, trust_remote_code=True, cache_dir=CACHE
)
tokenizer = model.update_special_tokens(tokenizer)
tokenizer.padding_side = "left"
tokenizer.eos_token = "<|end|>"

predictions = []
torch.cuda.reset_peak_memory_stats()
for i, row in enumerate(rows, 1):
    path = BASE / "images/val2014" / f"COCO_val2014_{row['image_id']:012d}.jpg"
    image = Image.open(path).convert("RGB")
    pixels = processor([image], image_aspect_ratio="anyres")["pixel_values"].to(
        device="cuda", dtype=torch.bfloat16
    )
    inputs = {"pixel_values": [[pixels]], **tokenizer([prompt(row["question"])], return_tensors="pt")}
    for name, value in inputs.items():
        if isinstance(value, torch.Tensor):
            inputs[name] = value.cuda()
    torch.cuda.synchronize()
    start = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(
            **inputs, image_size=[[image.size]],
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            do_sample=False, max_new_tokens=10, num_beams=1,
        )
    torch.cuda.synchronize()
    latency = time.perf_counter() - start
    prediction = tokenizer.decode(output[0], skip_special_tokens=True).split("<|end|>")[0].strip()
    predictions.append({**row, "prediction": prediction, "latency_s": latency})
    if i % 10 == 0:
        print(f"completed {i}/{len(rows)}", flush=True)

scores = [score(row["prediction"], row["answers"]) for row in predictions]
by_type = defaultdict(list)
for row, value in zip(predictions, scores):
    by_type[row["answer_type"]].append(value)
latencies = [row["latency_s"] for row in predictions]
mean_latency = sum(latencies) / len(latencies)
metrics = {
    "n": len(predictions),
    "accuracy": sum(scores) / len(scores),
    "accuracy_by_answer_type": {k: sum(v) / len(v) for k, v in by_type.items()},
    "mean_latency_s": mean_latency,
    "latency_sd_s": (sum((x - mean_latency) ** 2 for x in latencies) / len(latencies)) ** 0.5,
    "peak_memory_gb": torch.cuda.max_memory_allocated() / 1024**3,
    "model_id": MODEL_ID,
    "seed": 42,
}
(OUT / "predictions").mkdir(parents=True, exist_ok=True)
(OUT / "metrics").mkdir(parents=True, exist_ok=True)
(OUT / "predictions/baseline_pilot.json").write_text(json.dumps(predictions, indent=2))
(OUT / "metrics/baseline_pilot.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
