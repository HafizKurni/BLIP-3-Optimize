import json
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForVision2Seq, AutoTokenizer

MODEL_ID = "Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5"
BASE = Path("/workspace/data/vqav2")
OUT = Path("/workspace/outputs/pruning_10_visual_tokenizer")
CACHE = "/workspace/.hf_home"

model = AutoModelForVision2Seq.from_pretrained(
    MODEL_ID, trust_remote_code=True, torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True, cache_dir=CACHE,
).cuda().eval()
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID, trust_remote_code=True, use_fast=False, legacy=False, cache_dir=CACHE
)
processor = AutoImageProcessor.from_pretrained(MODEL_ID, trust_remote_code=True, cache_dir=CACHE)
tokenizer = model.update_special_tokens(tokenizer)
tokenizer.padding_side = "left"
tokenizer.eos_token = "<|end|>"

# Proof-of-concept: prune 10% of FFN intermediate channels in one visual-tokenizer block.
block = model.get_submodule("vlm.vision_tokenizer.layers.0.1")
up = block[1]
down = block[3]
old_channels = up.out_features
keep_n = int(old_channels * 0.90)
importance = up.weight.detach().float().norm(dim=1)
keep = torch.topk(importance, keep_n, largest=True).indices.sort().values
new_up = torch.nn.Linear(up.in_features, keep_n, bias=False, device="cuda", dtype=torch.bfloat16)
new_down = torch.nn.Linear(keep_n, down.out_features, bias=False, device="cuda", dtype=torch.bfloat16)
with torch.no_grad():
    new_up.weight.copy_(up.weight[keep].to(torch.bfloat16))
    new_down.weight.copy_(down.weight[:, keep].to(torch.bfloat16))
block[1] = new_up
block[3] = new_down

OUT.mkdir(parents=True, exist_ok=True)
model.save_pretrained(OUT, safe_serialization=True)
tokenizer.save_pretrained(OUT)

row = json.loads((BASE / "pilot_questions.json").read_text())["questions"][0]
image = Image.open(BASE / "images/val2014" / f"COCO_val2014_{row['image_id']:012d}.jpg").convert("RGB")
prompt = ("<|system|>\nA chat between a curious user and an artificial intelligence assistant. "
          "The assistant gives helpful, detailed, and polite answers to the user's questions.<|end|>\n"
          "<|user|>\n<image>\n" + row["question"] + "<|end|>\n<|assistant|>\n")
pixels = processor([image], image_aspect_ratio="anyres")["pixel_values"].to(device="cuda", dtype=torch.bfloat16)
inputs = {"pixel_values": [[pixels]], **tokenizer([prompt], return_tensors="pt")}
for name, value in inputs.items():
    if isinstance(value, torch.Tensor): inputs[name] = value.cuda()
torch.cuda.synchronize(); start = time.perf_counter()
with torch.inference_mode():
    out = model.generate(**inputs, image_size=[[image.size]], pad_token_id=tokenizer.pad_token_id,
                         eos_token_id=tokenizer.eos_token_id, do_sample=False, max_new_tokens=10, num_beams=1)
torch.cuda.synchronize()
prediction = tokenizer.decode(out[0], skip_special_tokens=True).split("<|end|>")[0].strip()
result = {"component":"visual_tokenizer", "block":"layers.0.1", "unit":"FFN intermediate channel",
          "old_units":old_channels, "new_units":keep_n, "pruning_fraction":1-keep_n/old_channels,
          "question_id":row["question_id"], "question":row["question"], "prediction":prediction,
          "latency_s":time.perf_counter()-start, "peak_memory_gb":torch.cuda.max_memory_allocated()/1024**3}
(OUT / "pruning_poc_result.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
