from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

src = '/Users/hafiz/Desktop/INTI Master Kuliah/Supervisor/Thesis Bimbingan/[Sept] Master_PD_Hafiz_Revised.docx'
out = '/Users/hafiz/Documents/ChatGPT/Thesis Master Data Science (RCVAQ)/Master_PD_Hafiz_Revised_Updated.docx'
doc = Document(src)

def find(text):
    for p in doc.paragraphs:
        if p.text.strip() == text:
            return p
    raise ValueError(text)

def after(p, text, style='INTI-C'):
    el = OxmlElement('w:p')
    p._p.addnext(el)
    q = Paragraph(el, p._parent)
    q.style = style
    q.add_run(text)
    return q

p = find('The RCVQA environment represents a consumer-grade deployment scenario while remaining controlled and reproducible. Consumer GPUs commonly provide between 6 GB and 12 GB of memory, which is well below the capacity of the servers on which large VLMs are usually evaluated. All experiments are conducted on a single fixed workstation. Because the uncompressed baseline requires more memory than the deployment envelope examined here, measurements are taken on a GPU with enough memory to run the baseline, and the memory limit is applied as an evaluation threshold rather than as the physical capacity of the measurement GPU.')
p.text = 'The RCVQA deployment scenario is defined using an 8 GB consumer-grade memory envelope while the measurement platform is kept fixed for controlled comparison. All experiments are conducted on one workstation equipped with one NVIDIA GeForce RTX 5090 GPU with 32 GB of VRAM. The RTX 5090 is used because the uncompressed BLIP-3 baseline requires sufficient memory for model loading and inference. The 8 GB value is therefore an evaluation constraint, not the physical memory of the measurement device.'
after(p, 'The GPU model, VRAM capacity, CPU, system RAM, operating system, NVIDIA driver, CUDA version, PyTorch version, Transformers version, and quantization backend are recorded and fixed throughout the experiment. The same platform and software environment are used for every configuration.')

p = find('The experiments are implemented in Python using PyTorch. The BLIP-3 checkpoint is loaded through the Hugging Face Transformers library together with the model code supplied with the checkpoint. Weight-only quantization is implemented with a PyTorch-native quantization backend (torchao is the intended backend). VQA answers are scored with a reimplementation of the official VQAv2 evaluation procedure, which is checked against the official script on the baseline predictions.')
after(p, 'The RTX 5090 is a measurement device rather than a claim about consumer-device latency. Latency is therefore interpreted as a hardware-specific comparative measure between the uncompressed and compressed configurations. The results should not be read as universal latency estimates for GPUs with 8–12 GB of VRAM.')

p = find('A configuration is deployable only when all four criteria are satisfied simultaneously. The memory threshold is grounded in consumer-hardware data, whereas the latency, size, and accuracy thresholds are operational criteria defined for this study. The latency threshold is not proposed as a universal VQA standard, and the size threshold is intentionally strict. Because the baseline stores approximately four billion parameters in 16-bit precision, pruning alone is not expected to satisfy S*, and the pattern of compliance across configurations is itself a result of interest. The accuracy threshold prevents a configuration from being classified as deployable merely because it saves resources. As a descriptive sensitivity check, compliance with a stricter 95% retention level is also reported.')
p.text = 'A configuration is deployable only when all four criteria are satisfied simultaneously. The 8 GB memory threshold represents the intended consumer-grade deployment envelope. The latency threshold of 2.0 seconds per image–question pair, the 4 GB model-size threshold, and the 90% accuracy-retention threshold are operational criteria defined for this study; they are not presented as universal VQA standards. The 2.0-second criterion is used consistently across configurations to compare relative compression effects on the fixed RTX 5090 platform. A sensitivity check using 95% accuracy retention is also reported.'
after(p, 'Because the RTX 5090 is substantially more capable than the 8 GB deployment envelope, a configuration that meets the latency criterion on the measurement GPU may not meet it on a lower-end consumer GPU. This distinction is recorded explicitly in the interpretation of results and in the validity threats and limitations.')

p = find("Model compression reduces the memory, storage, and computation required by a neural network while trying to preserve its accuracy (Z. Li et al., 2023). Among the many available techniques, pruning and quantization are the most widely used for large models because they can be applied to an existing pretrained network (Shinde et al., 2025). Their effects on VLMs are more complex than on single-modality models, because VQA accuracy depends on preserving cross-modal alignment, which is the model's ability to correctly connect visual information from the image with the meaning of the question.")
after(p, 'The broader compression literature provides important alternatives against which the present design should be positioned. LLM.int8() introduced mixed-precision decomposition for outlier-sensitive transformer activations (Dettmers et al., 2022). GPTQ demonstrated accurate post-training weight quantization using approximate second-order information (Frantar et al., 2023), while SparseGPT addressed one-shot pruning of large language models without retraining (Frantar & Alistarh, 2023). SmoothQuant moves quantization difficulty from activations to weights through equivalent transformations (Xiao et al., 2023), and AWQ uses activation-aware protection of salient weights for efficient low-bit inference (Lin et al., 2024). For multimodal models, FastV is relevant because it reduces visual tokens rather than permanently removing structural weights (Chen et al., 2024). These methods motivate the use of round-to-nearest INT8 and activation-informed structural importance as clearly defined baselines, while also showing that the present study does not claim to exhaust the compression design space.')

p = find('Justification for Selecting BLIP-3')
q = after(p, 'Preliminary Work', 'INTI-T3')
after(q, 'A feasibility pilot is planned before the full experiment and will be reported in the final thesis once the measurement environment is available. The pilot will run the uncompressed BLIP-3 baseline on approximately 100 VQAv2 samples and record accuracy, mean latency, and peak GPU memory using the same preprocessing, decoding, synchronization, and scoring procedures specified in this proposal. A second pilot will apply 10% structured pruning to one eligible component and verify successful model construction and forward inference. Because these measurements have not yet been completed, no pilot values are claimed in this proposal. The pilot is intended to de-risk the custom xGen-MM implementation, including fused QKV projections in Phi-3 and the Perceiver Resampler, before the 5,040-question evaluation.')

p = find('All subsets are obtained by proportional stratified random sampling by answer type, without replacement, with the random seed fixed at 42. Stratification preserves the natural composition of VQAv2 rather than creating an artificially balanced set.')
after(p, 'VQAv2 is selected because it is a widely used, publicly documented VQA benchmark with a stable official evaluation protocol and ten human answers per question. This makes it suitable for controlled comparison of small accuracy changes across compression configurations. The study does not claim that VQAv2 represents every xGen-MM capability: tasks such as image-text retrieval, captioning, and text-rich image understanding are outside scope. The single-dataset design is treated as an external-validity limitation, while the controlled benchmark provides a reproducible first test of BLIP-3 compression under explicit resource constraints.')

p = find('External validity is deliberately bounded. The findings concern one BLIP-3 checkpoint, a subset of VQAv2, the selected compression procedures, and one hardware environment. They are not claimed to generalize to all VLMs, datasets, or devices, and deployability conclusions apply only to the scenario defined in Section 3.3.2.')
p.text = 'External validity is deliberately bounded. The findings concern one BLIP-3 checkpoint, a subset of VQAv2, the selected compression procedures, and one RTX 5090 measurement environment. They are not claimed to generalize to all VLMs, datasets, or devices. In particular, latency findings indicate the relative efficiency effect of compression on the selected hardware rather than universal consumer-device performance. Deployability conclusions apply only to the scenario defined in Section 3.3.2.'

p = find('The study has several limitations. It evaluates one BLIP-3 checkpoint and one dataset, so the results may not transfer to other models or tasks. It uses post-training compression without recovery fine-tuning, which may underestimate the accuracy that compressed models could reach after brief retraining. The same pruning percentage is applied to every layer of a component, which may not be the optimal allocation. The number of latent queries in the connector is kept fixed, so reductions in visual-token length are not examined. Latency results depend on the hardware and the quantization backend, and peak allocated memory excludes the CUDA context. Finally, the thresholds describe one study-defined scenario rather than universal requirements.')
p.text = 'The study has several limitations. It evaluates one BLIP-3 checkpoint and one VQAv2 dataset, so the results may not transfer to other models, datasets, or tasks. It uses post-training compression without recovery fine-tuning, which may underestimate the accuracy that compressed models could reach after brief retraining. The same pruning percentage is applied to every layer of a component, which may not be the optimal allocation. The number of latent queries in the connector is kept fixed, so reductions in visual-token length are not examined. Latency is measured only on one NVIDIA RTX 5090 with 32 GB of VRAM and therefore does not reproduce the latency of lower-end consumer GPUs. The quantization backend may also affect results, and peak allocated memory excludes the CUDA context. Finally, the thresholds describe one study-defined scenario rather than universal requirements.'

for p in doc.paragraphs:
    if p.text.startswith('The study uses a quantitative, controlled comparative experimental design.'):
        p.text = p.text.replace('(Lim, 2025; Slater, 2025)', '(Han et al., 2015; Shuvo et al., 2023)')

refs = [
'Dettmers, T., Lewis, M., Shleifer, S., & Zettlemoyer, L. (2022). LLM.int8(): 8-bit matrix multiplication for transformers at scale. Advances in Neural Information Processing Systems, 35. https://doi.org/10.48550/arXiv.2208.07339',
'Frantar, E., Ashkboos, S., Hoeftmann, K., & Alistarh, D. (2023). GPTQ: Accurate post-training quantization for generative pre-trained transformers. In International Conference on Learning Representations (ICLR 2023). https://doi.org/10.48550/arXiv.2210.17323',
'Frantar, E., & Alistarh, D. (2023). SparseGPT: Massive language models can be accurately pruned in one-shot. In International Conference on Machine Learning (ICML 2023). https://doi.org/10.48550/arXiv.2301.00774',
'Xiao, G., Lin, J., Seifert, C., & Han, S. (2023). SmoothQuant: Accurate and efficient post-training quantization for large language models. In Proceedings of the 40th International Conference on Machine Learning (ICML 2023). https://doi.org/10.48550/arXiv.2211.10438',
'Lin, J., Tang, J., Tang, H., Yang, S., Dang, X., Gan, C., & Han, S. (2024). AWQ: Activation-aware weight quantization for LLM compression and acceleration. In Proceedings of Machine Learning and Systems, 6, 87–100. https://doi.org/10.48550/arXiv.2306.00978',
'Chen, L., et al. (2024). FastV: Efficient visual token pruning for large vision-language models. [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2403.06764',
]
last = doc.paragraphs[-1]
for ref in refs:
    last = after(last, ref, 'INTI-Reference')

doc.save(out)
print(out)

