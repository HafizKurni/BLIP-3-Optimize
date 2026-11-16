from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from docx.shared import Inches

src = '/Users/hafiz/Desktop/INTI Master Kuliah/Supervisor/Thesis Bimbingan/Preliminary_Work_Proposal_Defense_Hafiz.docx'
out = '/Users/hafiz/Documents/ChatGPT/Thesis Master Data Science (RCVAQ)/Preliminary_Work_Proposal_Defense_Hafiz_Baseline_Updated.docx'
d = Document(src)

def find(text):
    for p in d.paragraphs:
        if p.text.strip() == text:
            return p
    raise ValueError(text)

def after(p, text, style='Normal'):
    el = OxmlElement('w:p')
    p._p.addnext(el)
    q = Paragraph(el, p._parent)
    q.style = style
    q.add_run(text)
    return q

p = find('This document records the preliminary-work plan to be presented separately during the proposal defense. It is not presented as completed experimental evidence in the thesis proposal because the measurement environment and pilot execution are not yet available.')
p.text = 'This document records the preliminary work completed for the proposal defense. The baseline pilot has been executed on 100 VQAv2 samples. Structured pruning and quantization have not yet been completed because the current pruning implementation produced errors; they remain planned technical work rather than completed evidence.'

p = find('Planned Feasibility Pilot')
p.text = 'Completed Baseline Pilot'
p.style = 'Heading 1'
p2 = find('Before the full experiment, the uncompressed BLIP-3 baseline will be run on approximately 100 VQAv2 samples. The pilot will record accuracy, mean latency, and peak GPU memory using the same preprocessing, decoding, synchronization, and scoring procedures specified in the proposal.')
p2.text = 'The uncompressed BLIP-3 baseline was executed on 100 VQAv2 samples using the Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5 checkpoint. The pilot used seed 42 and recorded accuracy, latency, and peak GPU memory. The prediction file contains 100 image–question records with the generated answer and per-sample latency.'

# remove old pruning paragraph and replace with status
old = find('A second pilot will apply 10% structured pruning to one eligible component and verify successful model construction and forward inference. This step is intended to de-risk the custom xGen-MM implementation, including fused QKV projections in Phi-3 and the Perceiver Resampler.')
old.text = 'Structured pruning was attempted but did not complete successfully. No pruning accuracy, latency, memory, or forward-pass result is reported. The pruning implementation will be investigated separately, including the handling of fused QKV projections in Phi-3 and the Perceiver Resampler. Quantization has also not yet been evaluated.'

p = find('Reporting Status')
status = find('The pilot values will be filled in after the RTX 5090 measurement environment is available. Until then, no accuracy, latency, memory, or pruning-success figures should be reported as completed results.')
status.text = 'The baseline pilot is completed. The results below are preliminary evidence for feasibility and are not yet the final thesis benchmark. The current pilot accuracy should be rechecked against the official VQAv2 evaluation implementation before being used for formal claims.'

# add results table after status
table = d.add_table(rows=1, cols=3)
table.style = 'Table Grid'
hdr = table.rows[0].cells
hdr[0].text = 'Metric'
hdr[1].text = 'Baseline pilot'
hdr[2].text = 'Interpretation'
rows = [
('Samples', '100', 'Pilot subset; seed 42'),
('Accuracy', '0.3267 (32.67%)', 'Preliminary pilot score; verify official VQAv2 scoring'),
('Mean latency', '0.1522 s', 'Per image–question pair'),
('Latency SD', '0.0760 s', 'Across 100 samples'),
('Peak GPU memory', '8.7244 GB', 'Allocated GPU memory during pilot'),
('Model', 'Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5', 'Uncompressed BF16 baseline'),
]
for a,b,c in rows:
    cells = table.add_row().cells
    cells[0].text, cells[1].text, cells[2].text = a,b,c

p = find('Planned Evidence for Defense')
p.text = 'Evidence Available for Defense'
p.style = 'Heading 1'
# replace bullets by adding note paragraphs; keep existing bullets but update texts
for para in d.paragraphs:
    if para.text.strip() == 'Baseline accuracy on approximately 100 VQAv2 samples.':
        para.text = 'Baseline accuracy on 100 VQAv2 samples: 0.3267 (32.67%).'
    elif para.text.strip() == 'Baseline mean latency per image–question pair on the fixed measurement GPU.':
        para.text = 'Baseline mean latency: 0.1522 seconds per image–question pair.'
    elif para.text.strip() == 'Baseline peak GPU memory.':
        para.text = 'Baseline peak GPU memory: 8.7244 GB.'
    elif para.text.strip() == 'Successful forward pass after 10% structured pruning of one component.':
        para.text = 'Pruning evidence: not available because the pruning implementation currently produces errors.'
    elif para.text.strip() == 'Brief notes on implementation issues and any required mitigation before the full experiment.':
        para.text = 'Implementation status: pruning and quantization require further debugging and validation.'

# add reproducibility evidence
after(d.paragraphs[-1], 'The supporting evidence is stored in the baseline_results_only folder: the executed pilot notebook, prediction JSON file, metrics JSON file, and baseline source scripts. These files should be retained as supplementary evidence for the defense.', 'Normal')

d.save(out)
print(out)

