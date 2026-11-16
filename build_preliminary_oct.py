from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE

out='/Users/hafiz/Documents/ChatGPT/Thesis Master Data Science (RCVAQ)/[Octo] Preliminary Work Explained.docx'
doc=Document()
sec=doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.top_margin=Inches(.68); sec.bottom_margin=Inches(.68); sec.left_margin=Inches(.85); sec.right_margin=Inches(.85)
styles=doc.styles
styles['Normal'].font.name='Aptos'; styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'),'Aptos'); styles['Normal'].font.size=Pt(10.3)
styles['Normal'].paragraph_format.space_after=Pt(6); styles['Normal'].paragraph_format.line_spacing=1.08
for name,size in [('Title',20),('Heading 1',14),('Heading 2',11.5)]:
    styles[name].font.name='Aptos Display' if name=='Title' else 'Aptos'; styles[name]._element.rPr.rFonts.set(qn('w:eastAsia'),styles[name].font.name); styles[name].font.size=Pt(size); styles[name].font.bold=True; styles[name].font.color.rgb=RGBColor(0,0,0)
styles['Heading 1'].paragraph_format.space_before=Pt(14); styles['Heading 1'].paragraph_format.space_after=Pt(5)
styles['Heading 2'].paragraph_format.space_before=Pt(9); styles['Heading 2'].paragraph_format.space_after=Pt(3)

def shade(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)
def borders(table):
    tblPr=table._tbl.tblPr; b=tblPr.first_child_found_in('w:tblBorders')
    if b is None: b=OxmlElement('w:tblBorders'); tblPr.append(b)
    for edge in ('top','left','bottom','right','insideH','insideV'):
        el=b.find(qn('w:'+edge))
        if el is None: el=OxmlElement('w:'+edge); b.append(el)
        el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'4'); el.set(qn('w:color'),'D9D9D9')
def table(headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.style='Table Grid'; borders(t)
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i]; c.text=h; shade(c,'1F4E78'); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for p in c.paragraphs:
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs: r.font.bold=True; r.font.color.rgb=RGBColor(255,255,255); r.font.size=Pt(9)
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,val in enumerate(row):
            cells[i].text=str(val); cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri%2==1: shade(cells[i],'F2F6FA')
            for p in cells[i].paragraphs:
                for r in p.runs: r.font.size=Pt(8.6)
        
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

def p(text='', boldlead=None):
    pa=doc.add_paragraph()
    if boldlead and text.startswith(boldlead):
        pa.add_run(boldlead).bold=True; pa.add_run(text[len(boldlead):])
    else: pa.add_run(text)
    return pa

t=doc.add_paragraph(style='Title'); t.alignment=WD_ALIGN_PARAGRAPH.LEFT; t.add_run('Preliminary Work for Proposal Defense')
s=doc.add_paragraph(); s.alignment=WD_ALIGN_PARAGRAPH.LEFT; r=s.add_run('A clearer account of the pilot study and structural probe for BLIP-3 compression'); r.bold=True; r.font.size=Pt(11.5); r.font.color.rgb=RGBColor(31,78,121)
p('This document restates the preliminary work conducted before the main experiments. Its purpose was to confirm that the proposed evaluation pipeline could run with the available resources and to determine how the BLIP-3 checkpoint is organized for structured pruning. The work does not replace the thesis baseline; it validates the experimental procedure and identifies constraints that must be handled in the main study.')

doc.add_heading('1 Preliminary Work at a Glance', level=1)
p('The preliminary work had two parts: a small baseline pilot and a structural probe of the model. Both used the uncompressed Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5 checkpoint in BF16 precision on a rented cloud instance equipped with one NVIDIA GeForce RTX 3090 GPU with 24 GB of memory.')

doc.add_heading('2 Baseline Pilot', level=1)
p('The pilot followed the same evaluation protocol planned for the main experiments. It used 100 questions selected at random from the frozen 5,040-question evaluation subset. The model generated answers using greedy decoding, with a maximum of 10 new tokens and batch size 1. Answers were scored with the official VQAv2 leave-one-out procedure.')
doc.add_heading('Pilot settings', level=2)
table(['Item','Setting'],[
['GPU','NVIDIA GeForce RTX 3090 (24 GB), rented cloud instance'],['Software','Python 3.12; PyTorch 2.11.0 with CUDA 12.8'],['Model','Salesforce/xgen-mm-phi3-mini-instruct-interleave-r-v1.5, BF16'],['Prompt','Fixed short-answer instruction from Section 3.4.1 of the proposal'],['Questions','100: 49 other, 38 yes/no, and 13 number questions'],['Latency measurement','End-to-end, one pass over all questions, without warm-up runs']], [1.55,5.35])
doc.add_heading('Pilot results', level=2)
p('The pilot produced an overall VQA accuracy of 83.10%. Bootstrap resampling of question-level scores was used to calculate the 95% confidence intervals. The pilot also measured latency and GPU memory, but these measurements are used only to validate feasibility; the thesis baseline will come from the complete 5,040-question subset.')
table(['Metric','Result'],[
['VQA accuracy','83.10% (95% CI 76.40–89.20)'],['Other questions (n = 49)','74.90% (95% CI 64.29–84.90)'],['Yes/no questions (n = 38)','95.00% (95% CI 89.47–98.95)'],['Number questions (n = 13)','79.23% (95% CI 56.15–100.00)'],['Responses longer than three words','1 of 100'],['Mean end-to-end latency','0.334 s (SD 0.070 s)'],['Mean latency excluding first two inferences','0.329 s (SD 0.057 s)'],['Median latency and throughput','0.330 s and 2.99 queries/s'],['Peak allocated and reserved memory','8.73 GB and 8.96 GB']], [3.6,3.3])
p('The single response longer than three words was “No parking any time,” which was a natural phrase for reading a sign. The pilot therefore indicates that the short-answer instruction was followed in practice.')

doc.add_heading('3 Structural Probe of the Checkpoint', level=1)
p('The structural probe loaded the checkpoint, counted parameters, and inspected the weight layout of each component. Parameters for the visual encoder and language model were counted directly from their weight tensors. The connector parameter count was obtained as the remainder of the total.')
table(['Component','Structure','Parameters','Share'],[
['Visual encoder','Vision Transformer; 27 layers; hidden size 1,152; MLP size 4,304; patch size 14','428.2 million','9.82%'],['Multimodal connector','Perceiver Resampler; 128 latent queries; projection 1,152 → 3,072','≈109.9 million','≈2.52%'],['Language model','Phi-3-mini; 32 layers; hidden size 3,072; 32 heads of dimension 96; fused QKV and gate-up projections','3,821.1 million','87.66%'],['Total','BF16 weight footprint = parameters × 2 bytes','4,359,257,219','100%']], [1.25,3.55,1.25,1.0])

doc.add_heading('4 What the Preliminary Work Shows', level=1)
obs=[
('The pipeline is functional.','All 100 questions were completed without error. The question-level scores were 0, 0.3, 0.6, 0.9, or 1.0, matching the expected VQAv2 scoring pattern.'),
('The pilot is suitable for validation, not precise baseline estimation.','The overall confidence interval spans about 13 percentage points, while the interval for the 13 number questions spans more than 40 points. The baseline accuracy must therefore be calculated on the full 5,040-question subset.'),
('Both resource targets require meaningful compression.','BF16 weights occupy 8.12 GB and peak allocated memory reached 8.73 GB. The 8 GB memory target requires at least 0.73 GB of reduction, while the 4 GB model-size target requires roughly half of the stored weights to be removed. INT8 quantization alone is estimated at about 4.2 GB if token embeddings and the output head remain in BF16, so combined compression may be necessary.'),
('Most savings must come from the language model.','The language model contains 87.7% of all parameters, compared with 9.8% in the visual encoder and about 2.5% in the connector. This supports the parameter-normalized sensitivity measure in Equation 3.11 of the proposal.'),
('Latency must be evaluated on the target low-resource device.','The RTX 3090 mean latency was only 0.334 s, well below the 2.0 s criterion. It is therefore not a meaningful deployability constraint. Configurations that satisfy memory, size, and accuracy retention will be re-tested on an 8 GB consumer GPU. The first two inferences were slower because the pilot had no warm-up runs, which supports the main protocol’s ten warm-up runs.'),
('The weight layout limits attention-head pruning.','Each language-model layer stores Q, K, and V in one fused matrix and gate and up projections in another. Consequently, attention heads and feed-forward channels must be removed using coordinated slicing. The probe could construct 16- and 24-head configurations, but not 28- or 30-head configurations. The planned 29-, 26-, and 22-head pruning levels therefore require a modified configuration that preserves the head dimension of 96. Feed-forward channels do not have this restriction and should be pruned first, with attention heads pruned later.')]
for lead,body in obs: p(lead+' '+body, lead)

doc.add_heading('5 Evidence and Reporting Boundary', level=1)
p('The supporting evidence consists of the pilot prediction and metrics files together with the structural-probe report. The pilot results are not pooled with the thesis baseline because the pilot contains only 100 questions from the full evaluation subset. Instead, the baseline will be obtained from all 5,040 questions under the same protocol, including ten warm-up runs before efficiency measurement. Reproducing the 100 pilot predictions exactly will serve as a deterministic-decoding check.')
p('Efficiency will be measured separately on the 500-question timing subset using three timed passes. All fifteen main configurations will be measured on RTX 3090 instances in one session on one host, reducing variation caused by different rented machines. At the pilot latency, the 98,250 inferences planned for the main experiments correspond to approximately nine GPU-hours on an RTX 3090, supporting the feasibility of the proposed computational budget.')

doc.add_heading('6 Conclusion', level=1)
p('The preliminary work confirms that the experimental pipeline is operational and that the planned study is computationally feasible. It also shows that the main challenge is not simply reducing model size: compression must be large enough to meet both memory and storage targets while preserving accuracy, and pruning must respect the fused weight layout of the language model. These findings justify the staged experimental plan in the proposal: prune feed-forward channels first, evaluate the resulting configurations, and address attention-head pruning only after the structural constraints are incorporated.')

doc.save(out)
print(out)
