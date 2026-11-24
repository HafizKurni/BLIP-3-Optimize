from pathlib import Path
from docx import Document


path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))


def set_text(paragraph, text):
    for child in list(paragraph._p):
        if not child.tag.endswith('}pPr'):
            paragraph._p.remove(child)
    paragraph.add_run(text)


replacements = {
    '\tTherefore, this study addresses the gap through a controlled RCVQA framework. It compares the uncompressed baseline, structured pruning-only, INT8 weight-only quantization-only, and combined compression using the same data, prompt, decoding, hardware, and measurement procedures. It then examines component-level sensitivity and applies explicit deployability criteria so that the relative effects can be interpreted within one coherent experimental design.':
        '\tTherefore, this study addresses the gap through a controlled RCVQA framework. It compares the uncompressed baseline with structured pruning applied alone, INT8 weight-only quantization applied alone, and combined compression using the same data, prompt, decoding, hardware, and measurement procedures. It then examines component-level sensitivity and applies explicit deployability criteria so that the relative effects can be interpreted within one coherent experimental design.',
    '(b)\tFull-model benchmarking identifies the configurations most suitable for deployment. In full-model experiments, the visual encoder, multimodal connector, and language model are pruned at the same percentage. This track also includes quantization-only and combined configurations and addresses RQ1, RQ3, and RQ3.':
        '(b)\tFull-model benchmarking identifies the configurations most suitable for deployment. In full-model experiments, the visual encoder, multimodal connector, and language model are pruned at the same percentage. This track also includes quantization-only and combined configurations and addresses RQ1 and RQ3.',
}

changed = 0
for paragraph in doc.paragraphs:
    if paragraph.text in replacements:
        set_text(paragraph, replacements[paragraph.text])
        changed += 1

if changed != len(replacements):
    raise RuntimeError(f'Changed {changed} of {len(replacements)} expected paragraphs.')

doc.save(str(path))
print(f'Applied {changed} final safe-play cleanups.')
