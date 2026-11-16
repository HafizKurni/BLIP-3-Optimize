# Smart Presentation Speaker Notes

## Main presentation strategy

Present the research as one clear story:

> **BLIP-3 is accurate, but too expensive for limited hardware. This study tests whether compression can reduce the cost without losing too much accuracy, and identifies which configuration is actually deployable.**

Use this logic throughout the presentation:

1. Explain the deployment problem.
2. Show why existing studies do not fully answer it.
3. Explain the controlled experiment.
4. Show what is already known from the baseline.
5. Explain what the main experiments will determine.

The total timing from the slide plan is approximately **19 minutes**. Do not read every bullet. Use the slides as visual support and speak the short script below.

## Opening technique

Start with the practical problem, not with the title:

> “A large vision–language model can answer image questions accurately, but accuracy alone does not tell us whether the model can run on an ordinary GPU. My research asks whether BLIP-3 can be compressed enough for resource-constrained deployment while keeping acceptable VQA accuracy.”

Then introduce the title and research direction.

## Slide-by-slide talk track

### Slide 1 — Title

**Say:**

> “Good morning/afternoon. My research is titled *A Compression Benchmarking Framework for Evaluating Efficiency–Accuracy Trade-offs in BLIP-3 for Resource-Constrained Visual Question Answering*. The central question is whether compression can make BLIP-3 more practical without causing unacceptable accuracy loss.”

**Transition:**

> “To understand the problem, I will first explain why VQA models are becoming difficult to deploy.”

### Slide 2 — Background

**Say:**

> “Visual Question Answering requires a model to understand both an image and a natural-language question. Modern vision–language models perform this task well, but they are also becoming larger. BLIP-3 contains a visual encoder, a multimodal connector, and a language model. These components increase memory use, storage requirements, and inference time. Therefore, a high accuracy score does not give the complete picture of practical usefulness.”

**Emphasize:**

Accuracy is necessary, but it is not sufficient for deployment.

### Slide 3 — Problem Statement

**Say:**

> “The deployment gap is the main problem. BLIP-3 may work well in a high-resource environment, but consumer hardware has stricter limits. The research problem has four parts: limited controlled comparison of compression techniques for BLIP-3, limited evidence about BLIP-3 under consumer-grade limits, limited component-level analysis, and limited use of explicit deployment thresholds.”

**Smart point:**

Do not say that previous research is wrong. Say that it does not answer the complete deployment question for BLIP-3.

### Slide 4 — Research Questions and Objectives

**Say:**

> “The questions follow a sequence. RQ1 measures the general effect of pruning and quantization. RQ2 looks inside the model to compare the three main components. RQ3 compares combined compression with single techniques. Finally, RQ4 turns the measurements into a deployment recommendation.”

**Transition:**

> “Before describing my method, I reviewed the closest studies and identified what is still missing.”

### Slide 5 — Literature Comparison

**Say:**

> “Previous studies have examined quantized VQA, visual-token pruning, joint compression, and the internal effects of compression. These studies provide useful foundations. However, they use different model families, different tasks, or different evaluation goals. None provides the same controlled BLIP-3 comparison with component analysis and explicit deployment thresholds.”

**Avoid:**

Do not read all study names and details. Explain the pattern across the studies.

### Slide 6 — Research Gap and Contribution

**Say:**

> “The gap is therefore an integration and deployment-evaluation gap. This study contributes one controlled benchmark for BLIP-3, component-level sensitivity analysis, Pareto-based comparison, and a deployment decision based on four explicit criteria. The contribution is not a new compression algorithm. It is a reproducible way to evaluate whether compression is useful in practice.”

**Strong sentence:**

> “The study evaluates not only how much the model shrinks, but whether the smaller model remains useful.”

### Slide 7 — BLIP-3 and Compression Techniques

**Say:**

> “BLIP-3 is treated as three connected parts. The visual encoder processes the image, the connector transfers visual information into the language model, and the language model generates the answer. Structured pruning removes complete architectural units. INT8 weight-only quantization stores weights using lower precision while keeping activations at higher precision. The combined configuration applies full-model pruning first and quantization second.”

**Important clarification:**

> “I do not assume that quantization will always reduce latency. Latency depends on the hardware and software backend, so it will be measured.”

### Slide 8 — Theoretical and Conceptual Framework

**Say:**

> “The framework combines three ideas. Model redundancy explains why compression is worth testing. The efficiency–accuracy trade-off explains why resource savings must be considered together with accuracy. The resource-constraint perspective defines the hardware limits. Together, they lead from compression strategy to resource measurements, then to accuracy, Pareto position, and deployability.”

**Transition:**

> “These relationships lead to three hypotheses.”

### Slide 9 — Hypotheses

**Say:**

> “H1 expects compression to reduce memory and model size, while stronger pruning may reduce accuracy retention. H2 expects the BLIP-3 components to differ in their contribution and sensitivity. H3 expects combined compression to have a different profile from single techniques. Importantly, the hypotheses do not assume that one method will automatically be the best.”

**Smart point:**

Mention that RQ4 is descriptive because deployability is decided by the measured thresholds.

### Slide 10 — Research Design

**Say:**

> “This is a controlled quantitative comparative experiment. All configurations use the same checkpoint, data, preprocessing, prompt, decoding settings, and measurement procedures. The component-level track prunes one component at a time. The full-model track compresses all components together. In total, fifteen configurations are evaluated: one baseline and fourteen compressed configurations.”

**Emphasize:**

The purpose of the controls is to attribute differences to compression rather than to changes in data or environment.

### Slide 11 — Compression Procedures

**Say:**

> “Pruning is tested at 10%, 20%, and 30%. It targets eligible structural units such as feed-forward channels and attention heads. Quantization uses INT8 weight-only W8A16. The combined configuration uses 30% full-model pruning followed by INT8 quantization. The language model contains fused projection matrices, so pruning must preserve tensor shapes and head dimensions. Every pruned model must pass a forward check before evaluation.”

### Slide 12 — Dataset and Sampling

**Say:**

> “The source dataset is the VQAv2 validation set. I use three fixed subsets. The 5,040-question evaluation subset measures accuracy. The 500-question timing subset measures latency and memory. The 256-question calibration subset estimates pruning importance. The subsets are proportionally stratified by answer type and frozen before the comparisons begin, so every configuration answers the same questions.”

**Key reason:**

Same questions make the comparison fair and reduce the risk that data difficulty explains the result.

### Slide 13 — Metrics and Measurement

**Say:**

> “The study measures task performance and deployment efficiency together. Task performance uses official VQAv2 accuracy and accuracy retention. Efficiency uses latency, peak GPU memory, and on-disk model size. The main timing protocol includes ten warm-up runs and three synchronized passes. The RTX 3090 provides controlled comparisons, while candidate configurations are checked on an 8 GB consumer GPU for deployment latency.”

**Clarify preliminary result:**

> “The current baseline latency of 0.333 seconds is preliminary because it used an earlier timing procedure. The baseline will be measured again with the full protocol.”

### Slide 14 — Data Analysis

**Say:**

> “First, I calculate accuracy, accuracy retention, latency, memory, and model size. Second, I use paired bootstrap confidence intervals with 10,000 resamples. Third, I apply the four deployability criteria. Finally, I use Pareto analysis. Accuracy is maximized, while latency, memory, and model size are minimized. No subjective weighting is used.”

**Explain Pareto simply:**

> “A configuration is Pareto-nondominated when no other configuration is at least as good on every objective and strictly better on one objective.”

### Slide 15 — Feasibility, Ethics and Risks

**Say:**

> “The baseline phase has been completed. The baseline accuracy is 79.45%, and the preliminary peak allocated memory is 8.74 GB. The estimated total experiment requires 20 to 40 GPU-hours. The main risks include tensor-shape problems after pruning, backend-dependent latency, and verbose answers after compression. These risks are addressed through staged validation, pinned software versions, repeated timing, and saved raw predictions. The study uses public benchmark data and does not collect new human data.”

### Slide 16 — Expected Results

**Say:**

> “The baseline already gives us an important reference. It achieves 79.45% accuracy, but it exceeds the 8 GB memory threshold and the 4 GB model-size threshold. The main experiments will determine which compression method gives the best balance, which component is most sensitive, whether combined compression is favorable, and which configurations satisfy all four criteria.”

**Avoid overclaiming:**

Use “will determine” or “is expected to show,” not “will prove.”

### Slide 17 — Limitations

**Say:**

> “The findings will be limited to one BLIP-3 checkpoint, one VQAv2 dataset, the selected compression procedures, and the tested hardware environments. There is no recovery fine-tuning, and deployment latency is verified on one 8 GB GPU. Therefore, the results will describe the defined experimental scenario rather than every possible device or VLM.”

**Smart framing:**

> “These limits reduce generalization, but they improve experimental control and reproducibility.”

### Slide 18 — Contributions and Conclusion

**Say:**

> “In conclusion, this study starts from a validated baseline that is accurate but exceeds the defined memory and model-size limits. It will evaluate whether structured pruning, INT8 quantization, or their combination can reduce this deployment gap while retaining at least 90% accuracy. The final contribution will be an evidence-based recommendation for choosing compressed BLIP-3 configurations under the defined RCVQA constraints. Thank you. I welcome your questions.”

## Presentation techniques that make the talk sound confident

### Use three repeated phrases

These phrases keep the story consistent:

- “under the defined RCVQA scenario”
- “measured empirically”
- “accuracy and efficiency must be considered together”

### Use careful language for unfinished results

Use:

- “The preliminary baseline shows…”
- “The main experiment will evaluate…”
- “The study is designed to determine…”
- “This is an expected outcome, not a final result.”

Avoid:

- “The combined method is definitely the best.”
- “INT8 will definitely make the model faster.”
- “The results generalize to all consumer GPUs.”

### If you forget something during presentation

Use this recovery sentence:

> “The key point here is that the experiment keeps the comparison controlled, so any difference can be interpreted as an effect of the compression configuration.”

## Likely examiner questions and short answers

### Why BLIP-3?

> “BLIP-3 is suitable because it has three identifiable components with different roles and sizes. This allows both full-model compression and component-level sensitivity analysis.”

### Why not fine-tune after pruning?

> “The study focuses on post-training compression and wants to measure the direct effect of compression. Recovery fine-tuning is important, but it is outside the current scope and is discussed as future work.”

### Why use VQAv2 only?

> “VQAv2 has a stable official evaluation protocol and ten human answers per question. This supports controlled comparison of small accuracy changes. Generalization to other tasks is a limitation.”

### Why use 8 GB as the deployment threshold?

> “The 8 GB limit represents the consumer-grade scenario defined by this study. It is an operational threshold for reproducible evaluation, not a universal requirement for all devices.”

### Why measure on an RTX 3090 first?

> “The uncompressed baseline requires more than 8 GB, so the RTX 3090 is used as the controlled measurement platform. Candidate configurations are then checked on an 8 GB GPU for deployment latency.”

### Why might INT8 increase latency?

> “Weight-only quantization may add dequantization overhead, and the result depends on the backend and available kernels. Therefore, the study measures latency instead of assuming a speed-up.”

### What if no configuration is deployable?

> “That is still a useful result. The study will report the remaining shortfall and identify the most limiting criterion. It may also show that post-training compression alone is not enough and that recovery fine-tuning is needed.”

### What is the main novelty?

> “The novelty is the controlled integration of component-level pruning, full-model pruning, INT8 quantization, combined compression, explicit deployment thresholds, and Pareto analysis for BLIP-3.”

## Final rehearsal checklist

- Explain the deployment problem in the first two minutes.
- Do not read the literature table row by row.
- Explain why each control variable is fixed.
- Distinguish preliminary baseline results from future compression results.
- Repeat that latency is measured, not assumed.
- Repeat that deployability requires all four criteria.
- Mention the main limitation before the examiner asks.
- End with the decision the study will produce: which configuration is recommended under the defined constraints.
