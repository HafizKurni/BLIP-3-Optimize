from pathlib import Path
from docx import Document

path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))

def set_text(p, text, lead=None):
    for child in list(p._p):
        if not child.tag.endswith('}pPr'):
            p._p.remove(child)
    if lead and text.startswith(lead):
        r = p.add_run(lead)
        r.bold = True
        p.add_run(text[len(lead):])
    else:
        p.add_run(text)

# Convert the former fourth-level headings into concise bold lead-ins.
lead_ins = {
    'Dataset and Evaluation Coverage': 'Dataset and evaluation coverage. ',
    'Reproducibility and Execution Environment': 'Reproducibility and execution environment. ',
    'Pilot Pipeline Validation': 'Pilot pipeline validation. ',
    'BLIP-3 Structural Probe': 'BLIP-3 structural probe. ',
    'Baseline Accuracy': 'Baseline accuracy. ',
    'Baseline Response Behaviour': 'Baseline response behaviour. ',
    'Baseline Efficiency': 'Baseline efficiency. ',
    'Baseline Comparison with Deployability Criteria': 'Baseline comparison with deployability criteria. ',
}

paras = doc.paragraphs
for i, p in enumerate(list(paras)):
    heading = next((h for h in lead_ins if p.text.endswith(h) and p.text.startswith('3.16.')), None)
    if heading:
        # The next non-empty body paragraph carries the explanation for this heading.
        next_p = None
        current_index = paras.index(p)
        for candidate in paras[current_index + 1:]:
            if candidate.text.strip():
                next_p = candidate
                break
        if next_p is not None and next_p.style.name in {'INTI-C', 'Normal'}:
            set_text(next_p, lead_ins[heading] + next_p.text, lead_ins[heading])
        p._element.getparent().remove(p._element)

# Remove the corresponding fourth-level entries from the visible TOC.
toc_prefixes = (
    '3.16.1.1\t', '3.16.1.2\t', '3.16.2.1\t', '3.16.2.2\t',
    '3.16.3.1\t', '3.16.3.2\t', '3.16.3.3\t', '3.16.3.4\t',
)
for p in list(doc.paragraphs):
    if p.style.name.startswith('toc') and p.text.startswith(toc_prefixes):
        p._element.getparent().remove(p._element)

doc.save(str(path))
print(path)
