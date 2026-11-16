from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

thesis = 'Master_PD_Hafiz_Revised_Updated.docx'
defense = 'Preliminary_Work_Proposal_Defense_Hafiz.docx'

d = Document(thesis)
paras = d.paragraphs
for i, p in enumerate(paras):
    if p.text.strip() == 'Preliminary Work':
        p._element.getparent().remove(p._element)
        if i < len(paras) - 1 and 'A feasibility pilot is planned' in paras[i+1].text:
            paras[i+1]._element.getparent().remove(paras[i+1]._element)
        break
d.save(thesis)

x = Document()
title = x.add_paragraph()
title.style = 'Title'
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.add_run('Preliminary Work for Proposal Defense')
p = x.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run('A Compression Benchmarking Framework for Evaluating Efficiency–Accuracy Trade-offs in BLIP-3 for Resource-Constrained Visual Question Answering')
x.add_paragraph()
h = x.add_paragraph('Purpose')
h.style = 'Heading 1'
x.add_paragraph('This document records the preliminary-work plan to be presented separately during the proposal defense. It is not presented as completed experimental evidence in the thesis proposal because the measurement environment and pilot execution are not yet available.')
h = x.add_paragraph('Planned Feasibility Pilot')
h.style = 'Heading 1'
x.add_paragraph('Before the full experiment, the uncompressed BLIP-3 baseline will be run on approximately 100 VQAv2 samples. The pilot will record accuracy, mean latency, and peak GPU memory using the same preprocessing, decoding, synchronization, and scoring procedures specified in the proposal.')
x.add_paragraph('A second pilot will apply 10% structured pruning to one eligible component and verify successful model construction and forward inference. This step is intended to de-risk the custom xGen-MM implementation, including fused QKV projections in Phi-3 and the Perceiver Resampler.')
h = x.add_paragraph('Reporting Status')
h.style = 'Heading 1'
x.add_paragraph('The pilot values will be filled in after the RTX 5090 measurement environment is available. Until then, no accuracy, latency, memory, or pruning-success figures should be reported as completed results.')
h = x.add_paragraph('Planned Evidence for Defense')
h.style = 'Heading 1'
for item in [
    'Baseline accuracy on approximately 100 VQAv2 samples.',
    'Baseline mean latency per image–question pair on the fixed measurement GPU.',
    'Baseline peak GPU memory.',
    'Successful forward pass after 10% structured pruning of one component.',
    'Brief notes on implementation issues and any required mitigation before the full experiment.',
]:
    x.add_paragraph(item, style='List Bullet')
x.save(defense)
print(thesis)
print(defense)

