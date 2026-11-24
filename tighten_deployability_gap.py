from pathlib import Path
from docx import Document

path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))

old = '(c)\tFew studies assess deployability using accuracy, latency, memory, and model size simultaneously against explicit thresholds; most report accuracy retention or efficiency gains separately.'
new = '(c)\tIn the studies reviewed, no identified work evaluates deployability as a joint decision across VQA accuracy, inference latency, peak GPU memory, and model size using predefined thresholds. Related studies typically report accuracy retention or one or two efficiency measures, rather than applying all four criteria simultaneously.'

for p in doc.paragraphs:
    if p.text == old:
        for child in list(p._p):
            if not child.tag.endswith('}pPr'):
                p._p.remove(child)
        p.add_run(new)
        break

doc.save(str(path))
print(path)
