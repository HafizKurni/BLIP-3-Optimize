from copy import deepcopy
from pathlib import Path
import re
from docx import Document

path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))

def set_text(p, text):
    for child in list(p._p):
        if child.tag.endswith('}pPr'):
            continue
        p._p.remove(child)
    p.add_run(text)

# Make the Research Problem mirror the three connected RQ/RO stages.
rp = {
    'Nevertheless, the reviewed literature shows four limitations when this evidence is applied to BLIP-3 in a resource-constrained setting:':
        'Nevertheless, the reviewed literature shows three connected limitations when this evidence is applied to BLIP-3 in a resource-constrained setting:',
    '(i)\tPruning and quantization are usually studied separately or on other model families, rather than being compared for BLIP-3 under one controlled experimental environment.':
        '(i)\tThe overall effects of pruning, quantization, and combined compression have not been compared for BLIP-3 under one controlled experimental environment, leaving the efficiency–accuracy effects of each strategy difficult to interpret (Mishra et al., 2024; Li et al., 2023).',
    '(ii)\tExisting work rarely focuses on BLIP-3 itself, so its efficiency–accuracy behaviour under explicit consumer-grade limits remains insufficiently characterized.':
        '(ii)\tBecause BLIP-3 is modular, its components may contribute differently to computational cost and may tolerate structural pruning differently; however, component-level evidence for the visual encoder, multimodal connector, and language model remains limited (Michel et al., 2019; Ma et al., 2023).',
    '(iii)\tComponent-level evidence is lacking; it is not known whether the visual encoder, multimodal connector, and language model of BLIP-3 respond differently to the same level of structural pruning.': '',
    '(iv)\tAccuracy and deployment feasibility are seldom assessed together using explicit thresholds for GPU memory, inference latency, model size, and accuracy retention.':
        '(iii)\tThe resulting configurations are rarely assessed through one integrated decision that combines accuracy, memory, latency, model size, and explicit deployability thresholds; therefore, the most favorable trade-off and the main deployment bottleneck remain uncertain (Cooper et al., 2021; Mishra et al., 2024).',
    '\tThe research problem is therefore an integration and deployment-evaluation gap rather than an absence of compression research. Specifically, limited research has systematically evaluated pruning-only, quantization-only, and combined compression strategies for BLIP-3 under the same resource-constrained VQA environment, examined component-level compression sensitivity within BLIP-3, and determined whether the resulting configurations satisfy predefined deployment criteria. This study addresses the problem through a controlled quantitative evaluation of baseline and compressed BLIP-3 configurations.':
        '\tThese limitations are sequentially related. First, the overall effect of each compression strategy must be measured against the uncompressed baseline. Second, the internal components must be examined to explain where computational cost and compression sensitivity arise. Third, the component-level and full-model results must be integrated into an efficiency–accuracy and deployability decision. The research problem is therefore an integration and deployment-evaluation gap rather than an absence of compression research. This study addresses the gap through a controlled quantitative evaluation of baseline and compressed BLIP-3 configurations under the same resource-constrained VQA environment.'
}
for p in doc.paragraphs:
    if p.text in rp:
        set_text(p, rp[p.text])
    elif p.text.strip().startswith('Previous studies have examined important parts of this problem'):
        set_text(p, p.text.replace('four limitations', 'three connected limitations'))

# Correct the remaining cross-reference in the experimental schedule table.
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            if 'Section 3.17' in cell.text:
                cell.text = cell.text.replace('Section 3.17', 'Section 3.16')

# Repair the visible contents list order and page numbers.
toc_values = {
    '3.16\tPILOT STUDY AND PRELIMINARY RESULTS\t48': '3.16\tPILOT STUDY AND PRELIMINARY RESULTS\t47',
    '3.16.1\tExperimental Result Validation\t48': '3.16.1\tExperimental Result Validation\t47',
    '3.16.1.1\tDataset and Evaluation Coverage\t48': '3.16.1.1\tDataset and Evaluation Coverage\t47',
    '3.16.1.2\tReproducibility and Execution Environment\t49': '3.16.1.2\tReproducibility and Execution Environment\t48',
    '3.16.2\tPreliminary Pipeline and Structural Results\t49': '3.16.2\tPreliminary Pipeline and Structural Results\t48',
    '3.16.2.1\tPilot Pipeline Validation\t50': '3.16.2.1\tPilot Pipeline Validation\t49',
    '3.16.2.2\tBLIP-3 Structural Probe\t50': '3.16.2.2\tBLIP-3 Structural Probe\t49',
    '3.16.3\tBaseline BLIP-3 Results\t51': '3.16.3\tBaseline BLIP-3 Results\t50',
    '3.16.3.1\tBaseline Accuracy\t51': '3.16.3.1\tBaseline Accuracy\t50',
    '3.16.3.2\tBaseline Response Behaviour\t53': '3.16.3.2\tBaseline Response Behaviour\t52',
    '3.16.3.3\tBaseline Efficiency\t53': '3.16.3.3\tBaseline Efficiency\t52',
    '3.16.3.4\tBaseline Comparison with Deployability Criteria\t54': '3.16.3.4\tBaseline Comparison with Deployability Criteria\t53',
    '3.16.4\tImplications for the Main Experiments\t55': '3.16.4\tImplications for the Main Experiments\t54',
    '3.16.5\tPilot Study Summary\t56': '3.16.5\tPilot Study Summary\t55',
}
for p in doc.paragraphs:
    if p.text in toc_values:
        set_text(p, toc_values[p.text])

for p in list(doc.paragraphs):
    if p.style.name.startswith('toc') and p.text == '':
        p._element.getparent().remove(p._element)
    elif p.text.startswith('3.16\tPILOT STUDY AND PRELIMINARY RESULTS'):
        p.style = doc.styles['toc 1']

# Move the inserted final-summary TOC line before the References TOC line.
summary_toc = next((p for p in doc.paragraphs if p.text == '3.17\tChapter Summary\t55'), None)
refs_toc = next((p for p in doc.paragraphs if p.style.name.startswith('toc') and p.text.startswith('References')), None)
if summary_toc is not None and refs_toc is not None:
    refs_toc._p.addprevious(summary_toc._p)

doc.save(str(path))
print(path)
