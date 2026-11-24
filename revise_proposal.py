from copy import deepcopy
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

SRC = Path('/Users/hafiz/Desktop/INTI Master Kuliah/Supervisor/Persiapan PD dan VIVA/PD Material/[FINAL] Master PD Hafiz.docx')
OUT = Path('/Users/hafiz/Documents/ChatGPT/Thesis Master Data Science (RCVAQ)/[REVISED] Master PD Hafiz Proposal.docx')

doc = Document(str(SRC))

def set_text(p, text):
    # Keep paragraph-level formatting and replace runs cleanly.
    for child in list(p._p):
        if child.tag.endswith('}pPr'):
            continue
        p._p.remove(child)
    p.add_run(text)

def add_table_row(table, values):
    row = table.add_row()
    for c, v in zip(row.cells, values):
        c.text = v
    return row

def disable_auto_numbering(p):
    ppr = p._p.get_or_add_pPr()
    old = ppr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
    if old is not None:
        ppr.remove(old)
    numpr = OxmlElement('w:numPr')
    ilvl = OxmlElement('w:ilvl'); ilvl.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '0')
    numid = OxmlElement('w:numId'); numid.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '0')
    numpr.append(ilvl); numpr.append(numid); ppr.append(numpr)

# Consolidate the research questions and objectives to three aligned pairs.
set_text(doc.paragraphs[207], 'The study is guided by the following three research questions. Each question is grounded in the need to evaluate compression as a measurable deployment problem rather than as a size-reduction exercise alone (Cooper et al., 2021; Li et al., 2023; Mishra et al., 2024).')
set_text(doc.paragraphs[208], '(a) RQ1: To what extent do structured pruning, INT8 weight-only post-training quantization, and their combination change the peak GPU memory, inference latency, model size, and VQA accuracy of BLIP-3 relative to the uncompressed baseline?')
set_text(doc.paragraphs[209], '(b) RQ2: How do the visual encoder, multimodal connector, and language model of BLIP-3 differ in their contribution to computational cost and in their sensitivity to structured pruning? This question is motivated by evidence that transformer components are not equally important and that pruning sensitivity can vary across components (Michel et al., 2019; Ma et al., 2023).')
set_text(doc.paragraphs[210], '(c) RQ3: Which compressed BLIP-3 configurations provide the most favorable efficiency–accuracy trade-off and satisfy the predefined RCVQA deployability criteria? A joint decision is necessary because lower resource use does not by itself establish practical deployability (Cooper et al., 2021; Mishra et al., 2024).')
set_text(doc.paragraphs[211], '')
set_text(doc.paragraphs[212], 'The questions follow a sequential logic. RQ1 establishes the overall effects of the compression strategies. RQ2 identifies where computational cost and compression sensitivity are located within BLIP-3. RQ3 integrates these findings through multi-metric trade-off analysis and explicit deployment thresholds.')
set_text(doc.paragraphs[214], 'The main objective of this study is to evaluate whether post-training compression can make BLIP-3 feasible for resource-constrained VQA deployment while preserving an acceptable level of accuracy. The three specific objectives correspond directly to the research questions and are supported by the need for controlled, reproducible efficiency evaluation (Reddi et al., 2020; Li et al., 2023).')
set_text(doc.paragraphs[215], '(a) RO1: To measure the changes in peak GPU memory, inference latency, model size, and VQA accuracy produced by structured pruning, INT8 weight-only post-training quantization, and their combination, relative to the uncompressed baseline. These numerical measurements are required to make the efficiency–accuracy trade-off explicit (Cooper et al., 2021; Mishra et al., 2024).')
set_text(doc.paragraphs[216], '(b) RO2: To compare the computational contribution and pruning sensitivity of the visual encoder, multimodal connector, and language model of BLIP-3, using component-level profiling and parameter-normalized sensitivity analysis (Michel et al., 2019; Ma et al., 2023).')
set_text(doc.paragraphs[217], '(c) RO3: To identify the compressed configurations with the most favorable efficiency–accuracy profiles, determine which configurations satisfy the RCVQA deployability criteria, and identify the criterion that most limits deployment (Cooper et al., 2021; Miettinen, 1999).')
set_text(doc.paragraphs[218], '')
set_text(doc.paragraphs[219], 'Table 1.1 summarizes the alignment among the three research questions, objectives, hypotheses, and analyses.')

# Replace the alignment table with three rows.
t = doc.tables[0]
while len(t.rows) > 1:
    t._tbl.remove(t.rows[-1]._tr)
add_table_row(t, ['RQ1: Overall effects of pruning, quantization, and combined compression', 'RO1: Measure changes in efficiency and accuracy', 'H1', 'Compare BASE, full-model pruning, INT8 quantization, and combined compression using relative reductions and accuracy retention'])
add_table_row(t, ['RQ2: Differences among BLIP-3 components', 'RO2: Compare component contribution and pruning sensitivity', 'H2', 'Baseline component profiling and component-level pruning at 10%, 20%, and 30%, with absolute and parameter-normalized sensitivity'])
add_table_row(t, ['RQ3: Efficiency–accuracy trade-off and deployability', 'RO3: Identify favorable and deployable configurations and the limiting criterion', 'H3 / Descriptive', 'Pareto-based comparison and joint evaluation against memory, latency, model-size, and accuracy-retention criteria'])

# Make the rationale for the quantitative design explicit.
set_text(doc.paragraphs[348], 'Research Design')
doc.paragraphs[349].text = doc.paragraphs[349].text  # preserve paragraph position
quant = ('This study uses a quantitative, controlled comparative experimental design because its central constructs are numerical and directly measurable: VQA accuracy, accuracy retention, peak GPU memory, inference latency, model size, parameter count, and relative reduction. A quantitative design permits the same inputs, preprocessing, decoding settings, hardware, and software to be held constant while the compression configuration is varied, allowing observed differences to be summarized with effect sizes, confidence intervals, and reproducible comparisons (Reddi et al., 2020; Cooper et al., 2021; Efron & Tibshirani, 1993). This approach is appropriate for model-compression benchmarking because deployment decisions depend on measured resource thresholds rather than on subjective judgments (Li et al., 2023; Mishra et al., 2024).')
set_text(doc.paragraphs[349], quant)

# Align the expected-outcomes narrative with the consolidated RQ3.
set_text(doc.paragraphs[502], '\tFor RQ3, the combined configuration will be compared with pruning-only and quantization-only compression through Pareto analysis and the four deployability criteria. The study will identify any configuration that satisfies all criteria and the criterion that most limits deployment; whether the combined configuration is more favourable will be determined empirically rather than assumed.')
set_text(doc.paragraphs[503], '')

# Move the existing Chapter 4 material into the end of Chapter 3 as Section 3.17.
body_children = list(doc.element.body.iterchildren())
p_by_el = {p._p: i for i, p in enumerate(doc.paragraphs)}
start_el = doc.paragraphs[507]._p
end_el = doc.paragraphs[571]._p  # References heading; do not move references.
start_idx = body_children.index(start_el)
end_idx = body_children.index(end_el)
pilot_nodes = body_children[start_idx:end_idx]
for node in pilot_nodes:
    doc.element.body.remove(node)
insert_before = doc.paragraphs[504]._p
for node in pilot_nodes:
    insert_before.addprevious(node)

# Rebuild paragraph/table wrappers after reordering is not necessary for text edits below;
# use direct XML text replacement for the moved content and captions.
all_paras = list(doc.paragraphs)
repls = {
    'PRELIMINARY RESULTS': 'PILOT STUDY AND PRELIMINARY RESULTS',
    'Chapter 4': 'Section 3.17',
    'chapter 4': 'Section 3.17',
    'Section 4.2': 'Section 3.17.1',
    'Section 4.3': 'Section 3.17.2',
    'Section 4.4': 'Section 3.17.3',
    'Section 4.5': 'Section 3.17.4',
    'Section 4.6': 'Section 3.17.5',
    'Table 4.1': 'Table 3.9',
    'Table 4.2': 'Table 3.10',
    'Table 4.3': 'Table 3.11',
    'Table 4.4': 'Table 3.12',
    'Table 4.5': 'Table 3.13',
    'Table 4.6': 'Table 3.14',
    'Table 4.7': 'Table 3.15',
    'Table 4.8': 'Table 3.16',
    'Table 4.9': 'Table 3.17',
    'Table 4.10': 'Table 3.18',
    'Figure 4.1': 'Figure 3.2',
}
for p in all_paras:
    if not p.text:
        continue
    new = p.text
    for old, val in repls.items():
        new = new.replace(old, val)
    if new != p.text:
        set_text(p, new)

# The old four-question wording may also occur in the hypotheses narrative.
for p in all_paras:
    if 'RQ4' in p.text:
        set_text(p, p.text.replace('RQ4', 'RQ3'))

# Improve the pilot section labels and clarify that this is an initial baseline phase.
for p in all_paras:
    if p.text == 'Introduction' and p.style.name == 'INIT-T2':
        # There are two such headings; only the moved one is now after the Chapter 3 content.
        if p._p.getparent().index(p._p) > 500:
            set_text(p, 'Pilot Study Introduction')

# Update visible TOC/list entries so the document no longer advertises a Chapter 4.
for p in all_paras:
    txt = p.text
    if txt.startswith('4.1\tIntroduction'):
        set_text(p, '3.17\tPilot Study and Preliminary Results\t48')
    elif txt.startswith('4.2\tExperimental Result Validation'):
        set_text(p, '3.17.1\tExperimental Result Validation\t48')
    elif txt.startswith('4.2.1'):
        set_text(p, '3.17.1.1\tDataset and Evaluation Coverage\t48')
    elif txt.startswith('4.2.2'):
        set_text(p, '3.17.1.2\tReproducibility and Execution Environment\t49')
    elif txt.startswith('4.3\tPreliminary Pipeline'):
        set_text(p, '3.17.2\tPreliminary Pipeline and Structural Results\t49')
    elif txt.startswith('4.3.1'):
        set_text(p, '3.17.2.1\tPilot Pipeline Validation\t50')
    elif txt.startswith('4.3.2'):
        set_text(p, '3.17.2.2\tBLIP-3 Structural Probe\t50')
    elif txt.startswith('4.4\tBaseline BLIP-3 Results'):
        set_text(p, '3.17.3\tBaseline BLIP-3 Results\t51')
    elif txt.startswith('4.4.1'):
        set_text(p, '3.17.3.1\tBaseline Accuracy\t51')
    elif txt.startswith('4.4.2'):
        set_text(p, '3.17.3.2\tBaseline Response Behaviour\t53')
    elif txt.startswith('4.4.3'):
        set_text(p, '3.17.3.3\tBaseline Efficiency\t53')
    elif txt.startswith('4.4.4'):
        set_text(p, '3.17.3.4\tBaseline Comparison with Deployability Criteria\t54')
    elif txt.startswith('4.5\tImplications'):
        set_text(p, '3.17.4\tImplications for the Main Experiments\t55')
    elif txt.startswith('4.6\tChapter Summary'):
        set_text(p, '3.17.5\tPilot Study Summary\t56')
    elif txt.startswith('PRELIMINARY RESULTS'):
        set_text(p, '3.17\tPILOT STUDY AND PRELIMINARY RESULTS\t48')
    elif txt.startswith('Figure 4.1'):
        set_text(p, txt.replace('Figure 4.1', 'Figure 3.2'))

# Repair any TOC paragraphs that contain legacy and replacement text together.
toc_exact = {
    'PRELIMINARY RESULTS\t48PILOT STUDY AND PRELIMINARY RESULTS\t483.17\tPILOT STUDY AND PILOT STUDY AND PRELIMINARY RESULTS\t48': '3.17\tPILOT STUDY AND PRELIMINARY RESULTS\t48',
}
for p in all_paras:
    if p.text in toc_exact:
        set_text(p, toc_exact[p.text])

# Ensure the moved chapter title is clean after the global label replacements.
for p in all_paras:
    if 'PILOT STUDY AND PILOT STUDY AND PRELIMINARY RESULTS' in p.text:
        if p.style.name.startswith('toc'):
            set_text(p, '3.17\tPILOT STUDY AND PRELIMINARY RESULTS\t48')
        else:
            set_text(p, 'PILOT STUDY AND PRELIMINARY RESULTS')

# Remove the old Chapter 4 list-of-tables entries and replace their labels with Chapter 3 numbering.
for p in all_paras:
    txt = p.text
    for old, val in repls.items():
        if old == 'PRELIMINARY RESULTS':
            continue
        txt = txt.replace(old, val)
    if txt != p.text:
        set_text(p, txt)

# Keep the chapter outline accurate.
for p in all_paras:
    if 'This thesis is organized into five chapters.' in p.text:
        set_text(p, p.text.replace('five chapters', 'four chapters'))
    if p.text.startswith('Chapter 4 reports'):
        set_text(p, p.text.replace('Chapter 4', 'Section 3.17'))
    if p.text.startswith('Chapter 5 will'):
        set_text(p, p.text.replace('Chapter 5', 'Chapter 4'))
    if 'Draft of Chapter 4' in p.text:
        set_text(p, p.text.replace('Draft of Chapter 4', 'Draft of the results section'))
    if p.text.startswith('This chapter reports the preliminary results'):
        set_text(p, p.text.replace('This chapter reports', 'This section reports').replace('according to Chapter 3', 'in the main experiments'))
    if 'in the main experiments in the main experiments' in p.text:
        set_text(p, p.text.replace('in the main experiments in the main experiments', 'in the main experiments'))

# Final cross-reference cleanup after the pilot section has been repositioned.
for p in all_paras:
    if 'Chapter 4' in p.text:
        set_text(p, p.text.replace('Chapter 4', 'Section 3.17'))

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            if 'Chapter 4' in cell.text:
                cell.text = cell.text.replace('Chapter 4', 'Section 3.17').replace('Draft of Section 3.17', 'Draft of the results section')

# Keep one top-level pilot entry in the visible contents list; the former 4.1
# entry was the pilot introduction and is intentionally omitted.
for p in all_paras:
    if p.style.name == 'toc 1' and p.text.startswith('PILOT STUDY AND PRELIMINARY RESULTS'):
        set_text(p, '3.17\tPILOT STUDY AND PRELIMINARY RESULTS\t48')
    if p.style.name.startswith('toc') and p.text == '3.17\tPilot Study and Preliminary Results\t48':
        set_text(p, '')

# The source template numbers chapter headings automatically. Since the pilot is now
# inside Chapter 3, use explicit section labels and disable the inherited Chapter-4
# numbering for the moved headings.
pilot_heading_numbers = {
    'Experimental Result Validation': '3.17.1',
    'Dataset and Evaluation Coverage': '3.17.1.1',
    'Reproducibility and Execution Environment': '3.17.1.2',
    'Preliminary Pipeline and Structural Results': '3.17.2',
    'Pilot Pipeline Validation': '3.17.2.1',
    'BLIP-3 Structural Probe': '3.17.2.2',
    'Baseline BLIP-3 Results': '3.17.3',
    'Baseline Accuracy': '3.17.3.1',
    'Baseline Response Behaviour': '3.17.3.2',
    'Baseline Efficiency': '3.17.3.3',
    'Baseline Comparison with Deployability Criteria': '3.17.3.4',
    'Implications for the Main Experiments': '3.17.4',
    'Chapter Summary': '3.17.5',
}
for p in all_paras:
    if p._p in pilot_nodes and p.text in pilot_heading_numbers:
        disable_auto_numbering(p)
        set_text(p, pilot_heading_numbers[p.text] + ' ' + p.text)
    elif p._p in pilot_nodes and p.text == 'Pilot Study Introduction':
        disable_auto_numbering(p)
        p.style = doc.styles['Normal']
    elif p._p in pilot_nodes and p.text.strip() == 'PILOT STUDY AND PRELIMINARY RESULTS':
        disable_auto_numbering(p)
        p.style = doc.styles['Normal']
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_text(p, 'PILOT STUDY AND PRELIMINARY RESULTS')
        if p.runs:
            p.runs[0].bold = True
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(12)

doc.save(str(OUT))
print(OUT)
