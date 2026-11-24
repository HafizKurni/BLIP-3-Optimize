from pathlib import Path
from docx import Document

path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))

def set_text(p, text):
    for child in list(p._p):
        if not child.tag.endswith('}pPr'):
            p._p.remove(child)
    p.add_run(text)

for p in doc.paragraphs:
    if p.text.startswith('(a) RQ1:'):
        set_text(p, '(a) RQ1: How do structured pruning applied alone, INT8 weight-only quantization applied alone, and their combination affect BLIP-3 accuracy, peak GPU memory, inference latency, and model size compared with the uncompressed baseline? (Mishra et al., 2024; Li et al., 2023)')
    elif p.text.startswith('(a) RO1:'):
        set_text(p, '(a) RO1: To measure how structured pruning applied alone, INT8 weight-only quantization applied alone, and their combination change BLIP-3 accuracy, peak GPU memory, inference latency, and model size compared with the baseline (Cooper et al., 2021; Mishra et al., 2024).')

doc.save(str(path))
print(path)
