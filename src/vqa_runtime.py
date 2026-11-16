#!/usr/bin/env python3
"""Shared BLIP-3 loading, prompting, inference, and VQAv2 scoring helpers."""

import json
import re
import string
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForVision2Seq, AutoTokenizer


MODEL_ID = "Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5"
NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10",
}
PUNCT = re.compile(r"[{}]".format(re.escape(string.punctuation)))


def normalize(text):
    text = str(text).lower().strip().replace("\n", " ")
    text = PUNCT.sub("", text)
    words = [NUMBER_WORDS.get(x, x) for x in text.split() if x not in {"a", "an", "the"}]
    return re.sub(r"\s+", " ", " ".join(words)).strip()


def vqa_score(prediction, answers):
    pred = normalize(prediction)
    refs = [normalize(item["answer"]) for item in answers]
    return sum(min(1.0, sum(pred == refs[j] for j in range(10) if j != i) / 3.0) for i in range(10)) / 10.0


def prompt(question):
    return (
        "<|system|>\nA chat between a curious user and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the user's questions."
        "<|end|>\n<|user|>\n<image>\n" + question +
        "\nAnswer the question using a single word or phrase.<|end|>\n<|assistant|>\n"
    )


def load_rows(base):
    base = Path(base)
    question_file = base / "questions.json"
    annotation_file = base / "annotations.json"
    if not question_file.exists():
        question_file = next(p for p in sorted(base.glob("*questions.json")) if "pilot_" not in p.name)
    if not annotation_file.exists():
        annotation_file = next(p for p in sorted(base.glob("*annotations.json")) if "pilot_" not in p.name)
    questions = json.loads(question_file.read_text())["questions"]
    annotations = {int(row["question_id"]): row for row in json.loads(annotation_file.read_text())["annotations"]}
    return [{**question, **annotations[int(question["question_id"])]} for question in questions]


def load_split(base, filename):
    ids = json.loads((Path(base) / filename).read_text())
    if isinstance(ids, dict):
        ids = ids["question_ids"]
    return {int(question_id) for question_id in ids}


def select_rows(rows, ids):
    selected = [row for row in rows if int(row["question_id"]) in ids]
    if len(selected) != len(ids):
        raise ValueError(f"Question split requested {len(ids)} IDs but found {len(selected)}")
    return selected


def load_runtime(model_dir, cache_dir=None):
    dtype = torch.bfloat16
    kwargs = {"trust_remote_code": True, "torch_dtype": dtype, "low_cpu_mem_usage": True}
    if cache_dir:
        kwargs["cache_dir"] = cache_dir
    model = AutoModelForVision2Seq.from_pretrained(model_dir, **kwargs).cuda().eval()
    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True, use_fast=False, legacy=False, cache_dir=cache_dir)
    processor = AutoImageProcessor.from_pretrained(model_dir, trust_remote_code=True, cache_dir=cache_dir)
    tokenizer = model.update_special_tokens(tokenizer)
    tokenizer.padding_side = "left"
    tokenizer.eos_token = "<|end|>"
    return model, tokenizer, processor


def infer(model, tokenizer, processor, base, row, timed=False):
    image_path = Path(base) / "images" / "val2014" / f"COCO_val2014_{int(row['image_id']):012d}.jpg"
    image = Image.open(image_path).convert("RGB")
    if timed:
        torch.cuda.synchronize()
    start = time.perf_counter()
    pixels = processor([image], image_aspect_ratio="anyres")["pixel_values"].to("cuda", dtype=torch.bfloat16)
    inputs = {"pixel_values": [[pixels]], **tokenizer([prompt(row["question"])], return_tensors="pt")}
    for name, value in inputs.items():
        if isinstance(value, torch.Tensor):
            inputs[name] = value.cuda()
    with torch.inference_mode():
        generated = model.generate(
            **inputs,
            image_size=[[image.size]],
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            do_sample=False,
            num_beams=1,
            max_new_tokens=10,
        )
    if timed:
        torch.cuda.synchronize()
    latency = time.perf_counter() - start
    raw = tokenizer.decode(generated[0], skip_special_tokens=True)
    prediction = raw.split("<|end|>", 1)[0].splitlines()[0].strip()
    return raw, prediction, latency


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def mean_ci(values, seed=42):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    bootstrap = [float(np.mean(rng.choice(values, len(values), replace=True))) for _ in range(2000)]
    return float(np.mean(values)), [float(np.percentile(bootstrap, 2.5)), float(np.percentile(bootstrap, 97.5))]
