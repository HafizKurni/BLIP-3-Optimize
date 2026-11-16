#!/usr/bin/env python3
import argparse, csv, json, math, random, re, string, time
from collections import defaultdict
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForVision2Seq, AutoTokenizer

MODEL = "Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5"
PUNCT = re.compile(r"[{}]".format(re.escape(string.punctuation)))
NUMBERS = {"zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","eight":"8","nine":"9","ten":"10"}

def norm(s):
    s = str(s).lower().strip().replace("\n", " ")
    s = PUNCT.sub("", s)
    words = [NUMBERS.get(x, x) for x in s.split() if x not in {"a", "an", "the"}]
    return re.sub(r"\s+", " ", " ".join(words)).strip()

def vqa_score(pred, answers):
    p = norm(pred); refs = [norm(x["answer"]) for x in answers]
    # Official VQAv2 leave-one-out score over the ten human answers.
    return sum(min(1.0, sum(p == refs[j] for j in range(10) if j != i) / 3.0) for i in range(10)) / 10.0

def clean(raw):
    return raw.split("<|end|>", 1)[0].splitlines()[0].strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["pilot", "final"], required=True)
    ap.add_argument("--base", default="/workspace/data/vqav2/5k")
    ap.add_argument("--model-dir", default="/workspace/models/xgen-mm-phi3-mini-instruct-interleave-r-v1.5")
    ap.add_argument("--output-dir", default="/workspace/outputs")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--warmup-count", type=int, default=10)
    ap.add_argument("--timing-count", type=int, default=500)
    args = ap.parse_args(); random.seed(args.seed); np.random.seed(args.seed)
    base, out = Path(args.base), Path(args.output_dir); (out/"predictions").mkdir(parents=True, exist_ok=True); (out/"metrics").mkdir(parents=True, exist_ok=True)
    qf = next(base.glob("*questions.json")); af = next(base.glob("*annotations.json"))
    questions = json.loads(qf.read_text())["questions"]; annotations = {x["question_id"]: x for x in json.loads(af.read_text())["annotations"]}
    rows = [{**q, **annotations[q["question_id"]]} for q in questions]
    if args.mode == "pilot":
        by = defaultdict(list)
        for r in rows: by[r["answer_type"]].append(r)
        counts = {"other":49,"yes/no":38,"number":13}
        rows = sum((random.sample(by[k], counts[k]) for k in counts), [])
    else:
        random.shuffle(rows)
    timing_ids = {r["question_id"] for r in (rows if args.mode == "pilot" else rows[:args.timing_count])}
    model = AutoModelForVision2Seq.from_pretrained(args.model_dir, trust_remote_code=True, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True).cuda().eval()
    tok = AutoTokenizer.from_pretrained(args.model_dir, trust_remote_code=True, use_fast=False, legacy=False); tok = model.update_special_tokens(tok); tok.padding_side="left"; tok.eos_token="<|end|>"
    proc = AutoImageProcessor.from_pretrained(args.model_dir, trust_remote_code=True)
    def infer(r, timed=False):
        path = base/"images"/"val2014"/f"COCO_val2014_{r['image_id']:012d}.jpg"; image=Image.open(path).convert("RGB")
        prompt = "<|system|>\nA chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.<|end|>\n<|user|>\n<image>\n"+r["question"]+"\nAnswer the question using a single word or phrase.<|end|>\n<|assistant|>\n"
        if timed: torch.cuda.synchronize(); start=time.perf_counter()
        pixels=proc([image], image_aspect_ratio="anyres")["pixel_values"].to("cuda",dtype=torch.bfloat16); inputs={"pixel_values":[[pixels]],**tok([prompt],return_tensors="pt")}
        for k,v in inputs.items():
            if isinstance(v,torch.Tensor): inputs[k]=v.cuda()
        with torch.inference_mode(): gen=model.generate(**inputs,image_size=[[image.size]],pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id,do_sample=False,num_beams=1,max_new_tokens=10)
        if timed: torch.cuda.synchronize(); latency=time.perf_counter()-start
        else: latency=None
        raw=tok.decode(gen[0],skip_special_tokens=True); return raw,clean(raw),latency
    for r in rows[:min(args.warmup_count,len(rows))]: infer(r, False)
    torch.cuda.reset_peak_memory_stats(); results=[]; lat=[]
    for i,r in enumerate(rows,1):
        raw,pred,latency=infer(r, r["question_id"] in timing_ids); score=vqa_score(pred,r["answers"]); 
        if latency is not None: lat.append(latency)
        results.append({"question_id":r["question_id"],"image_id":r["image_id"],"question":r["question"],"answer_type":r["answer_type"],"raw_output":raw,"prediction":pred,"vqa_accuracy":score,"latency_s":latency})
        if i%25==0: print(f"completed {i}/{len(rows)}",flush=True)
    vals=[x["vqa_accuracy"] for x in results]; by=defaultdict(list)
    for x in results: by[x["answer_type"]].append(x["vqa_accuracy"])
    boot=[]; rng=np.random.default_rng(args.seed)
    for _ in range(10000): boot.append(float(np.mean(rng.choice(vals,len(vals),replace=True))))
    metrics={"mode":args.mode,"n":len(results),"seed":args.seed,"accuracy":float(np.mean(vals)),"accuracy_95_ci":[float(np.percentile(boot,2.5)),float(np.percentile(boot,97.5))],"accuracy_by_answer_type":{k:float(np.mean(v)) for k,v in by.items()},"answers_longer_than_3_words":sum(len(x["prediction"].split())>3 for x in results)/len(results),"peak_allocated_gb":torch.cuda.max_memory_allocated()/1024**3,"peak_reserved_gb":torch.cuda.max_memory_reserved()/1024**3,"timing_count":len(lat),"latency_mean_s":float(np.mean(lat)) if lat else None,"latency_sd_s":float(np.std(lat,ddof=1)) if len(lat)>1 else None,"latency_median_s":float(np.median(lat)) if lat else None,"throughput_qps":float(len(lat)/sum(lat)) if lat and sum(lat)>0 else None,"model":MODEL,"model_dir":args.model_dir,"dtype":"bfloat16","max_new_tokens":10,"do_sample":False,"num_beams":1}
    stem=f"baseline_{args.mode}"; (out/"predictions"/f"predictions_{stem}.json").write_text(json.dumps(results,indent=2)); (out/"metrics"/f"metrics_{stem}.json").write_text(json.dumps(metrics,indent=2))
    with open(out/"predictions"/f"predictions_{stem}.csv","w",newline="") as f: w=csv.DictWriter(f,fieldnames=results[0].keys()); w.writeheader(); w.writerows(results)
    print(json.dumps(metrics,indent=2))
if __name__=="__main__": main()
