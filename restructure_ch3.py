from copy import deepcopy
from pathlib import Path
import re
from docx import Document
from docx.oxml import OxmlElement

path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def set_text(p, text):
    for child in list(p._p):
        if child.tag != W + 'pPr':
            p._p.remove(child)
    p.add_run(text)

def disable_numbering(p):
    ppr = p._p.get_or_add_pPr()
    old = ppr.find(W + 'numPr')
    if old is not None:
        ppr.remove(old)
    numpr = OxmlElement('w:numPr')
    ilvl = OxmlElement('w:ilvl'); ilvl.set(W + 'val', '0')
    numid = OxmlElement('w:numId'); numid.set(W + 'val', '0')
    numpr.append(ilvl); numpr.append(numid); ppr.append(numpr)

# The pilot/preliminary block belongs before the final Chapter 3 summary.
# Its section number is therefore 3.16, and the final chapter summary becomes 3.17.
for p in doc.paragraphs:
    text = p.text
    text = re.sub(r'Section 3\.17(\.\d+(?:\.\d+)?)?', lambda m: 'Section 3.16' + (m.group(1) or ''), text)
    text = text.replace('Section 3.13.2', 'Section 3.13.1')
    if text != p.text:
        set_text(p, text)

pilot_heading_map = {
    '3.17.1 Experimental Result Validation': '3.16.1 Experimental Result Validation',
    '3.17.1.1 Dataset and Evaluation Coverage': '3.16.1.1 Dataset and Evaluation Coverage',
    '3.17.1.2 Reproducibility and Execution Environment': '3.16.1.2 Reproducibility and Execution Environment',
    '3.17.2 Preliminary Pipeline and Structural Results': '3.16.2 Preliminary Pipeline and Structural Results',
    '3.17.2.1 Pilot Pipeline Validation': '3.16.2.1 Pilot Pipeline Validation',
    '3.17.2.2 BLIP-3 Structural Probe': '3.16.2.2 BLIP-3 Structural Probe',
    '3.17.3 Baseline BLIP-3 Results': '3.16.3 Baseline BLIP-3 Results',
    '3.17.3.1 Baseline Accuracy': '3.16.3.1 Baseline Accuracy',
    '3.17.3.2 Baseline Response Behaviour': '3.16.3.2 Baseline Response Behaviour',
    '3.17.3.3 Baseline Efficiency': '3.16.3.3 Baseline Efficiency',
    '3.17.3.4 Baseline Comparison with Deployability Criteria': '3.16.3.4 Baseline Comparison with Deployability Criteria',
    '3.17.4 Implications for the Main Experiments': '3.16.4 Implications for the Main Experiments',
    '3.17.5 Chapter Summary': '3.16.5 Pilot Study Summary',
}
for p in doc.paragraphs:
    if p.text in pilot_heading_map:
        disable_numbering(p)
        set_text(p, pilot_heading_map[p.text])

# Make the final Chapter 3 summary explicit and place it after the pilot block.
summaries = [p for p in doc.paragraphs if p.text.strip() == 'Chapter Summary']
if summaries:
    final_summary = summaries[-1]
    disable_numbering(final_summary)
    set_text(final_summary, '3.17 Chapter Summary')

# Rewrite the visible TOC in logical order. The existing 3.16 and 3.17 entries
# are reused so the contents list retains its original formatting.
paras = doc.paragraphs
for p in paras:
    if p.text == '3.16\tChapter Summary\t47':
        set_text(p, '3.16\tPILOT STUDY AND PRELIMINARY RESULTS\t48')
    elif p.text == '3.17\tPILOT STUDY AND PRELIMINARY RESULTS\t48':
        set_text(p, '')
    elif p.text.startswith('3.17.1\tExperimental Result Validation'):
        set_text(p, p.text.replace('3.17.1', '3.16.1'))
    elif p.text.startswith('3.17.1.1\tDataset'):
        set_text(p, p.text.replace('3.17.1.1', '3.16.1.1'))
    elif p.text.startswith('3.17.1.2\tReproducibility'):
        set_text(p, p.text.replace('3.17.1.2', '3.16.1.2'))
    elif p.text.startswith('3.17.2\tPreliminary Pipeline'):
        set_text(p, p.text.replace('3.17.2', '3.16.2'))
    elif p.text.startswith('3.17.2.1\tPilot'):
        set_text(p, p.text.replace('3.17.2.1', '3.16.2.1'))
    elif p.text.startswith('3.17.2.2\tBLIP'):
        set_text(p, p.text.replace('3.17.2.2', '3.16.2.2'))
    elif p.text.startswith('3.17.3\tBaseline'):
        set_text(p, p.text.replace('3.17.3', '3.16.3'))
    elif p.text.startswith('3.17.3.1\tBaseline'):
        set_text(p, p.text.replace('3.17.3.1', '3.16.3.1'))
    elif p.text.startswith('3.17.3.2\tBaseline'):
        set_text(p, p.text.replace('3.17.3.2', '3.16.3.2'))
    elif p.text.startswith('3.17.3.3\tBaseline'):
        set_text(p, p.text.replace('3.17.3.3', '3.16.3.3'))
    elif p.text.startswith('3.17.3.4\tBaseline'):
        set_text(p, p.text.replace('3.17.3.4', '3.16.3.4'))
    elif p.text.startswith('3.17.4\tImplications'):
        set_text(p, p.text.replace('3.17.4', '3.16.4'))
    elif p.text.startswith('3.17.5\tPilot Study Summary'):
        set_text(p, p.text.replace('3.17.5', '3.16.5'))

# The old Chapter Summary entry was replaced by the pilot entry above. Add the
# new final Chapter Summary entry immediately before References.
ref = next((p for p in doc.paragraphs if p.text.strip() == 'References'), None)
if ref is not None and not any(p.text == '3.17\tChapter Summary\t55' for p in doc.paragraphs):
    new = doc.add_paragraph('3.17\tChapter Summary\t55', style='toc 2')
    ref._p.addprevious(new._p)

doc.save(str(path))
print(path)
