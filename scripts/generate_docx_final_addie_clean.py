import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os

doc = docx.Document()

# ==========================================
# 1. SETUP PAGE MARGIN STANDAR RESMI PENS TRM
# Kiri: 4.0 cm (1.57 inci)
# Atas: 3.0 cm (1.18 inci)
# Kanan: 3.0 cm (1.18 inci)
# Bawah: 3.0 cm (1.18 inci)
# ==========================================
for section in doc.sections:
    section.top_margin = Inches(1.18)
    section.bottom_margin = Inches(1.18)
    section.left_margin = Inches(1.57)
    section.right_margin = Inches(1.18)
    section.page_width = Inches(8.27)   # A4
    section.page_height = Inches(11.69) # A4

# ==========================================
# 2. STYLING HELPERS
# ==========================================
COLOR_BLACK = RGBColor(0, 0, 0)
COLOR_DARK = RGBColor(30, 41, 59)
COLOR_PRIMARY = RGBColor(64, 126, 121) # Soft Deep Teal (#407E79)

def set_font(run, name='Times New Roman', size=12, bold=False, italic=False, color=COLOR_BLACK):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color

def add_bab_header(doc, bab_text, title_text):
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    
    r1 = p.add_run(bab_text + '\n')
    set_font(r1, size=14, bold=True)
    r2 = p.add_run(title_text)
    set_font(r2, size=14, bold=True)
    return p

def add_heading_subbab(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, size=12, bold=True)
    return p

def add_heading_subsubbab(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, size=12, bold=True)
    return p

def add_paragraph_justify(doc, text, bold_prefix=None, space_after=6, first_line_indent=0.39):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if first_line_indent:
        p.paragraph_format.first_line_indent = Inches(first_line_indent) # ~1 cm indent
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_font(r_pre, size=12, bold=True)
        
    r = p.add_run(text)
    set_font(r, size=12)
    return p

def add_bullet_numbered(doc, num_str, title, text):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Inches(0.39)
    p.paragraph_format.first_line_indent = Inches(-0.39)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    r_num = p.add_run(num_str + ' ')
    set_font(r_num, size=12, bold=True)
    
    r_title = p.add_run(title + ': ')
    set_font(r_title, size=12, bold=True)
    
    r_text = p.add_run(text)
    set_font(r_text, size=12)
    return p

def add_figure_image(doc, path, caption_text, width_in_inches=5.6):
    if os.path.exists(path):
        p_img = doc.add_paragraph()
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.keep_with_next = True
        run_img = p_img.add_run()
        run_img.add_picture(path, width=Inches(width_in_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cap = p_cap.add_run(caption_text)
        set_font(run_cap, size=10, bold=True)
    else:
        p_err = doc.add_paragraph(f'[Gambar tidak ditemukan: {path}]')
        p_err.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ==========================================
# 3. KONTEN DOKUMEN SESUAI PROPOSAL ASLI
# ==========================================

# Judul Bab
add_bab_header(doc, 'BAB 3', 'DESAIN SISTEM')

# Subbab 3.3.4
add_heading_subbab(doc, '3.3.4 Implementation')

# Paragraf 1 (Persis Buku Proposal Hal 55)
add_paragraph_justify(doc, 
    'Tahap Implementation merupakan proses penerapan hasil pengembangan sistem ke dalam lingkungan operasional '
    'sehingga seluruh komponen yang telah dikembangkan dapat digunakan sebagai satu platform pembelajaran yang utuh.'
)

# Gambar 3.16 Diagram Implementasi Sistem MILO (Persis Buku Proposal Hal 56)
add_figure_image(doc, 
    'buku/generated_diagrams/Gambar_3_16_Diagram_Implementasi_Sistem_MILO.png', 
    'Gambar 3.16 Diagram Implementasi Sistem MILO', 
    width_in_inches=5.8
)

# Paragraf 2 (Persis Buku Proposal Hal 56)
add_paragraph_justify(doc, 
    'Pada tahap ini dilakukan integrasi antara antarmuka pengguna (frontend), layanan backend, basis data, '
    'teknologi Artificial Intelligence (AI), avatar virtual, serta mekanisme gamifikasi sehingga sistem MILO '
    '(Multimodal Interactive Learning Companion) dapat digunakan oleh pengguna untuk melakukan latihan berbicara '
    'bahasa Inggris secara interaktif.'
)

# Paragraf 3 (Persis Buku Proposal Hal 56)
add_paragraph_justify(doc, 
    'Pada tahap implementasi yang dijabarkan pada Gambar 3.16, pengguna akan mengakses sistem melalui aplikasi berbasis web '
    'kemudian melakukan autentikasi sebelum memulai sesi pembelajaran. Pengguna dapat memilih tujuan pembelajaran (learning goals) '
    'sesuai kebutuhan, kemudian berinteraksi dengan avatar virtual melalui masukan suara maupun teks. Masukan suara diproses '
    'menggunakan teknologi Automatic Speech Recognition (ASR), kemudian dianalisis oleh Large Language Model (LLM) dengan '
    'dukungan Retrieval-Augmented Generation (RAG) untuk menghasilkan respons percakapan dan umpan balik pembelajaran yang sesuai '
    'dengan konteks. Respons tersebut selanjutnya dikonversi menjadi suara menggunakan Text-to-Speech (TTS) dan ditampilkan melalui '
    'avatar virtual sehingga menciptakan pengalaman percakapan yang lebih natural.'
)

# Paragraf 4 (Persis Buku Proposal Hal 57)
add_paragraph_justify(doc, 
    'Selama proses pembelajaran berlangsung, sistem juga mencatat aktivitas pengguna, hasil evaluasi, serta perkembangan '
    'kemampuan berbicara sebagai bagian dari mekanisme progress tracking. Selain itu, elemen gamifikasi seperti point, '
    'achievement badge, dan daily streak diterapkan untuk meningkatkan motivasi dan keterlibatan pengguna selama proses latihan '
    'berbicara. Implementasi sistem ini selanjutnya menjadi dasar pelaksanaan pengujian pada tahap Evaluation untuk menilai '
    'fungsionalitas sistem, pengalaman pengguna, serta tingkat student engagement yang dihasilkan.'
)

# Paragraf 5 (Persis Buku Proposal Hal 57)
add_paragraph_justify(doc, 
    'Sebelum menggunakan MILO, responden diminta mengisi kuesioner student engagement berdasarkan media latihan speaking '
    'yang biasa mereka gunakan sebagai data awal (baseline). Selanjutnya responden menggunakan MILO selama beberapa sesi latihan '
    'berbicara. Selama penggunaan tersebut sistem merekam aktivitas pengguna seperti frekuensi latihan, durasi penggunaan, jumlah '
    'sesi yang diselesaikan, serta progres belajar. Setelah seluruh sesi selesai, responden kembali mengisi kuesioner student '
    'engagement untuk mengetahui perubahan tingkat keterlibatan belajar setelah menggunakan MILO.'
)

# ------------------------------------------
# A. Integrasi Lingkungan Operasional Nyata
# ------------------------------------------
add_heading_subsubbab(doc, 'A. Integrasi Lingkungan Operasional Layanan (Runtime Ecosystem)')

add_paragraph_justify(doc, 
    'Guna merealisasikan seluruh alur pemrosesan pada Gambar 3.16 ke dalam lingkungan uji operasional nyata, seluruh komponen '
    'perangkat lunak diintegrasikan dan dijalankan dalam satu kesatuan runtime asinkron terdistribusi:'
)

add_bullet_numbered(doc, '1.', 'Layanan Backend FastAPI & Antarmuka Web (Port 8000)', 
    'Server aplikasi utama dijalankan menggunakan Uvicorn ASGI server (uv run uvicorn app.main:app --reload --port 8000). '
    'Layanan ini bertugas menangani rute API RESTful dan WebSocket, mengelola sesi autentikasi berbasis JSON Web Token (JWT), '
    'serta menyajikan berkas antarmuka interaktif (dashboard.html, briefing.html, practice.html, dan summary.html).'
)

add_bullet_numbered(doc, '2.', 'AI Gateway Bifrost Berbasis Docker (Port 8080)', 
    'Kontainer Docker milo-bifrost-gateway dioperasikan secara lokal untuk mengelola laju permintaan (rate limiting 60 req/menit), '
    'menerapkan semantic caching kueri masukan berulang guna mereduksi latensi respons percakapan di bawah ambang 3 detik, '
    'serta memitigasi kegagalan koneksi ke server OpenAI API.'
)

add_bullet_numbered(doc, '3.', 'Basis Data Relasional & Koleksi Vektor Semantik', 
    'SQLAlchemy Async ORM dioperasikan untuk mencatat data akun pengguna, riwayat giliran percakapan, metrik latensi wicara, '
    'serta status poin gamifikasi secara persisten. Bersamaan dengan itu, koleksi vektor ChromaDB diaktifkan untuk menyediakan '
    'indeks semantik 18 modul kurikulum microlearning CEFR B1–B2.'
)

add_figure_image(doc, 
    'buku/screenshots/Gambar_3_13_LipSync_milo_live2d.png', 
    'Gambar 3.17 Tampilan Implementasi Ekstraksi Audio RMS dan Lip-sync Avatar Live2D', 
    width_in_inches=5.4
)

add_figure_image(doc, 
    'buku/screenshots/Gambar_3_14_Recording_practice_js.png', 
    'Gambar 3.18 Tampilan Implementasi Perekaman Wicara Dual Mode pada Practice Studio', 
    width_in_inches=5.4
)

# ------------------------------------------
# B. Prosedur Uji Coba Lapangan Kepada Responden
# ------------------------------------------
add_heading_subsubbab(doc, 'B. Prosedur Uji Coba Lapangan kepada Responden Mahasiswa')

add_paragraph_justify(doc, 
    'Sesuai dengan metodologi penelitian dan model ADDIE, penerapan platform MILO dilakukan kepada kelompok responden '
    'sebanyak minimal 30 mahasiswa politeknik dengan estimasi kemahiran CEFR level B1–B2 melalui empat fase pelaksanaan terstruktur, '
    'sebagaimana dirangkum pada Gambar 3.19:'
)

add_figure_image(doc, 
    'buku/generated_diagrams/Gambar_3_17_Prosedur_Uji_Coba_Responden.png', 
    'Gambar 3.19 Prosedur Empat Fase Penerapan dan Uji Coba Operasional kepada Responden', 
    width_in_inches=5.6
)

add_bullet_numbered(doc, '1.', 'Fase 1: Orientasi & Pengambilan Data Baseline (Pre-test)', 
    'Responden diberikan pengantar operasional sistem dan mengisi kuesioner Student Engagement awal (mencakup dimensi '
    'behavioral, emotional, dan cognitive) serta instrumen speaking anxiety berdasarkan pengalaman menggunakan media latihan berbicara '
    'yang biasa digunakan sebagai acuan awal (baseline).'
)

add_bullet_numbered(doc, '2.', 'Fase 2: Registrasi Akun & Diagnostic Placement Test', 
    'Responden membuka peramban web pada alamat localhost:8000, mendaftarkan akun baru, serta menyelesaikan tes diagnostik wicara '
    'singkat (setup-level.html) guna mengklasifikasikan kompetensi awal ke level CEFR B1 atau B2 dan memilih target modul pembelajaran.'
)

add_bullet_numbered(doc, '3.', 'Fase 3: Intervensi Latihan Percakapan Mandiri (3 hingga 5 Sesi)', 
    'Responden melaksanakan latihan berbicara interaktif berdurasi 3–5 menit per sesi. Pengguna meninjau kosakata pada briefing.html, '
    'bercakap-cakap 6–10 putaran dialog bersama avatar Live2D pada practice.html, dan menelaah koreksi tata bahasa serta perolehan XP '
    'pada summary.html. Selama sesi ini, sistem otomatis merekam telemetri aktivitas dan durasi latihan.'
)

add_bullet_numbered(doc, '4.', 'Fase 4: Post-test & Evaluasi Pengalaman Pengguna', 
    'Setelah menuntaskan seluruh sesi latihan berbicara, responden kembali mengisi kuesioner Student Engagement akhir (post-test) '
    'guna mengukur peningkatan keterlibatan belajar (N-Gain Hake), serta mengisi kuesioner User Experience Questionnaire (UEQ) '
    'untuk menilai aspek kebergunaan dan kenyamanan sistem sebagai masukan utama tahap 3.3.5 Evaluation.'
)

# Simpan Dokumen Final
final_output = 'buku/BAB_3_3_4_IMPLEMENTATION_ADDIE_MILO.docx'
doc.save(final_output)
print(f'Dokumen final berhasil disimpan secara rapi di: {final_output}')
