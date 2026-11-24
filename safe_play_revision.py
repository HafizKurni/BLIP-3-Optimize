from pathlib import Path
from docx import Document


path = Path('[REVISED] Master PD Hafiz Proposal.docx')
doc = Document(str(path))


def set_text(paragraph, text):
    for child in list(paragraph._p):
        if not child.tag.endswith('}pPr'):
            paragraph._p.remove(child)
    paragraph.add_run(text)


def set_cell_text(cell, text):
    paragraph = cell.paragraphs[0]
    set_text(paragraph, text)
    for extra in list(cell.paragraphs[1:]):
        extra._element.getparent().remove(extra._element)


paragraph_replacements = {
    '\tPrevious studies have examined quantization, pruning, and combined compression in VQA and VLMs (Mishra et al., 2024; Zeng et al., 2025; X. Li et al., 2026; Elluru et al., 2026). However, three connected problems remain for BLIP-3:':
        '\tPrevious studies have examined quantization, pruning, and combined compression in VQA and VLMs (Mishra et al., 2024; Zeng et al., 2025; X. Li et al., 2026; Elluru et al., 2026). When this evidence is considered for BLIP-3 in a resource-constrained setting, the reviewed literature indicates three connected research problems:',
    '(i)\tThe overall effects of pruning-only, quantization-only, and combined compression have not been compared for BLIP-3 under the same experimental conditions (Mishra et al., 2024; Li et al., 2023).':
        '(i)\tAlthough related studies have evaluated individual compression techniques or other vision–language models, the reviewed literature does not clearly provide a controlled comparison of structured pruning applied alone, INT8 weight-only quantization applied alone, and combined compression for BLIP-3 under the same dataset, decoding protocol, hardware, and efficiency-measurement procedure. Consequently, the relative effects of these strategies on BLIP-3 remain uncertain (Xue et al., 2025; Mishra et al., 2024; X. Li et al., 2026).',
    '(ii)\tIt is not clear which BLIP-3 component contributes most to computational cost or is most sensitive to structural pruning (Michel et al., 2019; Ma et al., 2023).':
        '(ii)\tThe reviewed literature also does not clearly establish which BLIP-3 component contributes most to computational cost or is most sensitive to structured pruning. This makes it difficult to determine how compression should be allocated across the visual encoder, multimodal connector, and language model (Michel et al., 2019; Ma et al., 2023).',
    '(iii)\tIt is also unclear which compressed configuration offers the best balance between accuracy and deployment efficiency when accuracy, latency, memory, and model size are assessed together against predefined thresholds (Cooper et al., 2021; Mishra et al., 2024).':
        '(iii)\tFinally, the reviewed literature does not clearly establish which compressed configuration provides the best balance between accuracy and deployment efficiency when VQA accuracy, inference latency, peak GPU memory, and model size are evaluated jointly against predefined thresholds. A configuration that improves one measure may not satisfy the others (Cooper et al., 2021; Mishra et al., 2024).',
    '\tThese problems are related in sequence. First, the compression strategies must be compared with the uncompressed baseline. Second, the BLIP-3 components must be examined to explain their cost and sensitivity. Third, the results must be combined to determine which configurations are efficient and deployable. This study addresses these problems through a controlled quantitative evaluation of BLIP-3 under resource-constrained VQA conditions.':
        '\tThese problems are related in sequence. First, the compression strategies must be compared with the uncompressed baseline. Second, the BLIP-3 components must be examined to explain their cost and sensitivity. Third, the results must be combined to determine which configurations are efficient and deployable. The study addresses the three problems through a controlled quantitative evaluation of BLIP-3 under resource-constrained VQA conditions.',
    'The study is guided by three research questions. They follow the sequence established in the Research Problem: overall compression effects, component sensitivity, and deployability (Cooper et al., 2021; Li et al., 2023; Mishra et al., 2024).':
        'The study is guided by three research questions. They translate the three research problems into measurable questions about overall compression effects, component sensitivity, and deployability (Cooper et al., 2021; Li et al., 2023; Mishra et al., 2024).',
    '(a) RQ1: How do structured pruning applied alone, INT8 weight-only quantization applied alone, and their combination affect BLIP-3 accuracy, peak GPU memory, inference latency, and model size compared with the uncompressed baseline? (Mishra et al., 2024; Li et al., 2023)':
        '(a) RQ1: Under a common dataset, decoding protocol, hardware, and measurement procedure, how do structured pruning applied alone, INT8 weight-only quantization applied alone, and their combination affect BLIP-3 accuracy, peak GPU memory, inference latency, and model size compared with the uncompressed baseline? (Mishra et al., 2024; Li et al., 2023)',
    '(b) RQ2: Which BLIP-3 component contributes most to computational cost, and which component is most sensitive to structured pruning? (Michel et al., 2019; Ma et al., 2023)':
        '(b) RQ2: Which BLIP-3 component contributes most to computational cost, and which component is most sensitive to structured pruning when component size is taken into account? (Michel et al., 2019; Ma et al., 2023)',
    '(c) RQ3: Which compressed BLIP-3 configurations provide the best balance between accuracy and deployment efficiency, and which configurations meet the predefined RCVQA criteria? (Cooper et al., 2021; Mishra et al., 2024)':
        '(c) RQ3: Which compressed BLIP-3 configurations provide the best balance between accuracy and deployment efficiency, and which configurations meet the predefined RCVQA criteria when the four metrics are assessed jointly? (Cooper et al., 2021; Mishra et al., 2024)',
    'The questions are connected. RQ1 measures the overall effects of compression. RQ2 explains the role and sensitivity of each BLIP-3 component. RQ3 uses these findings to identify efficient and deployable configurations.':
        'The questions are connected. RQ1 measures the overall effects of compression under a common protocol. RQ2 explains the role and sensitivity of each BLIP-3 component. RQ3 uses these findings to identify configurations that offer a favorable balance and meet the deployment criteria.',
    'The main objective is to determine whether post-training compression can make BLIP-3 more suitable for resource-constrained VQA while maintaining acceptable accuracy. The three objectives below correspond directly to the three research questions (Reddi et al., 2020; Li et al., 2023).':
        'The main objective is to assess whether post-training compression can make BLIP-3 more suitable for resource-constrained VQA while maintaining acceptable accuracy. The three objectives below correspond directly to the research questions and focus on measurable outcomes (Reddi et al., 2020; Li et al., 2023).',
    '(a) RO1: To measure how structured pruning applied alone, INT8 weight-only quantization applied alone, and their combination change BLIP-3 accuracy, peak GPU memory, inference latency, and model size compared with the baseline (Cooper et al., 2021; Mishra et al., 2024).':
        '(a) RO1: To compare the changes in BLIP-3 accuracy, peak GPU memory, inference latency, and model size produced by structured pruning applied alone, INT8 weight-only quantization applied alone, and their combination under a common experimental protocol (Cooper et al., 2021; Mishra et al., 2024).',
    '(b) RO2: To measure the computational contribution of the visual encoder, multimodal connector, and language model, and compare their pruning sensitivity after accounting for their different sizes (Michel et al., 2019; Ma et al., 2023).':
        '(b) RO2: To profile the computational contribution of the visual encoder, multimodal connector, and language model, and compare their pruning sensitivity after accounting for their different sizes (Michel et al., 2019; Ma et al., 2023).',
    '(c) RO3: To identify the configurations with the best accuracy–efficiency balance, determine which meet all RCVQA criteria, and identify the criterion that most limits deployment (Cooper et al., 2021; Miettinen, 1999).':
        '(c) RO3: To evaluate the accuracy–efficiency balance of the compressed configurations, determine which meet all RCVQA criteria, and identify the criterion that most limits deployment (Cooper et al., 2021; Miettinen, 1999).',
    '\tThe comparison shows that the individual techniques are established, but they address different parts of the problem. The original xGen-MM/BLIP-3 study evaluates multimodal capability and post-training safety interventions rather than pruning and quantization. Mishra et al. (2024) study quantization for VQA deployment on an embedded device, but not BLIP-3 or structural pruning. X. Li et al. (2026) compare joint quantization with visual-token pruning on other VLMs, whereas Elluru et al. (2026) examine internal effects rather than deployment feasibility. Thus, no identified study in this comparison combines BLIP-3, the three compression conditions, identical evaluation controls, component-level analysis, and explicit deployment thresholds.':
        '\tThe comparison shows that the individual techniques are established, but they address different parts of the problem. The original xGen-MM/BLIP-3 study evaluates multimodal capability and post-training safety interventions rather than pruning and quantization. Mishra et al. (2024) study quantization for VQA deployment on an embedded device, but not BLIP-3 or structural pruning. X. Li et al. (2026) compare joint quantization with visual-token pruning on other VLMs, whereas Elluru et al. (2026) examine internal effects rather than deployment feasibility. Taken together, the reviewed studies do not clearly cover BLIP-3, the three compression conditions, identical evaluation controls, component-level analysis, and explicit deployment thresholds within one study.',
    '(a)\tIn the studies reviewed in Table 2.2, no identified work provides a BLIP-3-specific comparison of structured pruning-only, INT8 weight-only quantization-only, and combined compression under the same dataset, decoding protocol, hardware, and efficiency-measurement procedure. Because the reviewed studies use different models, compression targets, tasks, or execution settings, their results cannot isolate the effect of compression strategy as cleanly as a controlled within-study comparison (Xue et al., 2025; Mishra et al., 2024; X. Li et al., 2026).':
        '(a)\tIn the studies reviewed in Table 2.2, the evidence does not clearly provide a BLIP-3-specific comparison of structured pruning applied alone, INT8 weight-only quantization applied alone, and combined compression under the same dataset, decoding protocol, hardware, and efficiency-measurement procedure. Because the reviewed studies use different models, compression targets, tasks, or execution settings, their results cannot isolate the effect of compression strategy as cleanly as a controlled within-study comparison (Xue et al., 2025; Mishra et al., 2024; X. Li et al., 2026).',
    '(b)\tIt is not yet clear which BLIP-3 component, the visual encoder, the multimodal connector, or the language model, is most sensitive to structured pruning, particularly when sensitivity is adjusted for the very different sizes of the components.':
        '(b)\tThe reviewed evidence does not clearly establish which BLIP-3 component, the visual encoder, the multimodal connector, or the language model, is most sensitive to structured pruning, particularly when sensitivity is adjusted for the different sizes of the components (Xue et al., 2025; Michel et al., 2019; Ma et al., 2023).',
    '(c)\tIn the studies reviewed, no identified work evaluates deployability as a joint decision across VQA accuracy, inference latency, peak GPU memory, and model size using predefined thresholds. Related studies typically report accuracy retention or one or two efficiency measures, rather than applying all four criteria simultaneously.':
        '(c)\tIn the studies reviewed, deployability is not clearly evaluated as a joint decision across VQA accuracy, inference latency, peak GPU memory, and model size using predefined thresholds. Related studies generally report accuracy retention or one or two efficiency measures, rather than applying all four criteria simultaneously (Cooper et al., 2021; Mishra et al., 2024).',
}

changed = 0
for paragraph in doc.paragraphs:
    if paragraph.text in paragraph_replacements:
        set_text(paragraph, paragraph_replacements[paragraph.text])
        changed += 1


# Keep the alignment table consistent with the safer wording used in Chapter 1.
alignment = doc.tables[0]
table_updates = {
    1: [
        'RQ1: Controlled comparison of compression effects',
        'RO1: Compare accuracy and efficiency across strategies',
        'H1',
        'Compare BASE, full-model pruning, INT8 quantization, and combined compression under a common protocol using relative reductions and accuracy retention',
    ],
    2: [
        'RQ2: Component-level cost and pruning sensitivity',
        'RO2: Profile component contribution and sensitivity',
        'H2',
        'Baseline component profiling and component-level pruning at 10%, 20%, and 30%, with absolute and parameter-normalized sensitivity',
    ],
    3: [
        'RQ3: Joint trade-off and deployability decision',
        'RO3: Identify balanced and deployable configurations',
        'H3 / Descriptive',
        'Pareto-based comparison and joint evaluation against memory, latency, model-size, and accuracy-retention criteria',
    ],
}
for row_index, values in table_updates.items():
    for cell, value in zip(alignment.rows[row_index].cells, values):
        set_cell_text(cell, value)


if changed != len(paragraph_replacements):
    missing = len(paragraph_replacements) - changed
    raise RuntimeError(f'Only changed {changed} of {len(paragraph_replacements)} paragraph targets; {missing} target(s) were not found.')

doc.save(str(path))
print(f'Updated {changed} paragraphs and {len(table_updates)} alignment-table rows in {path}')
