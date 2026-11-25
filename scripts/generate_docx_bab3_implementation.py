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

def add_body_p(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_font(r_pre, size=12, bold=True)
    r = p.add_run(text)
    set_font(r, size=12)
    return p

def add_bullet_p(doc, title, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r1 = p.add_run(title + ': ')
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

# Judul Bab & Subbab
p_title = doc.add_paragraph()
p_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(12)
p_title.paragraph_format.space_after = Pt(2)
r_b = p_title.add_run('BAB 3\nDESAIN SISTEM DAN METODOLOGI PENELITIAN')
set_font(r_b, size=14, bold=True)

# Subbab Utama
add_heading_1(doc, '3.3.4 Implementation (Tahap Penerapan Sistem AI-MILO)')

add_body_p(doc, 'Tahap Implementation (Penerapan) merupakan fase kritikal dalam kerangka kerja Multimedia Development Life Cycle (MDLC) maupun kerangka kerja instruksional ADDIE. Pada tahapan ini, seluruh komponen perangkat lunak, model kecerdasan buatan, basis pengetahuan kurikulum, serta aset antarmuka multimedia yang telah dituntaskan pada fase Development diintegrasikan dan dioperasikan ke dalam lingkungan operasional nyata. Penerapan ini bertujuan untuk memvalidasi bahwa arsitektur pipeline multimodal AI-MILO (Multimodal Interactive Learning Companion) mampu berjalan secara terpadu, stabil, responsif, dan siap digunakan dalam kegiatan eksperimen latihan berbicara bahasa Inggris mandiri oleh mahasiswa politeknik sebagai pengguna sasaran.')

add_image_centered(doc, 'buku/generated_diagrams/Gambar_3_16_Diagram_Arsitektur_Implementasi.png', 6.0)
add_caption(doc, 'Gambar 3.16 Diagram Arsitektur Integrasi dan Alur Operasional Pipeline AI-MILO')

add_heading_2(doc, '1. Penerapan Lingkungan Operasional dan Integrasi Layanan (Runtime Ecosystem)')

add_body_p(doc, 'Sistem AI-MILO dibangun menggunakan ekosistem multi-layanan (multi-service architecture) yang terkoordinasi secara asinkron guna memenuhi kebutuhan interaksi lisan berlatensi rendah (low-latency voice interaction). Seluruh komponen dikonfigurasikan pada lingkungan server lokal dengan pembagian peran komputasi sebagai berikut:')

add_bullet_p(doc, 'Manajemen Paket dan Lingkungan Eksekusi Python (uv)', 'Seluruh dependensi backend dikelola menggunakan pengelola paket modern uv pada Python versi 3.11+. Pendekatan ini menjamin kecepatan resolusi dependensi, deterministik environment melalui berkas uv.lock, dan isolasi pustaka inti seperti FastAPI, Uvicorn, SQLAlchemy, LangChain/ChromaDB, serta pustaka audio/evaluasi.')

add_bullet_p(doc, 'Layanan Backend FastAPI (Port 8000)', 'Dioperasikan melalui server ASGI Uvicorn (uvicorn app.main:app --reload --port 8000). Modul ini menyediakan gerbang RESTful API dan WebSocket untuk menangani alur transmisi berkas audio wicara pengguna (WAV/PCM 16 kHz), proses autentikasi berbasis JSON Web Token (JWT), isolasi sesi belajar, orkestrasi pipeline AI, serta penyajian aset antarmuka pengguna (frontend web application).')

add_bullet_p(doc, 'AI Gateway Bifrost Berbasis Kontainer Docker (Port 8080)', 'Dijalankan menggunakan kontainer Docker (docker-compose.bifrost.yml). Bifrost berfungsi sebagai proksi cerdas berkinerja tinggi antara backend FastAPI dengan penyedia model dasar (OpenAI API). Bifrost mengimplementasikan token-bucket rate limiting (60 request/menit) dan semantic caching untuk mencegah lonjakan biaya komputasi, menjamin ketersediaan kuota pemanggilan, serta meminimalisasi latensi pada kueri berulang.')

add_bullet_p(doc, 'Basis Data Relasional dan Penyimpanan Vektor Vektor Semantik', 'Penyimpanan data relasional dikelola melalui SQLAlchemy Async ORM yang terhubung ke SQLite/PostgreSQL untuk mencatat identitas pengguna, riwayat giliran percakapan, metrik latensi, perolehan skor XP, streak harian, serta capaian lencana gamifikasi. Di sisi lain, ChromaDB beroperasi sebagai basis data vektor tertanam (embedded vector database) yang memuat indeks embeddings 1536 dimensi dari 18 modul kurikulum microlearning CEFR B1–B2.')

# Screenshot Direktori
add_image_centered(doc, 'buku/screenshots/Gambar_3_10_Struktur_Direktori_VSCode.png', 5.6)
add_caption(doc, 'Gambar 3.17 Struktur Direktori Repositori dan Lingkungan Pengembangan AI-MILO')

add_heading_2(doc, '2. Realisasi Implementasi Modul Pipeline Multimodal AI')

add_body_p(doc, 'Pipeline percakapan pada AI-MILO melibatkan lima modul inti yang bekerja secara sekuensial dan asinkron untuk menjamin kelancaran interaksi berbicara antara pengguna dan tutor virtual:')

add_bullet_p(doc, 'Modul Automatic Speech Recognition (ASR) (app/core/asr.py)', 'Bertanggung jawab mengonversi masukan sinyal audio pengguna menjadi teks bahasa Inggris. Modul ini menerima audio pada sampling rate 16 kHz mono dari antarmuka web, menerapkan pra-pemrosesan normalisasi volume, serta meneruskan audio ke model OpenAI Whisper. Modul ini juga dilengkapi filter penghapus filler words berlebih dan deteksi jeda hening.')

add_bullet_p(doc, 'Modul Kurikulum dan Retrieval-Augmented Generation (RAG) (app/core/rag.py)', 'Mengimplementasikan mekanisme Hybrid Retrieval yang memadukan Dense Retrieval berbasis kesamaan kosinus vektor semantik pada ChromaDB dengan Sparse Retrieval berbasis leksikal BM25. Pendekatan hibrida ini memastikan tutor AI selalu merespons dengan konteks silabus yang presisi sesuai modul yang sedang dipelajari pengguna (misal: idiom akademik atau frasa wawancara kerja).')

add_bullet_p(doc, 'Modul Persona Tutor AI dan Session Closing Protocol (app/core/llm.py)', 'Mengorkestrasi model bahasa GPT-4o-mini dengan prompt rekayasa instruksional khusus. Tutor AI diinstruksikan untuk menggunakan persona ramah, sabar, adaptif terhadap level CEFR B1–B2, serta menerapkan teknik scaffolding komunikatif. Modul ini juga memuat logika Session Closing Protocol yang secara otomatis menghitung giliran bicara; pada putaran ke-8 hingga ke-10, tutor menutup percakapan secara alami dan memicu pengalihan ke halaman rangkuman.')

add_bullet_p(doc, 'Modul Evaluasi dan Umpan Balik Korektif CEFR (app/core/feedback.py)', 'Menganalisis tuturan pengguna secara objektif setelah sesi berakhir berdasarkan tiga pilar kompetensi komunikatif: akurasi tata bahasa (Grammar), kekayaan leksikal (Vocabulary), dan kelancaran wicara (Fluency). Modul ini menghasilkan koreksi terstruktur berupa kalimat asli pengguna, saran perbaikan kalimat, serta penjelasan kaidah bahasa dalam Bahasa Indonesia guna memudahkan pemahaman.')

add_bullet_p(doc, 'Modul Text-to-Speech (TTS) dan Real Audio Lip-Sync (app/core/tts.py & milo-live2d.js)', 'Mengonversi teks respons tutor AI menjadi aliran audio suara perempuan alami (natural conversational voice) berkarakter ramah. Pada sisi antarmuka, aliran audio diproses oleh Web Audio API AnalyserNode (FFT size 256) untuk mengekstraksi nilai RMS amplitudo secara real-time, lalu diinterpolasi secara halus (lerp smoothing) ke parameter gerak mulut avatar Live2D (ParamMouthOpenY dan ParamMouthForm).')

# Screenshot Lip Sync & Practice
add_image_centered(doc, 'buku/screenshots/Gambar_3_13_LipSync_milo_live2d.png', 5.6)
add_caption(doc, 'Gambar 3.18 Implementasi Ekstraksi Audio RMS dan Real-time Lip-Sync Live2D')

add_image_centered(doc, 'buku/screenshots/Gambar_3_14_Recording_practice_js.png', 5.6)
add_caption(doc, 'Gambar 3.19 Implementasi Perekaman Wicara Dual Mode (Push-to-Talk dan Smart VAD)')

add_heading_2(doc, '3. Prosedur Penerapan dan Skenario Uji Coba Lapangan kepada Responden')

add_body_p(doc, 'Setelah seluruh layanan terpasang dan terintegrasi secara andal pada server, sistem diterapkan kepada kelompok mahasiswa pengguna sasaran melalui protokol pengujian terstruktur yang terbagi dalam empat fase komprehensif, sebagaimana diilustrasikan pada Gambar 3.20:')

add_image_centered(doc, 'buku/generated_diagrams/Gambar_3_17_Prosedur_Uji_Coba_Responden.png', 5.8)
add_caption(doc, 'Gambar 3.20 Prosedur Empat Fase Penerapan dan Uji Coba Operasional kepada Responden')

add_bullet_p(doc, 'Fase 1: Orientasi dan Pengambilan Data Baseline (Pre-test)', 'Responden diberikan pengantar mengenai tata cara penggunaan sistem dan tujuan penelitian. Sebelum berinteraksi dengan AI-MILO, seluruh responden mengisi kuesioner Student Engagement awal (meliputi dimensi perilaku/behavioral, emosional/emotional, dan kognitif/cognitive) serta skala Speaking Anxiety berdasarkan pengalaman belajar konvensional mereka sebelumnya sebagai data acuan pembanding (baseline).')

add_bullet_p(doc, 'Fase 2: Registrasi Akun dan Diagnostic Placement Test', 'Responden mengakses peramban web pada alamat localhost:8000, membuat akun baru, dan menyelesaikan tes penempatan awal berbasis wicara (setup-level.html). Sistem secara otomatis mengklasifikasikan kompetensi awal pengguna ke dalam kategori CEFR B1 (Intermediate) atau B2 (Upper-Intermediate) serta menyajikan pilihan modul latihan yang relevan dengan sasaran karir mahasiswa.')

add_bullet_p(doc, 'Fase 3: Intervensi Latihan Percakapan Mandiri (3 hingga 5 Sesi)', 'Responden melaksanakan latihan berbicara secara berkala dengan durasi 3–5 menit per sesi. Alur latihan diawali dengan tinjauan kosakata pada briefing.html, dilanjutkan dengan percakapan interaktif bersama avatar Live2D pada practice.html selama 6–10 putaran dialog, dan diakhiri dengan peninjauan kartu koreksi kesalahan serta akumulasi poin XP pada summary.html. Selama fase ini, sistem telemetri otomatis mencatat rekaman log percakapan, durasi latihan, dan metrik latensi respon sistem.')

add_bullet_p(doc, 'Fase 4: Evaluasi Akhir dan Post-test Pengguna', 'Setelah menuntaskan seluruh siklus latihan, responden mengisi kembali kuesioner Student Engagement akhir (post-test) guna mengukur peningkatan keterlibatan belajar menggunakan metrik Normalized Gain (N-Gain Hake). Selain itu, responden mengisi kuesioner User Experience Questionnaire (UEQ) untuk mengevaluasi aspek kebergunaan (usability) dan daya tarik antarmuka platform.')

add_heading_2(doc, '4. Matriks Pengujian Fungsional Sistem (Black Box Testing Matrix)')

add_body_p(doc, 'Untuk memastikan keandalan fungsional dari seluruh antarmuka dan pipeline yang telah diterapkan, disusun matriks pengujian fungsionalitas kotak hitam (Black Box Testing) sebagaimana dirangkum pada Tabel 3.5 berikut:')

# Tambah Tabel Black Box Testing
table = doc.add_table(rows=1, cols=4)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = False

hdr_cells = table.rows[0].cells
hdr_titles = ['No', 'Komponen / Skenario Pengujian', 'Hasil yang Diharapkan', 'Status']
widths = [Inches(0.5), Inches(2.3), Inches(2.6), Inches(0.8)]

for idx, cell in enumerate(hdr_cells):
    cell.width = widths[idx]
    shading = parse_xml(r'<w:shd {} w:fill="1E293B"/>'.format(nsdecls('w')))
    cell._tc.get_or_add_tcPr().append(shading)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(hdr_titles[idx])
    set_font(r, size=10, bold=True, color=RGBColor(255, 255, 255))

test_cases = [
    ('1', 'Pendaftaran akun baru dan login pengguna via JWT token di login.html', 'Token JWT terbit, sesi tersimpan di LocalStorage, dan diarahkan ke dashboard', 'Valid'),
    ('2', 'Pelaksanaan Diagnostic Placement Test dengan input suara pada setup-level.html', 'Audio ditranskripsi Whisper, dihitung skor diagnostik, dan level CEFR terpetakan', 'Valid'),
    ('3', 'Navigasi katalog 18 modul microlearning dan halaman panduan briefing.html', 'Data kurikulum tampil dinamis sesuai level akun beserta target kosakata', 'Valid'),
    ('4', 'Perekaman audio mode Push-to-Talk (tekan-dan-tahan spasi / tombol mikrofon)', 'Audio 16 kHz direkam utuh dan berhasil dikirim ke endpoint /api/chat/audio', 'Valid'),
    ('5', 'Perekaman audio mode Smart VAD otomatis saat pengguna selesai berbicara', 'Sistem mendeteksi silence 1200 ms dan otomatis menghentikan serta mengirim audio', 'Valid'),
    ('6', 'Penelusuran silabus kontekstual melalui Hybrid RAG (ChromaDB + BM25)', 'Materi terkait modul berhasil diambil sebagai context augmentation prompt LLM', 'Valid'),
    ('7', 'Penalaran persona tutor AI dan eksekusi Session Closing Protocol', 'AI menjawab dalam konteks level CEFR dan menutup sesi otomatis pada putaran ke-8', 'Valid'),
    ('8', 'Sintesis suara respons tutor AI dan sinkronisasi bibir avatar Live2D', 'Audio TTS berputar jernih dan mulut avatar bergerak sinkron sesuai amplitudo RMS', 'Valid'),
    ('9', 'Pembangkitan evaluasi korektif tata bahasa dan metrik gamifikasi di summary.html', 'Kartu koreksi kalimat tampil terstruktur, skor XP dan streak harian bertambah', 'Valid'),
    ('10', 'Pencatatan telemetri aktivitas dan riwayat pesan ke basis data SQLAlchemy', 'Seluruh log sesi, transkrip, skor, dan timestamp tersimpan aman di tabel relasional', 'Valid'),
]

for row_idx, item in enumerate(test_cases):
    row_cells = table.add_row().cells
    bg_color = 'F8FAFC' if row_idx % 2 == 0 else 'FFFFFF'
    for col_idx, cell in enumerate(row_cells):
        cell.width = widths[col_idx]
        shading = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), bg_color))
        cell._tc.get_or_add_tcPr().append(shading)
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        if col_idx in [0, 3]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(item[col_idx])
        set_font(r, size=9, bold=(col_idx==3))
        if col_idx == 3:
            r.font.color.rgb = RGBColor(16, 149, 193) if item[3] == 'Valid' else RGBColor(220, 38, 38)

add_caption(doc, 'Tabel 3.5 Matriks Hasil Pengujian Fungsional Kotak Hitam (Black Box Testing) Sistem AI-MILO')

# Simpan Dokumen
output_path = 'buku/BAB_3_IMPLEMENTATION_AI_MILO.docx'
doc.save(output_path)
print(f'Dokumen Word berhasil dibuat: {output_path}')
