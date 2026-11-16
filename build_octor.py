from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

out='[Octo-R] Penjelasan Mudah Chapter 2.docx'
doc=Document(); s=doc.sections[0]
s.top_margin=Inches(.7); s.bottom_margin=Inches(.7); s.left_margin=Inches(.85); s.right_margin=Inches(.85)
doc.styles['Normal'].font.name='Aptos'; doc.styles['Normal'].font.size=Pt(10.5)
doc.styles['Normal'].paragraph_format.space_after=Pt(6)
for name,size in [('Title',24),('Heading 1',16),('Heading 2',12.5)]:
    st=doc.styles[name]; st.font.name='Aptos'; st.font.size=Pt(size); st.font.bold=True; st.font.color.rgb=RGBColor(0,0,0)

def shade(cell,fill):
    pr=cell._tc.get_or_add_tcPr(); x=OxmlElement('w:shd'); x.set(qn('w:fill'),fill); pr.append(x)
def borders(table):
    pr=table._tbl.tblPr; b=OxmlElement('w:tblBorders')
    for e in ['top','left','bottom','right','insideH','insideV']:
        x=OxmlElement('w:'+e); x.set(qn('w:val'),'single'); x.set(qn('w:sz'),'4'); x.set(qn('w:color'),'D9D9D9'); b.append(x)
    pr.append(b)
def cell(c,text,bold=False,header=False):
    c.text=''; p=c.paragraphs[0]; r=p.add_run(text); r.bold=bold; r.font.size=Pt(9.5)
    if header: shade(c,'1F4E78'); r.font.color.rgb=RGBColor(255,255,255)
def bullets(items):
    for x in items: doc.add_paragraph(x,style='List Bullet')
def table(headers,rows):
    t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; borders(t)
    for c,x in zip(t.rows[0].cells,headers): cell(c,x,True,True)
    for row in rows:
        for c,x in zip(t.add_row().cells,row): cell(c,x)

p=doc.add_paragraph(style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Penjelasan Mudah Chapter 2')
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Literature Review untuk BLIP-3 dan Resource-Constrained VQA').italic=True
doc.add_paragraph('Dokumen pendamping ini menjelaskan Chapter 2 dalam bahasa Indonesia yang lebih sederhana. Fokusnya adalah memahami masalah penelitian, konsep teknis, research gap, dan hubungan teori dengan eksperimen.')

doc.add_heading('1. Inti Chapter 2',1)
doc.add_paragraph('Chapter 2 menjelaskan mengapa BLIP-3 yang besar perlu dikompresi agar dapat digunakan pada perangkat dengan sumber daya terbatas, serta mengapa pruning, quantization, dan kombinasi keduanya perlu dibandingkan berdasarkan akurasi dan efisiensi.')
doc.add_heading('2. Alur Besar Chapter 2',1)
table(['Tahap','Pertanyaan','Makna sederhana'],[
('Masalah','Mengapa VQA sulit dijalankan?','Model besar memerlukan banyak memory, waktu, dan daya komputasi.'),
('Model','Mengapa BLIP-3 dipilih?','Strukturnya modular dan dapat dianalisis per komponen.'),
('Solusi','Bagaimana model dibuat ringan?','Pruning menghapus struktur; quantization mengurangi presisi angka.'),
('Gap','Apa yang belum diketahui?','Belum jelas strategi terbaik untuk BLIP-3 dalam kondisi RCVQA.'),
('Kerangka','Bagaimana hasil dibandingkan?','Akurasi dibandingkan dengan latency, memory, dan model size.')])

doc.add_heading('3. Konsep Dasar',1)
doc.add_heading('3.1 VQA dan RCVQA',2)
doc.add_paragraph('Visual Question Answering atau VQA adalah tugas ketika model menerima gambar dan pertanyaan berbasis teks, lalu menghasilkan jawaban. Resource-Constrained VQA atau RCVQA adalah VQA yang harus berjalan dengan keterbatasan memory, processing power, storage, dan waktu respons.')
doc.add_paragraph('Kesimpulannya, model tidak cukup hanya akurat. Model juga harus praktis untuk dijalankan.')
doc.add_heading('3.2 Vision-Language Model',2)
doc.add_paragraph('Vision-Language Model atau VLM menggabungkan pemahaman gambar dan bahasa. Proses sederhananya adalah:')
bullets(['Visual encoder mengubah gambar menjadi fitur numerik.','Multimodal connector menghubungkan fitur gambar dengan bahasa.','Language model menggunakan gambar dan pertanyaan untuk menghasilkan jawaban.'])
doc.add_paragraph('Hubungan antara informasi visual dan teks disebut cross-modal alignment. Jika hubungan ini rusak akibat compression, model dapat memberikan jawaban yang terdengar benar tetapi tidak sesuai dengan gambar.')
doc.add_heading('3.3 Perkembangan BLIP',2)
table(['Model','Ide utama','Relevansi'],[
('BLIP','Menggabungkan pemahaman gambar dan generasi bahasa.','Dasar keluarga BLIP.'),
('BLIP-2','Menghubungkan visual encoder dan language model melalui Q-Former.','Lebih modular dan scalable.'),
('BLIP-3','Memiliki visual encoder, multimodal connector, dan language model.','Model utama penelitian dan cocok untuk analisis komponen.')])

doc.add_heading('4. Teknik Compression',1)
doc.add_heading('4.1 Quantization',2)
doc.add_paragraph('Quantization mengurangi jumlah bit untuk menyimpan bobot atau aktivasi model. Contohnya, nilai FP32 dapat direpresentasikan menggunakan INT8. Hasilnya, memory dapat berkurang dan inference berpotensi lebih cepat. Kekurangannya, pembulatan nilai dapat menyebabkan penurunan akurasi.')
doc.add_heading('4.2 Pruning',2)
doc.add_paragraph('Pruning menghapus bagian model yang kurang penting atau redundan. Structured pruning menghapus unit yang lebih besar, seperti channel, attention head, layer, atau token. Teknik ini relevan untuk deployment karena pengurangan struktur lebih mungkin menghasilkan pengurangan komputasi yang nyata.')
doc.add_heading('4.3 Combined Compression',2)
doc.add_paragraph('Combined compression menggunakan pruning dan quantization sekaligus. Pruning mengurangi jumlah struktur, sedangkan quantization mengurangi ukuran numerik dari bagian yang tersisa. Kombinasi ini mungkin lebih efisien, tetapi dapat menyebabkan penurunan akurasi atau masalah kalibrasi sehingga harus diuji secara empiris.')

doc.add_heading('5. Research Gap',1)
doc.add_paragraph('Literatur sebelumnya telah membahas VQA, VLM, BLIP, pruning, quantization, dan efficient deployment. Namun, terdapat tiga kekosongan utama:')
bullets(['Belum cukup bukti yang membandingkan pruning-only, quantization-only, dan combined compression pada BLIP-3 dalam kondisi eksperimen yang sama.','Belum jelas komponen BLIP-3 mana yang paling banyak menyumbang biaya komputasi dan paling sensitif terhadap compression.','Belum cukup penelitian yang menilai deployability berdasarkan accuracy, latency, memory usage, dan model size secara bersamaan.'])
doc.add_paragraph('Kontribusi penelitian ini bukan menciptakan teknik compression baru, tetapi mengevaluasi teknik yang sudah ada secara terkontrol pada BLIP-3 dalam skenario RCVQA.')

doc.add_heading('6. Theoretical Framework',1)
doc.add_heading('6.1 Lottery Ticket Hypothesis',2)
doc.add_paragraph('Teori ini mendukung gagasan bahwa jaringan neural besar mungkin memiliki bagian yang redundan. Jika bagian yang tidak penting dihapus, model mungkin tetap mempertahankan kemampuan utamanya. Ini menjadi alasan teoritis untuk menggunakan pruning.')
doc.add_heading('6.2 Efficiency–Accuracy Trade-off',2)
doc.add_paragraph('Efisiensi dan akurasi tidak selalu meningkat bersama. Model yang lebih kecil atau cepat mungkin kehilangan sebagian akurasi. Karena itu, penelitian mencari keseimbangan yang sesuai, bukan sekadar model paling kecil atau paling akurat.')
doc.add_heading('6.3 Resource Constraint Theory',2)
doc.add_paragraph('Model yang baik harus sesuai dengan batas perangkat tempat model dijalankan. Dalam penelitian ini, batas tersebut diterjemahkan menjadi memory, latency, model size, dan minimum accuracy.')

doc.add_heading('7. Conceptual Framework',1)
doc.add_paragraph('Hubungan antarvariabel dapat dibaca sebagai berikut:')
doc.add_paragraph('Compression strategy → perubahan struktur dan presisi → perubahan memory, latency, dan model size → perubahan VQA accuracy → keputusan deployability',style='Intense Quote')
table(['Elemen','Dalam penelitian'],[
('Variabel bebas','Pruning, quantization, dan combined compression.'),
('Variabel hasil','VQA accuracy, inference latency, GPU memory usage, dan model size.'),
('Analisis tambahan','Perbedaan sensitivity pada visual encoder, multimodal connector, dan language model.'),
('Hasil akhir','Konfigurasi BLIP-3 yang paling layak untuk RCVQA.')])

doc.add_heading('8. Cara Memahami Hipotesis',1)
doc.add_paragraph('Hipotesis adalah dugaan yang akan diuji, bukan hasil yang sudah pasti benar.')
bullets(['Compression diperkirakan menurunkan kebutuhan sumber daya.','Tingkat compression yang berbeda dapat menghasilkan tingkat penurunan akurasi yang berbeda.','Komponen BLIP-3 mungkin tidak memiliki sensitivitas yang sama.','Combined compression mungkin memberikan trade-off yang lebih baik, tetapi tetap harus dibuktikan.'])

doc.add_heading('9. Saran Perbaikan Chapter 2',1)
bullets(['Kurangi pengulangan tentang keterbatasan komputasi dan risiko penurunan akurasi.','Tambahkan tabel perbandingan penelitian terdahulu yang memuat model, metode, metrik, dan keterbatasan.','Pisahkan literature review dari detail metodologi seperti jumlah konfigurasi, jumlah sampel, dan computational budget.','Jelaskan research gap dalam tiga poin yang spesifik dan hubungkan langsung dengan research questions.','Gunakan istilah secara konsisten, terutama quantization atau quantisation, resource-constrained, dan vision-language.','Periksa kembali validitas, DOI, tahun publikasi, dan hubungan setiap referensi dengan klaim dalam teks.'])

doc.add_heading('10. Ringkasan untuk Presentasi',1)
doc.add_paragraph('Chapter 2 membahas kebutuhan menjalankan VQA pada perangkat dengan sumber daya terbatas. BLIP-3 dipilih karena memiliki visual encoder, multimodal connector, dan language model yang dapat dianalisis secara terpisah. Penelitian membandingkan pruning, quantization, dan kombinasi keduanya. Karena compression dapat meningkatkan efisiensi tetapi juga menurunkan akurasi, evaluasi mencakup VQA accuracy, latency, memory usage, model size, dan deployability. Research gap utamanya adalah kurangnya evaluasi terkontrol dan component-level analysis khusus untuk BLIP-3 dalam kondisi RCVQA.')
doc.add_heading('11. Lima Poin Wajib Diingat',1)
bullets(['RCVQA menilai kemampuan model dalam kondisi hardware yang terbatas.','BLIP-3 terdiri dari visual encoder, multimodal connector, dan language model.','Pruning menghapus struktur; quantization mengurangi presisi numerik.','Compression dapat meningkatkan efisiensi tetapi berisiko menurunkan akurasi.','Model terbaik adalah model yang memenuhi keseimbangan accuracy–efficiency dan batas deployability.'])
doc.add_paragraph('Dokumen ini merupakan panduan pemahaman dan tidak menggantikan teks akademik, sitasi, atau definisi formal dalam tesis.',style='Caption')
doc.save(out); print(out)
