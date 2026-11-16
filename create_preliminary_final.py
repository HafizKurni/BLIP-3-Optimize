from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

out = '/Users/hafiz/Documents/ChatGPT/Thesis Master Data Science (RCVAQ)/Preliminary_Work_Proposal_Defense_Hafiz_Final.docx'
d = Document()
sec = d.sections[0]
sec.top_margin = Inches(0.8)
sec.bottom_margin = Inches(0.8)
sec.left_margin = Inches(0.9)
sec.right_margin = Inches(0.9)

title = d.add_paragraph(style='Title')
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.add_run('Preliminary Work for Proposal Defense')
sub = d.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.add_run('A Compression Benchmarking Framework for Evaluating Efficiency–Accuracy Trade-offs in BLIP-3 for Resource-Constrained Visual Question Answering')

d.add_heading('3.13.1 Preliminary Work', level=1)
d.add_paragraph('A baseline pilot was conducted to verify that the experimental pipeline can be executed with the available resources and to identify practical issues before the main experiments. The uncompressed BLIP-3 checkpoint (Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5) was run in BF16 precision on 100 VQAv2 validation questions drawn by proportional stratified sampling with seed 42, comprising 49 other, 38 yes/no, and 13 number questions. The pilot used a rented cloud instance with a single NVIDIA RTX 5090 GPU (32 GB), an Intel Xeon w7-3455 CPU, and a PyTorch environment with CUDA 12.8, at a rental cost of approximately US$0.52 per hour. The predictions were rescored with an implementation of the official VQAv2 protocol. Table 3.9 summarizes the results.')
d.add_heading('Table 3.9 Results of the Baseline Pilot', level=2)
t = d.add_table(rows=1, cols=3); t.style='Table Grid'
for c,v in zip(t.rows[0].cells,['Metric','Result','Remark']): c.text=v
rows=[
('Questions','100 (49 other, 38 yes/no, 13 number)','Proportional stratified sample, seed 42'),
('Pipeline execution','Completed without error','Image preprocessing, answer generation, and prediction/latency logging'),
('VQA accuracy','34.40% (other 20.20%, yes/no 48.68%, number 46.15%)','Official VQAv2 protocol; affected by answer format'),
('Mean inference latency','0.147 s (SD 0.052 s)','99 questions; first cold-start inference excluded; generation time only'),
('Peak GPU memory','8.72 GB','Peak allocated memory; 1 GB = 1024³ bytes'),
('Model weights (BF16)','Approximately 8–8.7 GB (estimated)','Bounded above by peak allocated memory; direct file-size measurement remains pending'),
]
for row in rows:
 cells=t.add_row().cells
 for c,v in zip(cells,row): c.text=v

d.add_heading('Table 3.10 Pilot Accuracy and Latency by Response Length', level=2)
t = d.add_table(rows=1, cols=4); t.style='Table Grid'
for c,v in zip(t.rows[0].cells,['Response length','Responses','VQA accuracy','Mean latency']): c.text=v
for row in [('Three words or fewer','42','81.9%','0.089 s'),('More than three words','58','0.0%','0.198 s')]:
 cells=t.add_row().cells
 for c,v in zip(cells,row): c.text=v

d.add_paragraph('The pilot yields five observations that inform the design of the main experiments.')
obs=[
('First, the complete inference pipeline executes successfully on the rented hardware, and the checkpoint can be loaded, run, and logged in BF16 precision without modification.'),
('Second, answer format has a decisive effect on VQAv2 scores. The pilot prompt followed the model card, which asks the model for detailed answers and does not include a short-answer instruction. As a result, 58 of the 100 responses were full sentences, many truncated at the 10-token generation limit. All 58 received a score of zero, including responses whose content was correct. The 42 short responses achieved 81.9% accuracy, but this subset is not a random sample and is not an estimate of baseline accuracy. The main experiments will therefore use the fixed short-answer instruction specified in the proposal, and the baseline pilot will be repeated with that prompt before the main experiments.'),
('Third, the baseline peak GPU memory of 8.72 GB exceeds the 8 GB criterion by approximately 9%. The 4 GB model-size criterion requires the stored weights to be reduced by roughly half. Because INT8 weight-only quantization may leave embeddings, the output head, and normalization layers in BF16, quantization alone may not reach 4 GB. The model-size criterion may therefore be more restrictive than the memory criterion.'),
('Fourth, the mean latency on the measurement GPU is far below the 2.0 s criterion, confirming that latency measured on a high-end GPU does not represent consumer-grade hardware. Configurations that satisfy the memory, model-size, and accuracy-retention criteria will therefore require additional benchmarking on an 8 GB consumer GPU before consumer-device latency is judged. Latency will be measured with the final prompt and after warm-up runs.'),
('Fifth, a first attempt at structured pruning did not complete because the fused query–key–value projection of the Phi-3 language model and the attention layers of the Perceiver Resampler require coordinated slicing of coupled weights. This confirms the implementation risk identified in the proposal. Pruning will be implemented in stages, beginning with feed-forward channels in the language model, followed by the visual encoder and connector, and finally attention heads. If attention-head pruning cannot be validated by Week 6, the eligible units will be restricted to feed-forward channels and the deviation will be reported. INT8 weight-only quantization will be tested on the pilot questions before the full experiments begin.')
]
for x in obs: d.add_paragraph(x)

d.add_heading('Computational Budget Implication', level=2)
d.add_paragraph('At the observed latency, the 98,250 inferences required for accuracy evaluation and efficiency benchmarking correspond to approximately 4 GPU-hours on the measurement GPU. Including implementation, validation, and repeated runs, the total requirement is estimated at 20–40 GPU-hours, or approximately US$10–US$21 at the observed rental rate.')

d.add_heading('Evidence and Reporting Boundary', level=2)
d.add_paragraph('The supporting evidence consists of the 100-sample prediction file, the rescored metrics file, pilot_questions.json, the executed visualization notebook, and the baseline source scripts. The reported 34.40% is a rescored pilot result, not the final baseline result for the thesis, because the original pilot used a detailed-answer prompt. The short-answer baseline must be rerun before formal accuracy-retention claims are made. No pruning or quantization result is reported as completed.')
d.save(out)
print(out)

