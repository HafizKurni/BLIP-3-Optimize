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
    'Research on VQA and vision–language modeling continues to emphasize model capability under well-resourced computing conditions. Modern VLMs perform strongly across multimodal tasks, but their memory, storage, and inference requirements restrict deployment on consumer-grade or otherwise resource-constrained systems.':
        'Vision–language models can perform VQA accurately, but their large memory, storage, and computation requirements make deployment difficult on consumer-grade and other resource-constrained devices.',
    '\tModel compression, including pruning and quantization, is well established as a means of reducing the size and computational cost of deep neural networks (Z. Li et al., 2023). However, improved efficiency does not automatically mean that a model becomes deployable, because compression may also reduce task performance. For VLMs, this problem is more complex, because performance depends on the interaction of several subsystems: visual information must be encoded, transformed by the multimodal connector, and then integrated with language reasoning to generate an answer. Compressing each subsystem may therefore yield different computational benefits and different levels of accuracy loss.':
        '\tPruning and quantization can reduce the resources required by a model, but they can also reduce VQA accuracy (Z. Li et al., 2023). The effect may differ across BLIP-3 because its visual encoder, multimodal connector, and language model perform different functions.',
    '\tPrevious studies have examined important parts of this problem, including quantization for efficient VQA deployment (Mishra et al., 2024), visual-token pruning (Chen et al., 2024; Zeng et al., 2025), joint quantization and token pruning (X. Li et al., 2026), and the internal effects of compression on VLMs (Elluru et al., 2026). Nevertheless, the reviewed literature shows three connected limitations when this evidence is applied to BLIP-3 in a resource-constrained setting:':
        '\tPrevious studies have examined quantization, pruning, and combined compression in VQA and VLMs (Mishra et al., 2024; Zeng et al., 2025; X. Li et al., 2026; Elluru et al., 2026). However, three connected problems remain for BLIP-3:',
    '(i)\tThe overall effects of pruning, quantization, and combined compression have not been compared for BLIP-3 under one controlled experimental environment, leaving the efficiency–accuracy effects of each strategy difficult to interpret (Mishra et al., 2024; Li et al., 2023).':
        '(i)\tThe overall effects of pruning-only, quantization-only, and combined compression have not been compared for BLIP-3 under the same experimental conditions (Mishra et al., 2024; Li et al., 2023).',
    '(ii)\tBecause BLIP-3 is modular, its components may contribute differently to computational cost and may tolerate structural pruning differently; however, component-level evidence for the visual encoder, multimodal connector, and language model remains limited (Michel et al., 2019; Ma et al., 2023).':
        '(ii)\tIt is not clear which BLIP-3 component contributes most to computational cost or is most sensitive to structural pruning (Michel et al., 2019; Ma et al., 2023).',
    '(iii)\tThe resulting configurations are rarely assessed through one integrated decision that combines accuracy, memory, latency, model size, and explicit deployability thresholds; therefore, the most favorable trade-off and the main deployment bottleneck remain uncertain (Cooper et al., 2021; Mishra et al., 2024).':
        '(iii)\tIt is also unclear which compressed configuration offers the best balance between accuracy and deployment efficiency when accuracy, latency, memory, and model size are assessed together against predefined thresholds (Cooper et al., 2021; Mishra et al., 2024).',
    '\tThese limitations are sequentially related. First, the overall effect of each compression strategy must be measured against the uncompressed baseline. Second, the internal components must be examined to explain where computational cost and compression sensitivity arise. Third, the component-level and full-model results must be integrated into an efficiency–accuracy and deployability decision. The research problem is therefore an integration and deployment-evaluation gap rather than an absence of compression research. This study addresses the gap through a controlled quantitative evaluation of baseline and compressed BLIP-3 configurations under the same resource-constrained VQA environment.':
        '\tThese problems are related in sequence. First, the compression strategies must be compared with the uncompressed baseline. Second, the BLIP-3 components must be examined to explain their cost and sensitivity. Third, the results must be combined to determine which configurations are efficient and deployable. This study addresses these problems through a controlled quantitative evaluation of BLIP-3 under resource-constrained VQA conditions.',
    'The study is guided by the following three research questions. Each question is grounded in the need to evaluate compression as a measurable deployment problem rather than as a size-reduction exercise alone (Cooper et al., 2021; Li et al., 2023; Mishra et al., 2024).':
        'The study is guided by three research questions. They follow the sequence established in the Research Problem: overall compression effects, component sensitivity, and deployability (Cooper et al., 2021; Li et al., 2023; Mishra et al., 2024).',
    '(a) RQ1: To what extent do structured pruning, INT8 weight-only post-training quantization, and their combination change the peak GPU memory, inference latency, model size, and VQA accuracy of BLIP-3 relative to the uncompressed baseline?':
        '(a) RQ1: How do pruning-only, INT8 weight-only quantization-only, and combined compression affect BLIP-3 accuracy, peak GPU memory, inference latency, and model size compared with the uncompressed baseline? (Mishra et al., 2024; Li et al., 2023)',
    '(b) RQ2: How do the visual encoder, multimodal connector, and language model of BLIP-3 differ in their contribution to computational cost and in their sensitivity to structured pruning? This question is motivated by evidence that transformer components are not equally important and that pruning sensitivity can vary across components (Michel et al., 2019; Ma et al., 2023).':
        '(b) RQ2: Which BLIP-3 component contributes most to computational cost, and which component is most sensitive to structured pruning? (Michel et al., 2019; Ma et al., 2023)',
    '(c) RQ3: Which compressed BLIP-3 configurations provide the most favorable efficiency–accuracy trade-off and satisfy the predefined RCVQA deployability criteria? A joint decision is necessary because lower resource use does not by itself establish practical deployability (Cooper et al., 2021; Mishra et al., 2024).':
        '(c) RQ3: Which compressed BLIP-3 configurations provide the best balance between accuracy and deployment efficiency, and which configurations meet the predefined RCVQA criteria? (Cooper et al., 2021; Mishra et al., 2024)',
    'The questions follow a sequential logic. RQ1 establishes the overall effects of the compression strategies. RQ2 identifies where computational cost and compression sensitivity are located within BLIP-3. RQ3 integrates these findings through multi-metric trade-off analysis and explicit deployment thresholds.':
        'The questions are connected. RQ1 measures the overall effects of compression. RQ2 explains the role and sensitivity of each BLIP-3 component. RQ3 uses these findings to identify efficient and deployable configurations.',
    'The main objective of this study is to evaluate whether post-training compression can make BLIP-3 feasible for resource-constrained VQA deployment while preserving an acceptable level of accuracy. The three specific objectives correspond directly to the research questions and are supported by the need for controlled, reproducible efficiency evaluation (Reddi et al., 2020; Li et al., 2023).':
        'The main objective is to determine whether post-training compression can make BLIP-3 more suitable for resource-constrained VQA while maintaining acceptable accuracy. The three objectives below correspond directly to the three research questions (Reddi et al., 2020; Li et al., 2023).',
    '(a) RO1: To measure the changes in peak GPU memory, inference latency, model size, and VQA accuracy produced by structured pruning, INT8 weight-only post-training quantization, and their combination, relative to the uncompressed baseline. These numerical measurements are required to make the efficiency–accuracy trade-off explicit (Cooper et al., 2021; Mishra et al., 2024).':
        '(a) RO1: To measure how pruning-only, quantization-only, and combined compression change BLIP-3 accuracy, peak GPU memory, inference latency, and model size compared with the baseline (Cooper et al., 2021; Mishra et al., 2024).',
    '(b) RO2: To compare the computational contribution and pruning sensitivity of the visual encoder, multimodal connector, and language model of BLIP-3, using component-level profiling and parameter-normalized sensitivity analysis (Michel et al., 2019; Ma et al., 2023).':
        '(b) RO2: To measure the computational contribution of the visual encoder, multimodal connector, and language model, and compare their pruning sensitivity after accounting for their different sizes (Michel et al., 2019; Ma et al., 2023).',
    '(c) RO3: To identify the compressed configurations with the most favorable efficiency–accuracy profiles, determine which configurations satisfy the RCVQA deployability criteria, and identify the criterion that most limits deployment (Cooper et al., 2021; Miettinen, 1999).':
        '(c) RO3: To identify the configurations with the best accuracy–efficiency balance, determine which meet all RCVQA criteria, and identify the criterion that most limits deployment (Cooper et al., 2021; Miettinen, 1999).',
}

for p in doc.paragraphs:
    if p.text in replacements:
        set_text(p, replacements[p.text])

# Remove the empty paragraph left between Research Problem items (ii) and (iii).
paras = doc.paragraphs
for i in range(1, len(paras) - 1):
    if paras[i].text == '' and paras[i-1].text.startswith('(ii)') and paras[i+1].text.startswith('(iii)'):
        paras[i]._element.getparent().remove(paras[i]._element)
        break

doc.save(str(path))
print(path)
