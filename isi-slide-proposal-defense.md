# Isi Slide Proposal Defense

Panduan isi dan narasi berdasarkan dokumen **[Octo-R] Master_PD_Hafiz**. Slide dibuat oleh peneliti; dokumen ini berisi teks ringkas yang dapat dimasukkan ke slide dan poin yang disampaikan secara lisan.

> **Updated to proposal version [Octo-4].** Use the updated points below when they differ from the earlier draft. The new proposal includes a completed preliminary-results chapter, changes RO4 from “identify” to “recommend,” and provides structural baseline evidence for BLIP-3.

## Pembaruan utama versi Octo-4

- Proposal sekarang memiliki **Chapter 4 Preliminary Results**.
- Baseline BLIP-3 sudah dievaluasi pada **5,040 pertanyaan**.
- Baseline accuracy: **79.45%**, 95% CI **78.45–80.44**.
- Accuracy per answer type: **yes/no 92.37%**, **other 73.28%**, **number 66.13%**.
- Struktur model: language model **87.66% parameter**, visual encoder **9.82%**, connector **±2.52%**.
- Total parameter: **4,359,257,219**; BF16 weight footprint sekitar **8.12 GB**.
- Baseline peak allocated memory: **8.74 GB**; peak reserved memory: **8.96 GB**.
- Preliminary latency RTX 3090: mean **0.333 s**, SD **0.049 s**, throughput **3.01 queries/s**. Jelaskan bahwa ini masih preliminary dan akan diukur ulang dengan full timing protocol.
- Baseline tidak memenuhi memory threshold 8 GB dan model-size threshold 4 GB, walaupun accuracy retention baseline otomatis 100%.
- RO4 terbaru: **recommend** compressed configurations yang memenuhi kriteria deployability dan menentukan limiting criterion.
- Implementasi pruning dilakukan bertahap: language-model feed-forward channels, visual-encoder/connector channels, kemudian attention heads jika tervalidasi.

## Pesan utama presentasi

BLIP-3 memiliki kemampuan VQA yang kuat, tetapi kebutuhan memori, ukuran model, dan waktu inferensinya menyulitkan deployment pada hardware terbatas. Penelitian ini membandingkan pruning terstruktur, quantization INT8, dan kombinasi keduanya untuk menentukan trade-off efficiency–accuracy serta konfigurasi yang memenuhi kriteria deployment RCVQA.

## Slide 1 — Title

**Isi slide**

- A Compression Benchmarking Framework for Evaluating Efficiency–Accuracy Trade-offs in BLIP-3 for Resource-Constrained Visual Question Answering
- Hafiz Muhammad Kurniawan
- Student ID: I25037849
- Supervisor: [isi nama supervisor]
- Proposal Defense

**Sampaikan**

“Penelitian ini mengevaluasi apakah BLIP-3 dapat dikompresi agar lebih feasible untuk Visual Question Answering pada hardware dengan sumber daya terbatas, tanpa kehilangan akurasi secara berlebihan.”

## Slide 2 — Background

**Isi slide**

- VQA menggabungkan pemahaman gambar dan pertanyaan bahasa alami.
- VLM modern meningkatkan kemampuan VQA melalui arsitektur multimodal berskala besar.
- BLIP-3 menggabungkan tiga komponen utama: visual encoder, multimodal connector, dan language model.
- Skala model meningkatkan kebutuhan GPU memory, storage, dan inference time.
- Benchmark accuracy saja belum cukup untuk menunjukkan kesiapan deployment.

**Visual yang disarankan**

Alur: `Image + Question → BLIP-3 → Answer`, kemudian tambahkan tiga indikator biaya: memory, latency, model size.

**Sampaikan**

“Masalah yang saya angkat bukan hanya apakah model menjawab dengan benar, tetapi apakah model tersebut dapat dijalankan secara praktis pada sistem consumer-grade.”

## Slide 3 — Problem Statement

**Isi slide**

**Deployment gap:** model VQA kuat pada lingkungan komputasi tinggi, tetapi belum tentu feasible pada hardware terbatas.

Empat celah yang ditemukan:

1. Pruning dan quantization jarang dibandingkan untuk BLIP-3 dalam satu lingkungan terkontrol.
2. Perilaku efficiency–accuracy BLIP-3 pada batas consumer-grade belum cukup diketahui.
3. Sensitivitas visual encoder, multimodal connector, dan language model belum dibandingkan secara komponen.
4. Deployment jarang dinilai secara bersamaan menggunakan accuracy, latency, memory, dan model size dengan threshold eksplisit.

**Sampaikan**

“Jadi, research problem ini merupakan integration and deployment-evaluation gap, bukan ketiadaan teknik compression.”

## Slide 4 — Research Questions and Objectives

**Isi slide**

| RQ | Research Question | Objective |
|---|---|---|
| RQ1 | Apa dampak pruning dan INT8 quantization terhadap memory, latency, model size, dan accuracy? | RO1: Mengukur perubahan empat metrik tersebut. |
| RQ2 | Bagaimana perbedaan kontribusi biaya dan sensitivitas pruning antar-komponen BLIP-3? | RO2: Membandingkan visual encoder, connector, dan language model. |
| RQ3 | Apakah kombinasi compression lebih favorable dibanding teknik tunggal? | RO3: Membandingkan combined, pruning-only, dan quantization-only. |
| RQ4 | Konfigurasi mana yang memenuhi kriteria deployability dan apa batasan terbesarnya? | RO4: Menentukan konfigurasi deployable dan limiting criterion. |

**Sampaikan**

“RQ1 sampai RQ4 memiliki urutan logis: mengukur dampak umum, menemukan komponen sensitif, membandingkan kombinasi, lalu mengambil keputusan deployment.”

## Slide 5 — Literature Comparison

**Isi slide**

| Studi | Fokus | Keterbatasan terhadap penelitian ini |
|---|---|---|
| Rashid et al. (2024) | Compact multimodal network untuk tiny devices | Bukan compression pada large pretrained VLM atau BLIP-3. |
| Mishra et al. (2024) | Post-training quantization untuk VQA embedded | Bukan BLIP-family; tidak membahas pruning dan analisis komponen. |
| Zeng et al. (2025) | Dynamic visual-token pruning | Mengurangi token input, bukan ukuran stored model. |
| Li et al. (2026) | Joint quantization dan visual-token pruning | Bukan BLIP-3; tidak memakai component analysis dan threshold deployment eksplisit. |
| Elluru et al. (2026) | Mekanisme internal compression pada VLM | Fokus pada circuit dan safety, bukan deployment feasibility. |

**Sampaikan**

“Literatur sudah membuktikan bahwa teknik individualnya relevan, tetapi belum memberikan evaluasi terpadu untuk BLIP-3 dengan kondisi, data, hardware, dan threshold yang sama.”

## Slide 6 — Research Gap and Contribution

**Isi slide**

### Research gap

- Belum ada perbandingan terkendali antara pruning-only, quantization-only, dan combined compression pada BLIP-3.
- Belum diketahui komponen BLIP-3 yang paling sensitif terhadap structured pruning.
- Belum banyak studi yang menggunakan empat threshold deployment secara simultan.

### Kontribusi penelitian

- Compression benchmark yang reproducible untuk BLIP-3.
- Component-level sensitivity analysis.
- Perbandingan efficiency–accuracy dengan Pareto analysis.
- Keputusan deployability berbasis threshold eksplisit, bukan hanya compression ratio.

**Sampaikan**

“Kontribusi utama bukan menciptakan algoritma compression baru, tetapi menghasilkan evaluasi yang terkontrol dan berorientasi deployment.”

## Slide 7 — BLIP-3 and Compression Techniques

**Isi slide**

### BLIP-3

- Visual encoder: mengekstrak representasi visual.
- Multimodal connector: menghubungkan representasi visual dengan language model.
- Language model: menghasilkan jawaban berdasarkan representasi multimodal.

### Compression

- Structured pruning: menghapus unit lengkap seperti attention heads atau feed-forward channels.
- INT8 weight-only PTQ: weight disimpan dalam 8-bit, activation tetap 16-bit (W8A16).
- Combined: 30% full-model pruning, kemudian INT8 quantization.

**Catatan penting**

- Pruning mengurangi struktur dan parameter.
- Quantization mengurangi precision penyimpanan.
- Latency tidak diasumsikan selalu menurun; efeknya diukur empiris karena bergantung pada backend dan hardware.

## Slide 8 — Theoretical and Conceptual Framework

**Isi slide**

### Theoretical framework

1. Lottery Ticket Hypothesis / model redundancy → compression layak diuji.
2. Efficiency–accuracy trade-off → savings harus dinilai bersama accuracy loss.
3. Resource-constraint perspective → deployment bergantung pada batas hardware.

### Conceptual framework

`Compression strategy + compression target`

→ `Model size, latency, peak memory`

→ `VQA accuracy and accuracy retention`

→ `Pareto position and deployability decision`

**Variabel kontrol**

Checkpoint, data, preprocessing, prompt, decoding, hardware, software, dan measurement protocol dibuat tetap.

## Slide 9 — Hypotheses

**Isi slide**

- **H1:** Structured pruning dan post-training quantization mengurangi model size serta peak GPU memory; accuracy retention menurun ketika pruning intensity meningkat. Dampak latency ditentukan secara empiris.
- **H2:** Visual encoder, multimodal connector, dan language model berbeda dalam computational contribution serta pruning sensitivity.
- **H3:** Combined pruning dan quantization menghasilkan efficiency–accuracy profile yang berbeda dari pruning-only dan quantization-only. Keunggulan ditentukan melalui Pareto dan deployability, bukan diasumsikan.
- **RQ4:** Dijawab secara deskriptif melalui deployability classification; tidak memiliki hipotesis.

**Sampaikan**

“Saya sengaja tidak mengasumsikan INT8 pasti mempercepat inference atau combined compression pasti paling baik, karena kedua hasil tersebut bergantung pada model, hardware, dan backend.”

## Slide 10 — Research Design

**Isi slide**

### Controlled quantitative comparative experiment

- Satu checkpoint BLIP-3.
- Satu fixed stratified subset VQAv2.
- Decoding, preprocessing, hardware, software, dan measurement protocol dibuat sama.
- Tanpa retraining atau fine-tuning setelah compression.

### Dua jalur eksperimen

1. **Component-level track:** pruning satu komponen pada satu waktu untuk mengukur sensitivity.
2. **Full-model track:** semua komponen dipruning bersama untuk mengukur trade-off dan deployment.

### 15 konfigurasi

- BASE: 1
- Component-level: VE-10/20/30, MC-10/20/30, LM-10/20/30 = 9
- Full-model pruning: FP-10/20/30 = 3
- Quantization-only: Q-INT8 = 1
- Combined: FP30-INT8 = 1

## Slide 11 — Compression Procedures

**Isi slide**

### Structured pruning

- Level pruning: 10%, 20%, dan 30%.
- Target: attention heads dan feed-forward channels yang eligible.
- Importance diestimasi dari calibration subset.
- Pruning dilakukan secara fisik sehingga weight matrix menjadi lebih kecil.

### INT8 W8A16

- Diterapkan pada linear layers ketiga komponen.
- Per-channel symmetric round-to-nearest quantization.
- Activation tetap BF16/16-bit.
- Normalization, token embedding, LM output head, dan patch embedding tetap BF16.

### Combined

- Full-model pruning 30% terlebih dahulu.
- Quantization INT8 diterapkan setelah arsitektur akhir terbentuk.
- Tidak ada retraining di antara atau setelah kedua tahap.

## Slide 12 — Dataset and Sampling

**Isi slide**

- Dataset: VQAv2 validation set, 214,354 questions.
- Tiga answer type resmi: yes/no, number, other.
- Fixed proportional stratified sampling; random seed = 42.

| Subset | Ukuran | Kegunaan |
|---|---:|---|
| Evaluation | 5,040 | Accuracy semua konfigurasi |
| Timing | 500 | Latency dan memory benchmarking |
| Calibration | 256 | Estimasi pruning importance; bukan untuk evaluasi performa |

**Sampaikan**

“Semua konfigurasi menggunakan question identifiers yang sama. Dengan demikian, perbedaan difficulty data tidak disalahartikan sebagai efek compression.”

## Slide 13 — Metrics and Measurement

**Isi slide**

### Accuracy

- Official VQAv2 accuracy.
- Accuracy per answer type.
- Accuracy retention: compressed accuracy / baseline accuracy.

### Efficiency

- Mean inference latency, batch size 1.
- Peak allocated GPU memory.
- On-disk model size.
- Throughput dan parameter count sebagai metrik tambahan.

### Timing protocol

- 10 warm-up runs.
- 3 synchronized passes.
- Timing subset: 500 questions.
- Semua konfigurasi dibandingkan pada RTX 3090.
- Kandidat yang lolos memory, size, dan accuracy diverifikasi pada GPU consumer 8 GB.

## Slide 14 — Data Analysis

**Isi slide**

1. Hitung accuracy, answer-type accuracy, accuracy retention, latency, memory, dan model size.
2. Gunakan paired bootstrap dengan 10,000 resamples untuk 95% confidence interval.
3. Nilai deployability dengan empat threshold yang harus dipenuhi bersamaan.
4. Hitung relative shortfall untuk menentukan limiting criterion.
5. Lakukan Pareto analysis: accuracy dimaksimalkan; latency, memory, dan size diminimalkan.
6. Kandidat terbaik adalah konfigurasi yang deployable dan Pareto-nondominated.

**Catatan**

Pareto-nondominated tidak otomatis berarti deployable. Keduanya dilaporkan sebagai dua konsep yang berbeda.

## Slide 15 — Feasibility, Ethics and Risks

**Isi slide**

### Feasibility

- Baseline accuracy awal: 79.45% (95% CI: 78.45–80.44).
- Baseline answer type: yes/no 92.37%, other 73.28%, number 66.13%.
- Baseline peak allocated memory awal: 8.74 GB.
- Estimasi total: 20–40 GPU-hours.
- Estimasi biaya: sekitar US$3–US$9, tidak termasuk data transfer.
- Persistent storage: sekitar 100 GB.

### Risiko dan mitigasi

- Quantization/pruning tidak kompatibel → pilot test dan contingency procedure.
- Variasi latency → warm-up, repeated synchronized passes, satu host untuk efficiency session.
- Perubahan library/checkpoint → pin version dan checkpoint revision.
- Kehilangan data → persistent storage, backup, checksum.

### Ethics

- Dataset publik dan tidak melibatkan pengumpulan data pribadi baru.
- Tidak ada human subject intervention.
- Hasil dibatasi pada checkpoint, dataset, hardware, dan threshold yang didefinisikan.

## Slide 16 — Expected Results

**Isi slide**

| RQ | Expected output |
|---|---|
| RQ1 | Perubahan memory, latency, model size, accuracy, dan accuracy retention untuk pruning serta INT8. |
| RQ2 | Komponen dengan computational share dan pruning sensitivity berbeda, berdasarkan absolute dan parameter-normalized sensitivity. |
| RQ3 | Profil empiris FP30-INT8 dibandingkan dengan FP-30 dan Q-INT8. |
| RQ4 | Daftar konfigurasi deployable, Pareto-nondominated, serta criterion yang paling membatasi. |

**Anticipated interpretation**

- Model-size criterion diperkirakan lebih ketat daripada memory criterion.
- INT8 belum tentu cukup untuk mencapai batas model size 4 GB.
- Jika pruning menghasilkan accuracy loss besar, hal tersebut menunjukkan kemungkinan perlunya recovery fine-tuning pada penelitian lanjutan.
- Ini adalah expected outcomes, bukan hasil final yang sudah diklaim.

## Slide 17 — Limitations

**Isi slide**

- Hanya satu BLIP-3 checkpoint.
- Hanya satu dataset dan subset VQAv2.
- Hanya post-training compression; tidak ada recovery fine-tuning.
- Pruning percentage seragam dan belum tentu optimal untuk setiap layer.
- Latency deployment diverifikasi pada satu GPU consumer 8 GB.
- Hasil dipengaruhi oleh quantization backend, hardware, dan software version.
- Threshold deployment merepresentasikan satu skenario studi, bukan standar universal.

**Sampaikan**

“Keterbatasan ini membatasi generalisasi, tetapi sekaligus menjaga eksperimen tetap terkontrol, reproducible, dan feasible dalam lingkup penelitian.”

## Slide 18 — Contributions and Conclusion

**Isi slide**

### Kontribusi teoretis

- Menghubungkan model redundancy, efficiency–accuracy trade-off, dan resource constraints dalam konteks RCVQA.

### Kontribusi metodologis

- Controlled benchmark untuk 15 konfigurasi BLIP-3.
- Component-level sensitivity analysis.
- Paired bootstrap, explicit deployment thresholds, dan Pareto analysis.

### Kontribusi praktis

- Panduan berbasis bukti untuk memilih konfigurasi BLIP-3 pada hardware terbatas.
- Identifikasi bottleneck deployment: memory, latency, model size, atau accuracy retention.

### Kesimpulan

“Penelitian ini akan menentukan bukan hanya seberapa banyak BLIP-3 dapat dikompresi, tetapi konfigurasi mana yang memberikan trade-off paling masuk akal dan apakah konfigurasi tersebut benar-benar memenuhi batas deployment RCVQA.”

## Daftar angka yang perlu konsisten di semua slide

- 15 konfigurasi total.
- 5,040 evaluation questions.
- 500 timing questions.
- 256 calibration questions.
- Pruning: 10%, 20%, 30%.
- INT8 weight-only: W8A16.
- Deployability: memory ≤ 8 GB; latency ≤ 2.0 s; model size ≤ 4 GB; accuracy retention ≥ 90%.
- Baseline preliminary accuracy: 79.45%.
- Baseline preliminary peak memory: 8.74 GB.
- Measurement GPU: RTX 3090 24 GB.
- Verification GPU: consumer GPU 8 GB.

## Penyesuaian poin slide berdasarkan Octo-4

Gunakan penyesuaian berikut pada slide yang sudah disusun sebelumnya.

### Slide 3 — Problem Statement

Tambahkan bukti baseline:

- BLIP-3 baseline membutuhkan **8.74 GB peak allocated memory**, melebihi batas 8 GB.
- BF16 weights berukuran sekitar **8.12 GB**, sekitar dua kali batas model-size 4 GB.
- Artinya, baseline memiliki kemampuan VQA yang baik tetapi belum langsung deployable pada skenario RCVQA yang didefinisikan.

### Slide 4 — RQ and RO

Perbarui RO4 menjadi:

> “To recommend the compressed configurations that satisfy the RCVQA deployability criteria and to determine the most limiting criterion for those that do not.”

Pada saat presentasi, tekankan bahwa RQ4 menghasilkan **recommendation berbasis bukti**, bukan hanya daftar konfigurasi.

### Slide 7 — BLIP-3 Architecture

Tambahkan structural evidence dari preliminary probe:

- Visual encoder: **428.2 million parameters / 9.82%**.
- Multimodal connector: **approximately 109.9 million / approximately 2.52%**.
- Language model: **3,821.1 million / 87.66%**.

Pesan utama: pruning percentage yang sama akan menghapus jumlah parameter yang sangat berbeda antar-komponen, sehingga perlu absolute dan parameter-normalized sensitivity.

### Slide 10 — Research Design

Tambahkan status pelaksanaan:

- Baseline phase: **completed**.
- Main compression experiments: **planned for the next stages**.
- Lima belas konfigurasi tetap dievaluasi: 1 baseline + 14 compressed configurations.

Jangan mengatakan semua hasil eksperimen sudah tersedia; yang sudah selesai di proposal ini adalah baseline dan validasi pipeline.

### Slide 11 — Compression Procedures

Tambahkan alasan staged pruning:

- Phi-3 language model menggunakan fused QKV dan gate-up projections.
- Head dimension harus dipertahankan pada 96.
- Karena itu, feed-forward channels dikerjakan lebih dahulu sebelum attention heads.
- Setiap konfigurasi harus lulus forward-pass validation sebelum evaluasi.

### Slide 13 — Metrics and Measurement

Pisahkan hasil awal dari protokol utama:

- **Preliminary baseline:** mean latency 0.333 s pada RTX 3090, satu pass pada 500 pertanyaan pertama.
- **Main experiment protocol:** frozen timing subset 500 questions, 10 warm-up runs, 3 synchronized timed passes, semua 15 konfigurasi dalam satu efficiency session dan satu host.
- Latency pada RTX 3090 digunakan untuk perbandingan terkendali; deployability latency dikonfirmasi pada GPU consumer 8 GB.

### Slide 15 — Feasibility, Ethics and Risks

Ubah judul kecil “Preliminary evidence” menjadi:

- Pipeline validated on the frozen evaluation subset.
- Semua 5,040 pertanyaan menghasilkan scored response.
- Pilot predictions direproduksi secara deterministik.
- Hanya **8 respons (0.16%)** yang lebih panjang dari tiga kata pada baseline.

Tambahkan risiko teknis yang spesifik:

- Fused projection matrices dapat menyebabkan tensor-shape mismatch setelah pruning.
- Quantization backend dapat menaikkan latency.
- Compressed model dapat menghasilkan respons lebih panjang sehingga accuracy turun karena format, bukan kemampuan visual.

### Slide 16 — Expected Results

Bedakan secara tegas:

**Sudah diketahui dari preliminary results**

- Baseline accuracy dan confidence interval.
- Distribusi accuracy per answer type.
- Baseline memory dan preliminary latency.
- Baseline gagal pada memory dan model-size criteria.

**Belum diketahui dan akan diuji**

- Konfigurasi compression yang paling efektif.
- Komponen paling sensitif.
- Apakah combined compression lebih favorable.
- Konfigurasi mana yang memenuhi semua empat criteria.

### Slide 18 — Contributions and Conclusion

Gunakan conclusion terbaru:

> “The study begins from a validated BLIP-3 baseline that is accurate but exceeds the defined memory and model-size limits. The main experiments will determine whether structured pruning, INT8 quantization, or their combination can close this deployment gap while retaining at least 90% accuracy.”

Kontribusi praktis sebaiknya menggunakan kata **recommend** dan **evidence-based deployment choice**, bukan menjanjikan bahwa model pasti deployable.

## Catatan presentasi

- Jangan menaruh seluruh narasi di slide; gunakan slide sebagai visual cue.
- Utamakan satu pesan utama per slide.
- Saat menjelaskan hasil yang belum ada, gunakan istilah “expected”, “will be evaluated”, atau “the study will determine”.
- Bedakan jelas antara measurement platform RTX 3090 dan verification platform 8 GB.
- Jangan menyatakan INT8 pasti mempercepat latency.
- Jangan menyatakan combined compression pasti terbaik sebelum Pareto analysis selesai.

## Image prompts untuk membangun visual slide

Gunakan gaya umum berikut pada semua prompt: **“clean academic presentation infographic, modern deep-tech visual language, dark navy and electric blue palette with teal accents, white background or subtle navy gradient, minimal text, high contrast, professional research proposal defense, 16:9 widescreen composition, no watermark, no random logos, no misspelled text.”**

Untuk hasil yang lebih aman, gunakan AI image generation untuk membuat visual tanpa teks, kemudian tambahkan label, angka, dan caption langsung di PowerPoint.

### Slide 1 — Title

**Prompt:**

“Abstract visual of a multimodal AI system answering a question about an image, glowing image panel connected to language tokens and a compact neural network, subtle compression motif with neatly reduced layers, elegant academic technology atmosphere, large clean negative space on the left for title text, visual emphasis on the right, clean academic presentation infographic, 16:9.”

### Slide 2 — Background

**Prompt:**

“Conceptual academic infographic showing the evolution from Visual Question Answering to Vision–Language Models to a large BLIP-3 style multimodal model, image and question entering a neural architecture, three visual cost indicators represented by GPU memory, storage drive, and response clock, clear left-to-right progression, no text labels, 16:9.”

### Slide 3 — Problem Statement

**Prompt:**

“Split-screen contrast: powerful multimodal AI model running in a large data center on the left, the same model struggling to fit on a small consumer GPU and laptop on the right, visual metaphor of a deployment gap, four subtle warning symbols for memory, latency, model size, and accuracy, serious research tone, no text, 16:9.”

### Slide 4 — Research Questions and Objectives

**Prompt:**

“Minimal research roadmap infographic with four connected stages represented by magnifying glass, component analysis, comparison scales, and deployment checkmark, flowing from research questions to objectives to final deployment decision, balanced academic layout with open space for a table, no text, 16:9.”

### Slide 5 — Literature Comparison

**Prompt:**

“Academic literature landscape visualization: several research papers and study nodes arranged around a central BLIP-3 compression benchmark, each node represented by a different visual symbol for quantization, token pruning, embedded VQA, and mechanistic analysis, central gap highlighted subtly, clean scholarly infographic, no readable text, 16:9.”

### Slide 6 — Research Gap and Contribution

**Prompt:**

“Three-column research gap and contribution concept: isolated compression methods on the left, missing component-level comparison in the center, integrated BLIP-3 deployment benchmark on the right, arrows converging into one complete framework, visual metaphor of puzzle pieces becoming a unified system, no text, 16:9.”

### Slide 7 — BLIP-3 and Compression Techniques

**Prompt:**

“Clean technical architecture diagram of a BLIP-3-like multimodal model with three modular blocks: visual encoder, multimodal connector, and language model, show structured pruning as removing complete internal blocks and INT8 quantization as converting weight symbols into compact 8-bit representations, clear modular design, no text labels, 16:9.”

### Slide 8 — Theoretical and Conceptual Framework

**Prompt:**

“Layered conceptual framework infographic: model redundancy at the top, efficiency–accuracy trade-off in the middle, resource constraints at the bottom, all connected to a final deployability decision, use concentric layers and directional arrows, elegant academic systems-thinking visual, no text, 16:9.”

### Slide 9 — Hypotheses

**Prompt:**

“Three hypothesis pathways shown as scientific experiment branches: compression intensity versus resource savings and accuracy, component sensitivity comparison, and combined pruning plus quantization versus single techniques, each pathway ending in an empirical measurement symbol rather than a predetermined winner, no text, 16:9.”

### Slide 10 — Research Design

**Prompt:**

“Experimental design flowchart visual with two parallel tracks: component-level experiments and full-model experiments, branching into multiple model configurations and converging into common evaluation metrics, reproducible controlled laboratory setup, clean geometric infographic, no text, 16:9.”

### Slide 11 — Compression Procedures

**Prompt:**

“Technical process visualization showing three compression procedures side by side: structured pruning removing neural network channels and attention heads, INT8 weight-only quantization transforming high-precision weights into compact integer blocks, and combined pruning followed by quantization, precise engineering style, no text, 16:9.”

### Slide 12 — Dataset and Sampling

**Prompt:**

“Dataset sampling infographic based on a large collection of image-question cards being proportionally divided into three fixed groups: evaluation, timing, and calibration, use balanced visual clusters and a subtle random-seed lock icon, emphasize reproducible stratified sampling, no text, 16:9.”

### Slide 13 — Metrics and Measurement

**Prompt:**

“Four-metric measurement dashboard visual for a multimodal model: accuracy target, GPU memory gauge, inference latency stopwatch, and on-disk model size storage icon, all connected to the same BLIP-3 model under controlled timing, clean technical dashboard aesthetic with space for metric table, no text, 16:9.”

### Slide 14 — Data Analysis

**Prompt:**

“Research analytics visualization combining bootstrap resampling distributions, confidence interval bars, a four-threshold deployment gate, and a Pareto frontier scatter plot comparing accuracy against efficiency, sophisticated but uncluttered academic data-science infographic, no text, 16:9.”

### Slide 15 — Feasibility, Ethics and Risks

**Prompt:**

“Responsible research feasibility visual: twelve-week timeline, GPU hour and storage resource icons, shield symbols for ethics and reproducibility, risk–mitigation arrows for software failure, hardware variation, and data loss, professional project planning infographic, no text, 16:9.”

### Slide 16 — Expected Results

**Prompt:**

“Expected-results visualization showing several compressed model candidates moving through four deployment gates: memory, latency, model size, and accuracy retention, some candidates passing and some stopping at different gates, ending with a Pareto frontier of promising configurations, no text, 16:9.”

### Slide 17 — Limitations

**Prompt:**

“Academic limitations visual represented by a controlled laboratory experiment inside a clearly bounded frame, with subtle boundary markers for one checkpoint, one dataset, one verification GPU, one backend, and no fine-tuning, honest and restrained research tone, no warning-heavy design, no text, 16:9.”

### Slide 18 — Contributions and Conclusion

**Prompt:**

“Final synthesis visual: three streams labeled conceptually as theoretical, methodological, and practical contribution converge into a deployable compressed multimodal model, balanced scales showing accuracy preserved while resource demand decreases, confident but scientifically cautious closing image, open space for conclusion text, no text, 16:9.”

## Negative prompt umum

“photorealistic people, generic business meeting, cartoon style, excessive neon, cluttered UI, tiny unreadable labels, fake citations, random letters, misspelled words, watermark, brand logos, overly decorative background, low contrast, distorted neural network, 3D text.”
