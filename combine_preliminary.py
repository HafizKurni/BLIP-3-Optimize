from pathlib import Path
from docx import Document

path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))

def remove_paragraph(p):
    p._element.getparent().remove(p._element)

# Remove the duplicate preliminary-results subsection from Feasibility, Schedule,
# and Risk Management. Its baseline content is already presented in Section 3.17.
for p in list(doc.paragraphs):
    if p.text.strip() in {
        'Preliminary Results',
        'The baseline phase of the study has been completed and is reported in Section 3.17. The uncompressed baseline was evaluated on the frozen 5,040-question evaluation subset under the protocol described in this chapter and achieved a VQA accuracy of 79.45% (95% CI 78.45–80.44). This value is used as Ab in all subsequent comparisons. The efficiency of the baseline will be measured again with the full protocol in the single efficiency session together with the compressed configurations (Section 3.9.2).',
    }:
        remove_paragraph(p)

# Remove the obsolete 3.13.1 entry from the visible contents list.
for p in doc.paragraphs:
    if p.text.strip().startswith('3.13.1\tPreliminary Results'):
        remove_paragraph(p)

# Clarify that the pilot section now contains the complete preliminary phase.
for p in doc.paragraphs:
    if p.text == 'Pilot Study Introduction':
        p.text = 'Pilot Study and Preliminary Results Introduction'
        break

# Renumber the remaining subsections after removing 3.13.1.
renumber = {
    '3.13.2\tComputational Budget\t43': '3.13.1\tComputational Budget\t43',
    '3.13.3\tExperimental Schedule\t43': '3.13.2\tExperimental Schedule\t43',
    '3.13.4\tRisk Identification and Mitigation\t44': '3.13.3\tRisk Identification and Mitigation\t44',
    '3.13.5\tSoftware and Hardware Documentation\t45': '3.13.4\tSoftware and Hardware Documentation\t45',
}
for p in doc.paragraphs:
    if p.text in renumber:
        p.text = renumber[p.text]

doc.save(str(path))
print(path)
