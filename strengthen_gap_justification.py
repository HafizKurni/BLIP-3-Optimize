from pathlib import Path
from docx import Document

path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))

def set_text(p, text):
    for child in list(p._p):
        if child.tag.endswith('}pPr'):
            continue
        p._p.remove(child)
    p.add_run(text)

replacements = {
    'Table 2.2 compares the studies most closely related to this research. The comparison focuses on the model context, compression method, task, reported metrics, and the limitation of each study relative to the aims of this thesis.':
        'Table 2.2 compares the studies most closely related to this research. The table is used as an evidence map for the research gap: it records the model context, compression method, task, metrics, and the specific condition that prevents each study from answering the present BLIP-3 comparison problem.',
    '\tThe comparison shows that the individual techniques used in this study are well established. Quantized VQA deployment, visual-token pruning, joint quantization and pruning, and mechanistic analysis of compression have all been studied. What is missing is their integration for BLIP-3 within one controlled environment that also examines each architectural component and applies explicit deployment thresholds.':
        '\tThe comparison shows that the individual techniques are established, but they address different parts of the problem. The original xGen-MM/BLIP-3 study evaluates multimodal capability and post-training safety interventions rather than pruning and quantization. Mishra et al. (2024) study quantization for VQA deployment on an embedded device, but not BLIP-3 or structural pruning. X. Li et al. (2026) compare joint quantization with visual-token pruning on other VLMs, whereas Elluru et al. (2026) examine internal effects rather than deployment feasibility. Thus, no identified study in this comparison combines BLIP-3, the three compression conditions, identical evaluation controls, component-level analysis, and explicit deployment thresholds.',
    '(a)\tFew studies compare pruning-only, quantization-only, and combined compression of BLIP-3 under identical data, decoding, hardware, and measurement conditions, so their relative effects on this architecture cannot be attributed reliably.':
        '(a)\tIn the studies reviewed in Table 2.2, no identified work provides a BLIP-3-specific comparison of structured pruning-only, INT8 weight-only quantization-only, and combined compression under the same dataset, decoding protocol, hardware, and efficiency-measurement procedure. Because the reviewed studies use different models, compression targets, tasks, or execution settings, their results cannot isolate the effect of compression strategy as cleanly as a controlled within-study comparison (Xue et al., 2025; Mishra et al., 2024; X. Li et al., 2026).',
    '\tTherefore, this study addresses the gap by evaluating BLIP-3 compression under a controlled RCVQA framework that uses both task-performance and deployment-efficiency metrics, examines each architectural component separately, and applies explicit deployability criteria.':
        '\tTherefore, this study addresses the gap through a controlled RCVQA framework. It compares the uncompressed baseline, structured pruning-only, INT8 weight-only quantization-only, and combined compression using the same data, prompt, decoding, hardware, and measurement procedures. It then examines component-level sensitivity and applies explicit deployability criteria so that the relative effects can be interpreted within one coherent experimental design.',
}
for p in doc.paragraphs:
    if p.text in replacements:
        set_text(p, replacements[p.text])

# Add the BLIP-3 source study to the evidence table.
t = doc.tables[3]
if not any(row.cells and row.cells[0].text == 'Xue et al. (2025)' for row in t.rows):
    row = t.add_row()
    vals = [
        'Xue et al. (2025)',
        'BLIP-3 / xGen-MM',
        'DPO and safety fine-tuning; no pruning or quantization benchmark',
        'Multimodal benchmarks and safety evaluation',
        'VQA, hallucination, safety, helpfulness',
        'Establishes the BLIP-3 model context but does not compare compression strategies or deployment efficiency',
    ]
    for cell, val in zip(row.cells, vals):
        cell.text = val
    cant_split = row._tr.get_or_add_trPr()
    from docx.oxml import OxmlElement
    cant_split.append(OxmlElement('w:cantSplit'))
    # Put the row before the existing "This study" row.
    study_row = next(r for r in t.rows if r.cells[0].text == 'This study')
    study_row._tr.addprevious(row._tr)

xue_row = next((r for r in t.rows if r.cells[0].text == 'Xue et al. (2025)'), None)
if xue_row is not None:
    trpr = xue_row._tr.get_or_add_trPr()
    if trpr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cantSplit') is None:
        from docx.oxml import OxmlElement
        trpr.append(OxmlElement('w:cantSplit'))

doc.save(str(path))
print(path)
