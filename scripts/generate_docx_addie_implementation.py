import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os

doc = docx.Document()

# Setup Page Margin (Standar PENS: Kiri 4cm, Atas 3cm, Kanan 3cm, Bawah 3cm)
for section in doc.sections:
    section.top_margin = Inches(1.18)    # ~3 cm
    section.bottom_margin = Inches(1.18) # ~3 cm
    section.left_margin = Inches(1.57)   # ~4 cm
    section.right_margin = Inches(1.18)  # ~3 cm

# Styling Helper
def set_font(run, name='Times New Roman', size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_font(run, size=14, bold=True)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_font(run, size=12, bold=True)
    return p

def add_body_p(doc, text, bold_prefix=None, space_after=6, italic_terms=None):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_font(r_pre, size=12, bold=True)
    
    # Simple formatting if no special terms
    if not italic_terms:
        r = p.add_run(text)
        set_font(r, size=12)
    else:
        # Menjaga istilah asing tetap miring sesuai kaidah penulisan proposal TRM
        words = text.split(' ')
        for w in words:
            clean_w = w.strip('.,():;"')
            is_it = clean_w in italic_terms
            r = p.add_run(w + ' ')
            set_font(r, size=12, italic=is_it)
    return p

def add_bullet_p(doc, num_str, title, text, italic_terms=None):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r1 = p.add_run(num_str + '. ' + title + ': ')
    set_font(r1, size=12, bold=True)
    r2 = p.add_run(text)
    set_font(r2, size=12)
    return p

def add_caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_font(run, size=10, bold=True)
    return p

def add_image_centered(doc, path, width_in_inches=5.8):
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(path, width=Inches(width_in_inches))
    else:
        p = doc.add_paragraph(f'[Gambar tidak ditemukan: {path}]')

# Header Judul
p_title = doc.add_paragraph()
p_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(12)
p_title.paragraph_format.space_after = Pt(2)
r_b = p_title.add_run('BAB 3\nDESAIN SISTEM')
set_font(r_b, size=14, bold=True)

# Subbab Utama Sesuai Buku Proposal Asli
add_heading_1(doc, '3.3.4 Implementation')

# Paragraf 1 persis teks asli
add_body_p(doc, 'Tahap Implementation merupakan proses penerapan hasil pengembangan sistem ke dalam lingkungan operasional sehingga seluruh komponen yang telah dikembangkan dapat digunakan sebagai satu platform pembelajaran yang utuh.')

# Gambar 3.16 Diagram Implementasi Sistem MILO persis seperti di proposal halaman 56
add_image_centered(doc, 'buku/generated_diagrams/Gambar_3_16_Diagram_Implementasi_Sistem_MILO.png', 5.9)
add_caption(doc, 'Gambar 3.16 Diagram Implementasi Sistem MILO')

# Paragraf 2 persis teks asli
add_body_p(doc, 'Pada tahap ini dilakukan integrasi antara antarmuka pengguna (frontend), layanan backend, basis data, teknologi Artificial Intelligence (AI), avatar virtual, serta mekanisme gamifikasi sehingga sistem MILO (Multimodal Interactive Learning Companion) dapat digunakan oleh pengguna untuk melakukan latihan berbicara bahasa Inggris secara interaktif.')

# Paragraf 3 persis teks asli
add_body_p(doc, 'Pada tahap implementasi yang dijabarkan pada Gambar 3.16, pengguna akan mengakses sistem melalui aplikasi berbasis web kemudian melakukan autentikasi sebelum memulai sesi pembelajaran. Pengguna dapat memilih tujuan pembelajaran (learning goals) sesuai kebutuhan, kemudian berinteraksi dengan avatar virtual melalui masukan suara maupun teks. Masukan suara diproses menggunakan teknologi Automatic Speech Recognition (ASR), kemudian dianalisis oleh Large Language Model (LLM) dengan dukungan Retrieval-Augmented Generation (RAG) untuk menghasilkan respons percakapan dan umpan balik pembelajaran yang sesuai dengan konteks. Respons tersebut selanjutnya dikonversi menjadi suara menggunakan Text-to-Speech (TTS) dan ditampilkan melalui avatar virtual sehingga menciptakan pengalaman percakapan yang lebih natural.')

# Paragraf 4 persis teks asli
add_body_p(doc, 'Selama proses pembelajaran berlangsung, sistem juga mencatat aktivitas pengguna, hasil evaluasi, serta perkembangan kemampuan berbicara sebagai bagian dari mekanisme progress tracking. Selain itu, elemen gamifikasi seperti point, achievement badge, dan daily streak diterapkan untuk meningkatkan motivasi dan keterlibatan pengguna selama proses latihan berbicara. Implementasi sistem ini selanjutnya menjadi dasar pelaksanaan pengujian pada tahap Evaluation untuk menilai fungsionalitas sistem, pengalaman pengguna, serta tingkat student engagement yang dihasilkan.')

# Paragraf 5 persis teks asli
add_body_p(doc, 'Sebelum menggunakan MILO, responden diminta mengisi kuesioner student engagement berdasarkan media latihan speaking yang biasa mereka gunakan sebagai data awal (baseline). Selanjutnya responden menggunakan MILO selama beberapa sesi latihan berbicara. Selama penggunaan tersebut sistem merekam aktivitas pengguna seperti frekuensi latihan, durasi penggunaan, jumlah sesi yang diselesaikan, serta progres belajar. Setelah seluruh sesi selesai, responden kembali mengisi kuesioner student engagement untuk mengetahui perubahan tingkat keterlibatan belajar setelah menggunakan MILO.')

# Detail Tambahan Operasional ADDIE (Penerapan Lingkungan dan Layanan Nyata Sesuai Codebase Proyek)
add_heading_2(doc, '1. Penerapan Lingkungan Operasional Layanan (Runtime Ecosystem)')
add_body_p(doc, 'Guna merealisasikan alur pada Gambar 3.16 ke dalam lingkungan operasional nyata, seluruh komponen dihubungkan dan dijalankan dalam satu kesatuan runtime asinkron:')

add_bullet_p(doc, '1', 'Layanan Backend FastAPI (Port 8000)', 'Server aplikasi web dan REST API dijalankan menggunakan server ASGI Uvicorn untuk menangani transmisi audio wicara pengguna (16 kHz mono), token autentikasi JWT, serta isolasi data sesi belajar pengguna.')

add_bullet_p(doc, '2', 'Layanan AI Gateway Bifrost (Port 8080)', 'Kontainer Docker milo-bifrost-gateway diaktifkan sebagai proksi cerdas antara backend dengan model OpenAI (Whisper, GPT-4o-mini, TTS-1) untuk mengelola rate limiting 60 req/menit dan semantic cache lokal guna menjamin latensi rendah.')

add_bullet_p(doc, '3', 'Penyimpanan Relasional & Koleksi Vektor', 'Tabel basis data relasional SQLAlchemy ORM dioperasikan untuk mencatat riwayat percakapan dan gamifikasi, sedangkan ChromaDB memuat indeks vektor 1536-dimensi materi silabus CEFR B1–B2 untuk mendukung Retrieval-Augmented Generation (RAG).')

# Screenshot Praktik & Lip-sync
add_image_centered(doc, 'buku/screenshots/Gambar_3_13_LipSync_milo_live2d.png', 5.6)
add_caption(doc, 'Gambar 3.17 Tampilan Implementasi Ekstraksi Audio RMS dan Lip-sync Avatar Live2D')

add_image_centered(doc, 'buku/screenshots/Gambar_3_14_Recording_practice_js.png', 5.6)
add_caption(doc, 'Gambar 3.18 Tampilan Implementasi Perekaman Wicara Dual Mode pada Practice Studio')

# Tahapan 4 Fase Uji Coba Responden Sesuai Model ADDIE
add_heading_2(doc, '2. Prosedur Uji Coba Lapangan kepada Responden Mahasiswa')
add_body_p(doc, 'Sesuai dengan kerangka model ADDIE, penerapan sistem dilakukan kepada minimal 30 mahasiswa dengan rentang kemahiran CEFR B1–B2 melalui empat fase terstruktur:')

add_bullet_p(doc, 'Fase 1', 'Orientasi dan Pengambilan Data Baseline (Pre-test)', 'Responden mengisi kuesioner Student Engagement awal (meliputi dimensi behavioral, emotional, dan cognitive) serta survei speaking anxiety berdasarkan media latihan konvensional yang biasa digunakan.')

add_bullet_p(doc, 'Fase 2', 'Registrasi Akun dan Diagnostic Placement Test', 'Pengguna melakukan pembuatan akun dan mengikuti tes penempatan diagnostik wicara (setup-level.html) untuk memetakan level awal (B1 atau B2) dan rekomendasi topik microlearning.')

add_bullet_p(doc, 'Fase 3', 'Intervensi Latihan Percakapan Mandiri (3 hingga 5 Sesi)', 'Pengguna menjalankan sesi latihan berbicara interaktif berdurasi 3–5 menit bersama avatar Live2D melalui halaman briefing.html, practice.html, hingga meninjau umpan balik grammar pada summary.html. Seluruh data aktivitas dan giliran bicara terekam secara otomatis oleh sistem telemetri.')

add_bullet_p(doc, 'Fase 4', 'Pengambilan Data Post-test dan Evaluasi Pengalaman Pengguna', 'Responden mengisi kuesioner Student Engagement akhir (post-test) untuk mengukur peningkatan keterlibatan (N-Gain) serta kuesioner User Experience Questionnaire (UEQ) sebagai input untuk tahap Evaluation (3.3.5).')

add_image_centered(doc, 'buku/generated_diagrams/Gambar_3_17_Prosedur_Uji_Coba_Responden.png', 5.8)
add_caption(doc, 'Gambar 3.19 Prosedur Empat Fase Penerapan dan Uji Coba Operasional kepada Responden')

# Simpan Dokumen
output_file = 'buku/BAB_3_3_4_IMPLEMENTATION_ADDIE_MILO.docx'
doc.save(output_file)
print(f'Dokumen berhasil dibuat dan disimpan: {output_file}')
