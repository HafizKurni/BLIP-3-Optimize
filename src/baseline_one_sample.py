import json
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForVision2Seq, AutoTokenizer


MODEL_ID = "Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5"
BASE = Path("/workspace/data/vqav2")
CACHE = "/workspace/.hf_home"

row = json.loads((BASE / "pilot_questions.json").read_text())["questions"][0]
image_path = BASE / "images/val2014" / f"COCO_val2014_{row['image_id']:012d}.jpg"

print("question_id:", row["question_id"])
print("question:", row["question"])
print("image:", image_path, image_path.exists())

model = AutoModelForVision2Seq.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    cache_dir=CACHE,
).cuda().eval()
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID, trust_remote_code=True, use_fast=False, legacy=False, cache_dir=CACHE
)
image_processor = AutoImageProcessor.from_pretrained(
    MODEL_ID, trust_remote_code=True, cache_dir=CACHE
)
tokenizer = model.update_special_tokens(tokenizer)
tokenizer.padding_side = "left"
tokenizer.eos_token = "<|end|>"

image = Image.open(image_path).convert("RGB")
prompt = (
    "<|system|>\n"
    "A chat between a curious user and an artificial intelligence assistant. "
    "The assistant gives helpful, detailed, and polite answers to the user's questions."
    "<|end|>\n<|user|>\n<image>\n"
    + row["question"]
    + "<|end|>\n<|assistant|>\n"
)

pixel_values = image_processor(
    [image], image_aspect_ratio="anyres"
)["pixel_values"].to(device="cuda", dtype=torch.bfloat16)
inputs = {
    "pixel_values": [[pixel_values]],
    **tokenizer([prompt], return_tensors="pt"),
}
for name, value in inputs.items():
    if isinstance(value, torch.Tensor):
        inputs[name] = value.cuda()

torch.cuda.reset_peak_memory_stats()
torch.cuda.synchronize()
start = time.perf_counter()
with torch.inference_mode():
    generated = model.generate(
        **inputs,
        image_size=[[image.size]],
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        temperature=0.05,
        do_sample=False,
        max_new_tokens=10,
        top_p=None,
        num_beams=1,
    )
torch.cuda.synchronize()

prediction = tokenizer.decode(generated[0], skip_special_tokens=True).split("<|end|>")[0]
print("prediction:", prediction)
print("latency_s:", round(time.perf_counter() - start, 3))
print("peak_memory_gb:", round(torch.cuda.max_memory_allocated() / 1024**3, 3))
