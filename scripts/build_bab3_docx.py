import os
import docx
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def create_bab3_docx(output_path):
    doc = Document()

    # Standar Margin PENS: Atas 3cm, Kiri 4cm, Bawah 3cm, Kanan 3cm
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(3)
        section.left_margin = Cm(4)
        section.bottom_margin = Cm(3)
        section.right_margin = Cm(3)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)

    def add_p(text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.5):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_heading_4(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_figure_placeholder(caption, figure_hint):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(5.8)
        set_cell_background(cell, "F3F4F6")
        set_cell_margins(cell, top=200, bottom=200, left=200, right=200)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(f"[AREA GAMBAR / SCREENSHOT]\n{figure_hint}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.italic = True
        r.font.color.rgb = RGBColor(100, 100, 100)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(11)
        r_cap.bold = True

    def add_table_custom(title, headers, rows_data, col_widths=None):
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_before = Pt(12)
        p_title.paragraph_format.space_after = Pt(4)
        r_title = p_title.add_run(title)
        r_title.bold = True
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(11)

        tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl)

        for c_idx, h_text in enumerate(headers):
            cell = tbl.cell(0, c_idx)
            set_cell_background(cell, "E2E8F0")
            set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(h_text)
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)

        for r_idx, row in enumerate(rows_data):
            for c_idx, val in enumerate(row):
                cell = tbl.cell(r_idx + 1, c_idx)
                set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx > 0 else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                r = p.add_run(str(val))
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10)

        if col_widths:
            for i, col in enumerate(tbl.columns):
                for cell in col.cells:
                    cell.width = col_widths[i]

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_equation_box(eq_text, eq_number):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.line_spacing = 1.2
        r = p.add_run(eq_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.italic = True
        r_num = p.add_run(f"       {eq_number}")
        r_num.bold = True
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(11)

    # ==================== ISI BAB 3 ====================
    add_heading_1("BAB 3\nDESAIN SISTEM DAN METODOLOGI PENELITIAN")

    # 3.1 DESKRIPSI SOLUSI
    add_heading_2("3.1 DESKRIPSI SOLUSI")
    add_p("Berdasarkan permasalahan yang telah diidentifikasi pada Bab II, penelitian ini merealisasikan pengembangan MILO (Multimodal Interactive Learning Companion), yaitu platform pembelajaran berbicara bahasa Inggris berbasis web yang memanfaatkan teknologi Artificial Intelligence (AI) dan avatar virtual sebagai mitra belajar interaktif. Platform ini ditujukan bagi mahasiswa dengan kemampuan bahasa Inggris setara CEFR level B1–B2 yang masih mengalami kendala dalam berlatih berbicara akibat speaking anxiety, minimnya mitra praktik lisan, serta ketiadaan media pembelajaran mandiri yang mampu memberikan koreksi secara langsung tanpa menghakimi. Melalui platform ini, pengguna dapat berlatih berbicara secara mandiri dalam lingkungan belajar yang aman, adaptif, dan responsif.")

    add_figure_placeholder(
        "Gambar 3.1 Diagram Alur Interaksi Pengguna (User Flow Diagram)",
        "Bagan Alur Pengguna: Login -> Diagnostic Placement Test -> Dashboard -> Briefing Studio -> Practice Studio (Live2D + VAD/Push-to-Talk) -> Closing Turn -> Summary Feedback & Gamification"
    )

    add_p("MILO mengintegrasikan teknologi Automatic Speech Recognition (ASR), Large Language Model (LLM), Retrieval-Augmented Generation (RAG), Text-to-Speech (TTS), serta avatar virtual dua dimensi (Live2D) dalam satu ekosistem terpadu. Sebagaimana diilustrasikan pada Gambar 3.1, pengguna memulai interaksi dengan memilih modul microlearning setelah melewati tahap uji penempatan awal (Diagnostic Placement Test). Sebelum memasuki percakapan, pengguna dibekali pemahaman awal melalui halaman Briefing yang menyajikan kosakata dan frasa kunci. Pada ruang latihan (Practice Studio), masukan suara pengguna ditangkap menggunakan dua pilihan mode: Push-to-Talk atau deteksi hening otomatis (Voice Activity Detection / VAD). Suara diproses menggunakan ASR Whisper untuk menghasilkan transkripsi teks, kemudian dianalisis oleh LLM dengan pengawalan RAG hibrida yang mengambil konteks silabus CEFR B1–B2. Respons percakapan disintesiskan kembali menjadi audio vokal alami melalui TTS, yang secara langsung menggerakkan artikulasi bibir (lip-sync) model avatar Live2D di kanvas WebGL.")

    add_p("Selain mendukung latihan berbicara, platform ini menerapkan pendekatan microlearning (sesi singkat 3–5 menit dengan 6–10 putaran dialog) dan gamifikasi terintegrasi. Pengguna memperoleh poin pengalaman (experience points/XP), mempertahankan rekor latihan harian (daily streak), serta membuka lencana pencapaian (badges). Kombinasi fitur ini dirancang untuk menumbuhkan motivasi intrinsik dan kebiasaan belajar mandiri secara konsisten.")

    # 3.2 METODE PENELITIAN
    add_heading_2("3.2 METODE PENELITIAN")
    add_p("Bab ini menjelaskan metodologi yang digunakan dalam penelitian untuk mengembangkan platform pembelajaran berbicara bahasa Inggris berbasis Artificial Intelligence (AI). Metodologi penelitian disusun secara sistematis agar proses pengembangan sistem, pengumpulan data, hingga evaluasi dapat dilakukan secara terarah sesuai dengan tujuan penelitian. Pada penelitian ini digunakan pendekatan mixed method yang mengombinasikan metode kualitatif dan kuantitatif untuk memperoleh hasil evaluasi yang komprehensif, sedangkan proses pengembangan sistem dilakukan menggunakan model ADDIE (Analysis, Design, Development, Implementation, dan Evaluation).")

    add_heading_3("3.2.1 Pendekatan Penelitian")
    add_p("Penelitian ini menerapkan pendekatan metode campuran (mixed methods approach) yang memadukan investigasi kualitatif dan pengujian empiris kuantitatif:")
    add_p("1. Pendekatan Kualitatif: Dilaksanakan melalui tinjauan ahli (expert review) yang melibatkan ahli media pembelajaran interaktif untuk validasi antarmuka dan animasi avatar Live2D, serta ahli pengajaran bahasa Inggris (ESL pedagogy expert) guna memvalidasi kesesuaian kurikulum CEFR B1–B2 dan keabsahan koreksi tata bahasa sistem.")
    add_p("2. Pendekatan Kuantitatif: Dilaksanakan melalui pengujian komputasi perangkat lunak (keberhasilan Black Box Testing, akurasi transkripsi ASR Whisper, latensi sistem melalui AI Gateway Bifrost), evaluasi kebergunaan antarmuka (usability) menggunakan kuesioner terstandar User Experience Questionnaire (UEQ), serta pengukuran dampak intervensi terhadap keterlibatan belajar (student engagement) mahasiswa melalui desain eksperimen pretest-posttest (N >= 30) dengan analisis Normalized Gain (N-Gain).")

    add_heading_3("3.2.2 Metode Pengembangan ADDIE")
    add_p("Pengembangan sistem dipandu oleh kerangka kerja instruksional ADDIE (Analysis, Design, Development, Implementation, Evaluation). Model ADDIE menyediakan metodologi rekayasa multimedia yang bertahap, berulang (iterative), dan memiliki siklus evaluasi formatif pada setiap fasenya.")

    add_figure_placeholder(
        "Gambar 3.2 Kerangka Pengembangan Sistem MILO Menggunakan Model ADDIE",
        "Diagram 5 Tahap Model ADDIE: Analysis -> Design -> Development -> Implementation -> Evaluation beserta siklus umpan balik formatif dan revisi"
    )

    # 3.3 TAHAPAN PENGEMBANGAN SISTEM
    add_heading_2("3.3 TAHAPAN PENGEMBANGAN SISTEM")

    # 3.3.1 Analysis
    add_heading_3("3.3.1 Analysis (Analisis Kebutuhan Sistem)")
    add_p("Tahap Analysis berfokus pada identifikasi profil pengguna sasaran, batasan kompetensi komunikatif, serta spesifikasi kebutuhan fungsional dan teknis sistem:")

    add_heading_4("1. Analisis Kebutuhan Pembelajaran dan Sasaran Pengguna")
    add_p("Subjek sasaran penelitian adalah mahasiswa politeknik/perguruan tinggi vokasi dengan estimasi kemahiran berbicara bahasa Inggris tingkat menengah (Intermediate / CEFR B1) hingga menengah atas (Upper-Intermediate / CEFR B2). Hasil studi pendahuluan menunjukkan bahwa kendala utama mahasiswa bukan terletak pada ketidaktahuan teori tata bahasa, melainkan pada kecemasan situasional (speaking anxiety) saat harus memproduksi tuturan spontan di hadapan dosen atau rekan sejawat. Oleh karena itu, platform membutuhkan mitra tutur virtual yang responsif, sabar, dan dilengkapi umpan balik formatif terstruktur.")

    add_heading_4("2. Analisis Kebutuhan Fungsional (Functional Requirements)")
    add_p("Sistem dirancang untuk memenuhi tujuh kapabilitas fungsional utama:")
    add_p("• F-01 (Manajemen Autentikasi & Akun): Pengelolaan akun pengguna, autentikasi sesi berbasis token JWT, dan isolasi riwayat latihan personal.")
    add_p("• F-02 (Diagnostic Placement Test): Pengujian diagnostik wicara singkat untuk memvalidasi penempatan level awal pengguna (B1 vs B2).")
    add_p("• F-03 (Perekaman & Transkripsi Wicara Dual Mode): Perekaman audio mikrofon pada resolusi 16 kHz mono menggunakan mode Push-to-Talk maupun Smart Voice Activity Detection (VAD) dengan transkripsi akurat oleh OpenAI Whisper.")
    add_p("• F-04 (Hybrid Context Retrieval): Penelusuran materi silabus kurikulum CEFR secara hibrida memadukan pencarian semantik (ChromaDB) dan pencarian leksikal (BM25).")
    add_p("• F-05 (Contextual Conversation & Closing Protocol): Penalaran dialog interaktif berbasis GPT-4o-mini yang mematuhi batasan The One-Question Rule, penyesuaian register CEFR, serta penanganan otomatis sesi penutup dialog (closing turn).")
    add_p("• F-06 (Neural Speech Synthesis & Real Audio Lip-Sync): Konversi teks balasan ke suara alami melalui OpenAI TTS profil nova dan penggerak bukaan bibir model Live2D di kanvas WebGL berbasis energi amplitudo audio nyata (RMS volume).")
    add_p("• F-07 (Microlearning & Gamification Engine): Pengelolaan 18 modul latihan berdurasi 3–5 menit, perhitungan poin pengalaman (XP), pencatatan daily streak, dan pembukaan lencana prestasi (badges).")

    add_heading_4("3. Analisis Kebutuhan Non-Fungsional (Non-Functional Requirements)")
    add_p("• NF-01 (Performansi & Latensi Komputasi): Waktu pemrosesan keseluruhan (end-to-end response time) dari selesainya ucapan pengguna hingga suara avatar terdengar dibatasi maksimal 3,0 detik.")
    add_p("• NF-02 (Keandalan Operasional & Caching): Integrasi AI Gateway Bifrost pada port lokal 8080 untuk pembatasan laju kueri (rate limiting 60 req/min), penyimpanan cache semantik kueri berulang, dan mitigasi kegagalan jaringan.")
    add_p("• NF-03 (Aksesibilitas & Ergonomi Antarmuka): Tata letak antarmuka dirancang bersih, kontras warna memenuhi standar WCAG AAA, serta responsif terhadap layar komputer jinjing (laptop).")
    add_p("• NF-04 (Keamanan & Integritas Data): Penyimpanan data kredensial terenkripsi Bcrypt pada basis data relasional SQLite/PostgreSQL melalui SQLAlchemy Async ORM.")

    add_table_custom(
        "Tabel 3.1 Analisis Kebutuhan Pengembangan Sistem MILO",
        ["Kategori Kebutuhan", "Komponen Analisis", "Deskripsi Kebutuhan Sistem"],
        [
            ["Karakteristik Pengguna", "Mahasiswa Tingkat B1–B2", "Memerlukan lingkungan latihan berbicara yang bebas dari tekanan sosial, topik kontekstual, dan koreksi tata bahasa yang konstruktif."],
            ["Teknologi Wicara", "ASR Whisper & TTS Nova", "Perekaman audio 16 kHz (Push-to-Talk & VAD), transkripsi ASR Whisper-1, dan sintesis vokal ekspresif OpenAI TTS-1."],
            ["Kecerdasan Buatan", "LLM GPT-4o-mini & Hybrid RAG", "Penalaran tutor cerdas berstandar CEFR, prompt scaffolding, didukung basis pengetahuan materi Markdown, ChromaDB, dan BM25."],
            ["Antarmuka Visual", "Avatar Virtual 2D Live2D", "Karakter 2D orisinal MILO yang di-rigging pada Live2D Cubism 4, di-render via WebGL/PIXI.js dengan real audio lip-sync."],
            ["Keterlibatan Belajar", "Microlearning & Gamifikasi", "18 topik latihan ringkas (3–5 menit), panduan briefing, perolehan poin XP, rekor konsistensi harian (streak), dan lencana apresiasi."]
        ],
        [Inches(1.8), Inches(1.8), Inches(2.2)]
    )

    add_table_custom(
        "Tabel 3.2 Komponen Perangkat Lunak yang Digunakan",
        ["No", "Perangkat Lunak", "Versi / Rilis", "Peran dan Fungsi dalam Sistem"],
        [
            ["1", "Python", "3.11.x (via uv)", "Bahasa pemrograman utama logika backend, pipeline AI, dan ekspor analitik."],
            ["2", "FastAPI", "0.115.x", "Framework backend asinkron berkinerja tinggi untuk penyedia REST API."],
            ["3", "Uvicorn", "0.34.x", "ASGI server untuk menjalankan aplikasi backend FastAPI pada port 8000."],
            ["4", "ChromaDB", "0.5.x", "Basis data vektor untuk menyimpan representasi numerik dokumen kurikulum."],
            ["5", "OpenAI Whisper API", "Whisper-1", "Model Automatic Speech Recognition (ASR) untuk transkripsi audio wicara."],
            ["6", "OpenAI Chat API", "GPT-4o-mini", "Model bahasa cerdas untuk penalaran percakapan dan koreksi linguistik."],
            ["7", "OpenAI Audio API", "TTS-1 (nova)", "Layanan sintesis wicara alami untuk menghasilkan suara tutor virtual."],
            ["8", "Bifrost AI Gateway", "1.x (Docker)", "Reverse proxy lokal untuk manajemen rate limit, caching, dan token budgeting."],
            ["9", "Live2D Cubism Editor & SDK", "Cubism 4.2 & Web SDK", "Perangkat lunak rigging model karakter 2D dan pustaka rendering WebGL/PIXI.js."],
            ["10", "Tailwind CSS & HTML5", "3.4.x", "Framework styling antarmuka web, kontrol Web Audio API, dan kanvas responsif."],
            ["11", "Docker Desktop", "4.3x", "Kontainerisasi layanan Bifrost AI Gateway pada port 8080."]
        ],
        [Inches(0.5), Inches(1.8), Inches(1.4), Inches(2.1)]
    )

    add_table_custom(
        "Tabel 3.3 Spesifikasi Perangkat Keras Pengembangan dan Pengujian",
        ["No", "Komponen Perangkat Keras", "Spesifikasi Minimum / Rekomendasi", "Peran dalam Proyek Akhir"],
        [
            ["1", "Processor (CPU)", "Intel Core i7 12th Gen / AMD Ryzen 7", "Komputasi server backend, pemrosesan sinyal audio, dan embedding vektor."],
            ["2", "Memori (RAM)", "16 GB DDR4 / DDR5", "Memastikan eksekusi paralel FastAPI, ChromaDB, dan kontainer Docker stabil."],
            ["3", "Penyimpanan (Storage)", "512 GB NVMe SSD", "Menyimpan korpus kurikulum, aset tekstur Live2D, dan basis data relasional."],
            ["4", "Mikrofon Masukan", "USB Condenser Microphone / Headset Mic", "Menangkap masukan suara wicara pengguna dengan kualitas sinyal bersih."],
            ["5", "Perangkat Keluaran Audio", "Stereo Headphone / Speaker", "Memonitor keluaran suara TTS dan sinkronisasi artikulasi bibir avatar."],
            ["6", "Koneksi Jaringan", "Pita lebar internet minimal 10 Mbps", "Komunikasi data dengan API model bahasa dan layanan gateway awan."]
        ],
        [Inches(0.5), Inches(1.8), Inches(1.8), Inches(1.7)]
    )

    # 3.3.2 Design
    add_heading_3("3.3.2 Design (Perancangan Sistem)")
    add_p("Perancangan sistem dalam penelitian ini difokuskan pada integrasi alur pemrosesan kecerdasan buatan multimodal (multimodal AI pipeline) dan interaksi pengguna yang terstruktur. Sistem yang dirancang bertujuan untuk menghubungkan basis pengetahuan pembelajaran bahasa Inggris standar CEFR B1–B2 dengan teknologi pemrosesan bahasa alami serta avatar virtual interaktif, sehingga menghasilkan mitra belajar berbicara (virtual learning companion) yang adaptif dan responsif. Penjelasan mengenai perancangan sistem ini diawali dengan gambaran umum arsitektur sistem (high-level view) untuk memudahkan pemahaman terhadap alur pemrosesan data secara keseluruhan.")

    # A. Design Sistem (Layered Architecture) - SESUAI PERMINTAAN USER LENGKAP
    add_heading_4("A. Design Sistem (Arsitektur Berlapis)")
    add_figure_placeholder(
        "Gambar 3.3 Desain Sistem",
        "Diagram Arsitektur Berlapis (Layered Architecture): Input Layer -> Core Processing -> Knowledge & Data -> Output Layer -> Learning & Engagement"
    )
    add_p("Berdasarkan hasil analisis kebutuhan pada tahap sebelumnya, desain sistem MILO (Multimodal Interactive Learning Companion) dirancang menggunakan pendekatan arsitektur berlapis (layered architecture). Pendekatan ini bertujuan untuk memisahkan fungsi utama setiap komponen sehingga sistem menjadi lebih terstruktur, mudah dikembangkan, serta memudahkan integrasi antara layanan kecerdasan buatan (ASR, LLM, RAG, dan TTS), avatar virtual 2D (Live2D), dan fitur gamifikasi dalam satu ekosistem berbasis web.")
    add_p("Secara keseluruhan, arsitektur sistem MILO terdiri atas lima komponen utama, yaitu Input Layer, Core Processing, Knowledge & Data, Output Layer, dan Learning & Engagement, yang saling terintegrasi untuk menghasilkan luaran berupa peningkatan student engagement sebagai tujuan utama penelitian, sebagaimana ditunjukkan pada Gambar 3.3.")
    add_p("Berdasarkan Gambar 3.3, alur kerja sistem dapat dijelaskan melalui beberapa tahapan sebagai berikut:")

    add_p("1) Input Layer", bold=True)
    add_p("Input Layer merupakan tahap awal interaksi antara pengguna dengan sistem. Pada tahap ini, pengguna dapat memberikan masukan melalui voice input, text input, serta learning goals. Voice input digunakan sebagai media utama latihan berbicara bahasa Inggris, di mana pengguna berbicara secara langsung melalui mikrofon perangkat. Selain itu, sistem juga menyediakan text input sebagai alternatif apabila pengguna ingin berinteraksi menggunakan teks.")
    add_p("Komponen learning goals digunakan untuk menentukan tujuan pembelajaran yang ingin dicapai, seperti Daily Conversation, Presentation Practice, Academic Discussion, atau Job Interview Practice. Informasi tersebut menjadi acuan bagi sistem dalam menyesuaikan konteks percakapan, materi pembelajaran, serta tingkat kesulitan latihan yang akan diberikan kepada pengguna.")

    add_p("2) Core Layer", bold=True)
    add_p("Core Processing merupakan inti dari sistem MILO yang bertugas mengolah seluruh masukan pengguna hingga menghasilkan respons pembelajaran. Pada tahap ini, voice input terlebih dahulu diproses menggunakan teknologi Automatic Speech Recognition (ASR) berbasis OpenAI Whisper untuk mengubah ucapan pengguna menjadi teks (speech-to-text). Selanjutnya, teks masukan diproses oleh Large Language Model (LLM), yaitu GPT-4o Mini, untuk memahami konteks percakapan, menghasilkan respons, serta memberikan umpan balik yang sesuai dengan tujuan pembelajaran.")
    add_p("Agar respons yang dihasilkan lebih akurat dan relevan, sistem mengimplementasikan mekanisme Retrieval-Augmented Generation (RAG). Melalui mekanisme ini, LLM memperoleh informasi tambahan dari basis pengetahuan yang dimiliki sistem sebelum menghasilkan respons akhir. Dengan demikian, jawaban yang diberikan tidak hanya bergantung pada pengetahuan bawaan model, tetapi juga mempertimbangkan materi pembelajaran yang telah disediakan.")

    add_p("3) Storage Layer", bold=True)
    add_p("Knowledge & Data berfungsi sebagai pusat penyimpanan informasi yang mendukung proses pembelajaran serta implementasi mekanisme RAG. Komponen ini menyimpan berbagai data yang diperlukan sistem, antara lain:")
    add_p("• Knowledge Base yang berisi materi kosakata (vocabulary), tata bahasa (grammar), dan materi pembelajaran sesuai level CEFR B1–B2.")
    add_p("• Riwayat percakapan (conversation history) yang digunakan untuk menjaga konteks interaksi antar sesi.")
    add_p("• Data perkembangan pengguna (learning progress) yang digunakan untuk memantau pencapaian selama proses pembelajaran.")
    add_p("Seluruh data tersebut dimanfaatkan oleh mekanisme RAG untuk menyediakan konteks tambahan kepada LLM sehingga respons yang dihasilkan lebih sesuai dengan topik pembelajaran dan kebutuhan pengguna.")

    add_p("4) Output Layer", bold=True)
    add_p("Output Layer merupakan tahap akhir proses interaksi antara pengguna dan sistem. Berdasarkan hasil pemrosesan pada Core Processing, sistem menghasilkan respons percakapan yang disampaikan melalui beberapa bentuk keluaran, yaitu audio menggunakan teknologi Text-to-Speech (TTS), tampilan avatar virtual 2D (Live2D) sebagai media interaksi, serta umpan balik pembelajaran berupa koreksi tata bahasa, rekomendasi kosakata, dan saran perbaikan kemampuan berbicara. Penyajian respons dalam bentuk visual dan audio dirancang untuk menciptakan pengalaman belajar yang lebih natural sehingga pengguna dapat berlatih berbicara layaknya melakukan percakapan dengan tutor virtual.")

    add_p("5) Learning & Engagement", bold=True)
    add_p("Learning & Engagement merupakan komponen yang mendukung peningkatan keterlibatan pengguna selama proses pembelajaran. Layer ini terdiri atas tiga fitur utama, yaitu Microlearning, Gamification, dan Progress Tracking.")
    add_p("Fitur Microlearning menyajikan materi pembelajaran dalam durasi singkat dan terfokus sehingga lebih mudah dipelajari secara bertahap. Gamification memberikan elemen permainan seperti poin, lencana (badge), dan tantangan harian untuk meningkatkan motivasi belajar. Sementara itu, Progress Tracking digunakan untuk memantau perkembangan kemampuan pengguna berdasarkan aktivitas latihan yang telah dilakukan.")
    add_p("Ketiga fitur tersebut saling terintegrasi dengan proses pembelajaran sehingga mampu mendorong pengguna untuk berlatih secara konsisten, mempertahankan motivasi, serta meningkatkan keterlibatan dalam menggunakan sistem.")
    add_p("Sebagai hasil akhir dari keseluruhan proses, MILO diharapkan mampu meningkatkan student engagement dalam pembelajaran berbicara bahasa Inggris. Peningkatan keterlibatan ini dicapai melalui integrasi teknologi AI, penyajian materi secara adaptif, interaksi menggunakan avatar virtual, serta penerapan strategi microlearning, gamification, dan progress tracking. Dengan pendekatan tersebut, pengguna diharapkan memiliki motivasi belajar yang lebih tinggi, rasa percaya diri dalam berlatih berbicara, serta kebiasaan belajar yang berkelanjutan.")

    # B. Perancangan Alur Pengguna
    add_heading_4("B. Perancangan Alur Pengguna (Detailed User Flow Diagram)")
    add_figure_placeholder(
        "Gambar 3.4 Diagram Alur Pengguna Terperinci (Detailed User Flow Diagram)",
        "Diagram Alur Pengguna Rinci: Login -> Diagnostic Test -> Dashboard -> Pemilihan 18 Modul -> Briefing Studio -> Practice Studio (Push-to-Talk/VAD) -> Closing Turn -> Summary Feedback"
    )
    add_p("Alur interaksi pengguna memetakan tahapan mulai dari autentikasi akun -> pengujian diagnostik (setup-level.html) -> pemilihan topik dari 18 modul microlearning (pilih_topik_microlearning.html) -> persiapan kosakata pada Briefing Studio (briefing.html) -> latihan berbicara aktif di Practice Studio (practice.html) -> penutupan dialog otomatis -> hingga halaman rangkuman evaluasi (summary.html).")

    # C. Perancangan Knowledge Base & Adaptive Hybrid RAG
    add_heading_4("C. Perancangan Knowledge Base & Adaptive Hybrid RAG")
    add_figure_placeholder(
        "Gambar 3.5 Diagram Pipeline Ingesti dan Penelusuran Adaptive Hybrid RAG",
        "Pipeline Hybrid RAG: Markdown & curriculum-data.js 18 Topik -> Chunking 500/50 -> Dense Embedding (text-embedding-3-small 1536 dim) + Sparse Indexing BM25 -> ChromaDB & In-Memory Index -> Hybrid Retrieval & RRF Reranking -> GPT-4o-mini"
    )
    add_p("1. Struktur Korpus Silabus: Korpus materi disimpan dalam berkas Markdown berstruktur frontmatter pada direktori knowledge_base/ dan direplikasi ke dalam format data JavaScript terstruktur (frontend/js/curriculum-data.js) mencakup 18 modul microlearning (9 topik level B1 dan 9 topik level B2) yang siap beroperasi secara offline fallback.")
    add_p("2. Chunking Strategy: Dokumen dipecah menggunakan RecursiveCharacterTextSplitter dengan ukuran pecahan (chunk size) 500 karakter dan toleransi tumpang tindih (overlap) 50 karakter.")
    add_p("3. Vektorisasi Semantik: Potongan teks dikonversi menjadi representasi vektor numerik berdimensi 1536 menggunakan model text-embedding-3-small, lalu diindeks pada ChromaDB dengan metrik Cosine Similarity.")
    add_p("4. Hybrid Retrieval & RRF: Penelusuran semantik ChromaDB dipadukan dengan penelusuran kata kunci leksikal BM25. Hasil pemeringkatan kedua metode digabungkan menggunakan algoritma Reciprocal Rank Fusion (RRF) untuk mengambil 3 dokumen terbaik (top_k = 3).")

    # D. Perancangan AI Gateway
    add_heading_4("D. Perancangan AI Gateway (Bifrost)")
    add_figure_placeholder(
        "Gambar 3.6 Diagram Arsitektur Perantara AI Gateway Bifrost",
        "Diagram Arsitektur Bifrost: FastAPI Port 8000 -> Bifrost Container Port 8080 (Rate Limiter 60 req/min, Semantic Cache cosine >= 0.95, Token Budgeting 250 token, Circuit Breaker) -> OpenAI API"
    )
    add_p("1. Rate Limiting: Membatasi beban panggilan maksimal 60 permintaan per menit per pengguna.")
    add_p("2. Semantic Cache: Kueri masukan yang memiliki derajat kemiripan kosinus >= 0.95 dengan riwayat kueri sebelumnya langsung disajikan dari cache lokal dalam waktu < 50 ms.")
    add_p("3. Token Budgeting: Maksimal 250 output token per giliran respons dialog untuk efisiensi biaya komputasi.")
    add_p("4. Circuit Breaker: Mekanisme penanganan kegagalan otomatis (retry 3x) sebelum mengaktifkan respons darurat (fallback).")

    # E. Perancangan Conversational Prompting & Scaffolding
    add_heading_4("E. Perancangan Conversational Prompting & Scaffolding Pedagogis")
    add_p("1. The One-Question Rule: Setiap giliran respons tutor AI hanya diperbolehkan memuat satu pertanyaan terarah di akhir kalimat guna menjaga fokus pengguna dan mencegah cognitive overload.")
    add_p("2. Scaffolding Adaptif CEFR: Mengatur kompleksitas sintaksis dan perbendaharaan kata sesuai level B1 vs B2.")
    add_p("3. Closing Turn Protocol: Ketika giliran bicara pengguna telah mencapai batas target (misal putaran ke-8), model AI secara otomatis beralih ke mode penutup: memberikan evaluasi umum yang membesarkan hati, salam penutup, dan memicu pengalihan otomatis ke halaman rangkuman.")
    add_p("4. Format Umpan Balik Terstruktur: Koreksi tata bahasa diformat dalam struktur JSON standar (original_sentence, corrected_sentence, error_category, dan pedagogical_explanation).")

    # F. Formulasi Matematis Sistem
    add_heading_4("F. Formulasi Matematis Sistem")
    add_p("1. Kemiripan Kosinus (Cosine Similarity):")
    add_equation_box(
        "Cosine Similarity(q, d) = (q · d) / (||q|| ||d||) = Σ(q_i · d_i) / [sqrt(Σ q_i^2) · sqrt(Σ d_i^2)]",
        "(Persamaan 3.1)"
    )

    add_p("2. Penggabungan Peringkat (Reciprocal Rank Fusion - RRF):")
    add_equation_box(
        "RRF_Score(d ∈ D) = Σ [1 / (k + r_m(d))]    dengan k = 60",
        "(Persamaan 3.2)"
    )

    add_p("3. Formulasi Skor Placement Test (Diagnostic Score):")
    add_equation_box(
        "Score_placement = (0.40 · S_g) + (0.35 · S_v) + (0.25 · S_f)",
        "(Persamaan 3.3)"
    )
    add_p("Kriteria: Jika Score_placement >= 70.0% maka level B2, sebaliknya level B1.")

    add_p("4. Formulasi Skor Performa Sesi Pembelajaran (Session Speaking Score):")
    add_equation_box(
        "Score_session = [0.30 · (C_turns / T_target)] + (0.40 · Acc_grammar) + (0.30 · Fluency_wpm)",
        "(Persamaan 3.4)"
    )

    # G. Perancangan Basis Data
    add_heading_4("G. Perancangan Basis Data (Database Design)")
    add_figure_placeholder(
        "Gambar 3.7 Entity Relationship Diagram (ERD) Basis Data MILO",
        "Diagram ERD Relasional Basis Data: Entitas users, practice_sessions, messages, user_gamification, user_badges beserta relasi Primary Key dan Foreign Key"
    )

    add_table_custom(
        "Tabel 3.4 Kamus Data Basis Data Relasional MILO",
        ["Nama Tabel", "Nama Kolom", "Tipe Data", "Keterangan & Batasan"],
        [
            ["users", "id\nemail\nhashed_password\nfull_name\ntarget_cefr", "UUID\nVARCHAR(255)\nVARCHAR(255)\nVARCHAR(100)\nVARCHAR(10)", "Primary Key\nUnique, Not Null\nSandi terenkripsi Bcrypt\nNama lengkap pengguna\nLevel aktif ('B1' atau 'B2')"],
            ["practice_sessions", "id\nuser_id\ntopic_name\ntarget_cefr\nstart_time", "UUID\nUUID\nVARCHAR(100)\nVARCHAR(10)\nTIMESTAMP", "Primary Key\nForeign Key (users.id)\nTopik percakapan\nTingkat kesulitan sesi\nWaktu mulai sesi"],
            ["messages", "id\nsession_id\nsender_role\ntranscribed_text\nfeedback_json", "UUID\nUUID\nVARCHAR(20)\nTEXT\nJSONB / TEXT", "Primary Key\nForeign Key (practice_sessions.id)\nNilai: 'user' / 'assistant'\nTranskripsi suara pengguna\nData koreksi tata bahasa"],
            ["user_gamification", "id\nuser_id\ntotal_points\ncurrent_streak\nlast_active", "UUID\nUUID\nINTEGER\nINTEGER\nDATE", "Primary Key\nForeign Key (users.id)\nAkumulasi poin XP pengguna\nRekor hari berturut-turut\nTanggal aktivitas terakhir"],
            ["user_badges", "id\nuser_id\nbadge_code\nunlocked_at", "UUID\nUUID\nVARCHAR(50)\nTIMESTAMP", "Primary Key\nForeign Key (users.id)\nKode unik lencana prestasi\nWaktu perolehan lencana"]
        ],
        [Inches(1.5), Inches(1.5), Inches(1.3), Inches(1.5)]
    )

    # H. Perancangan Identitas Visual dan Karakter Live2D
    add_heading_4("H. Perancangan Identitas Visual dan Karakter Avatar Live2D")
    add_p("Identitas visual dirancang sebagai representasi dari platform pembelajaran berbicara bahasa Inggris interaktif yang dikembangkan. Perancangan identitas visual dilakukan dengan mempertimbangkan tema pendamping belajar bahasa Inggris virtual (virtual learning companion) yang ramah serta karakteristik target audiens, yaitu mahasiswa dengan tingkat kemahiran CEFR B1–B2 yang kerap mengalami kecemasan berbicara (speaking anxiety). Identitas visual tersebut mencakup logo, tipografi, desain karakter beserta rigging Live2D, dan palet warna yang digunakan sebagai pedoman untuk menjaga konsistensi tampilan pada setiap bagian aplikasi web. Penerapan elemen visual yang selaras dan menenangkan diharapkan dapat menciptakan lingkungan belajar yang nyaman, mudah dikenali, serta mendorong keterlibatan belajar pengguna.")

    add_p("a) Logo", bold=True)
    add_p("Logo platform pembelajaran dirancang dengan mengangkat nama \"MILO\" (Multimodal Interactive Learning Companion) sebagai identitas utama aplikasi berbasis web sebagaimana ditunjukkan pada Gambar 3.8a. Penggunaan ikon karakter dan penamaan \"MILO\" bertujuan merepresentasikan sosok mitra belajar virtual yang bersahabat, santai, dan tidak mengintimidasi saat menemani pengguna berlatih berbicara bahasa Inggris. Secara visual, logo menggunakan kombinasi warna hangat bernuansa cokelat kayu manis (#8D613F) dan hijau teal (#407E79) di atas latar krem lembut (#FAF5EB). Susunan tipografi merek \"MILO\" dirancang dengan bentuk huruf tebal dan sedikit membulat untuk menghadirkan kesan ramah dan modern, serta dipadukan secara konsisten pada bilah navigasi di seluruh halaman aplikasi (frontend/assets/Icon logo milo.svg).")
    add_figure_placeholder(
        "Gambar 3.8a Logo Platform Pembelajaran AI-MILO",
        "Tampilan logo utama AI-MILO (Icon logo milo.svg dan wordmark MILO)"
    )

    add_p("b) Tipografi", bold=True)
    add_p("Tipografi yang digunakan dalam perancangan platform MILO terdiri atas dua typeface utama, yaitu Nunito dan DM Sans sebagaimana ditunjukkan pada Gambar 3.8b. Nunito (bobot 600–900) digunakan sebagai tipografi utama untuk judul halaman, merek antarmuka, dan elemen teks yang membutuhkan penekanan visual. Jenis huruf sans-serif bergaya membulat (rounded) tersebut dipilih untuk memperkuat kesan bersahabat, hangat, dan mengurangi ketegangan psikologis pengguna. Sementara itu, DM Sans (bobot 400–700) digunakan sebagai tipografi pendukung untuk menyajikan teks dialog percakapan, instruksi materi briefing, serta rincian umpan balik koreksi tata bahasa. DM Sans memiliki proporsi huruf yang bersih dan keterbacaan tinggi pada layar digital sehingga memudahkan pengguna membaca hasil transkripsi maupun koreksi kalimat secara cepat.")
    add_figure_placeholder(
        "Gambar 3.8b Tipografi Platform AI-MILO (Nunito dan DM Sans)",
        "Spesimen huruf Nunito (Headings/Brand) dan DM Sans (Body/Dialog/Feedback)"
    )

    add_p("c) Palet Warna", bold=True)
    add_p("Palet warna yang digunakan dalam perancangan antarmuka MILO didominasi oleh kombinasi warna hangat bernuansa krem (Cream #FAF5EB dan Paper #FFFDF8), hijau teal (Deep Teal #407E79 dan Soft Teal #A8D9D1), cokelat kayu manis (Milo Cinnamon #8D613F), serta aksen oranye terakota (#E99965) dan tinta abu-abu gelap (#344557) sebagai warna teks utama sebagaimana ditunjukkan pada Gambar 3.8c. Pemilihan palet warna netral-hangat dan hijau botanical ini bertujuan untuk menciptakan atmosfer belajar yang tenang, nyaman di mata (mengurangi kelelahan visual), dan mereduksi kecemasan berbicara, sekaligus memberikan kontras yang jelas pada tombol aksi utama dan elemen umpan balik.")
    add_figure_placeholder(
        "Gambar 3.8c Palet Warna Antarmuka AI-MILO (#FAF5EB, #407E79, #8D613F, #E99965, #344557)",
        "Susunan swatch palet warna resmi AI-MILO lengkap dengan kode hex"
    )

    add_p("d) Karakter dan Spesifikasi Avatar Virtual 2D (Live2D)", bold=True)
    add_p("Desain karakter dalam platform MILO menggunakan ilustrasi bergaya semi-anime/ilustratif dua dimensi yang merepresentasikan sosok asisten tutor virtual yang ekspresif sebagaimana ditunjukkan pada Gambar 3.8d. Selain 9 variasi aset pose ekspresif untuk memperkaya antarmuka pengantar (menyapa, melambai, duduk, memakai laptop, membaca buku, membaca ponsel, mempersilahkan, menunduk, dan mendengarkan musik), karakter utama MILO di-rigging secara khusus menggunakan Live2D Cubism Editor (MILO Model.moc3, MILO Model.model3.json, dan MILO Model.cdi3.json) agar dapat merespons suara secara real-time di kanvas WebGL. Alur sinkronisasi audio serta pemetaan parameter rigging karakter terhadap sinyal suara dan dinamika interaksi sistem dirinci pada Gambar 3.8e dan Tabel 3.5.")
    add_figure_placeholder(
        "Gambar 3.8d Desain Karakter Avatar Virtual 2D MILO dan Variasi Pose",
        "Tampilan karakter utama MILO Live2D beserta variasi pose ekspresifnya"
    )

    add_figure_placeholder(
        "Gambar 3.8e Diagram Alur Sinkronisasi Audio dan Rigging Parameter Live2D",
        "Diagram Alur Audio Lip-sync: Audio TTS -> Web Audio API AnalyserNode (FFT Size 256) -> Ekstraksi RMS Volume -> Lerp Smoothing -> Parameter Live2D ParamMouthOpenY & ParamMouthForm"
    )

    add_table_custom(
        "Tabel 3.5 Pemetaan Parameter Model Live2D terhadap Dinamika Sistem",
        ["Parameter ID", "Rentang Nilai", "Pemicu Input / Event", "Efek Gerak Visual pada Avatar"],
        [
            ["ParamMouthOpenY", "0.0 s.d. 1.0", "Amplitudo RMS audio wicara TTS", "Buka-tutup mulut (lip-sync) mengikuti suku kata"],
            ["ParamMouthForm", "-1.0 s.d. +1.0", "Bentuk vokal suara percakapan", "Bentuk bibir tersenyum saat mengartikulasikan kata"],
            ["ParamEyeLOpen, ParamEyeROpen", "0.0 s.d. 1.0", "Random timer interval 2.5–4.0 detik", "Kedipan mata natural saat posisi siaga (idle)"],
            ["ParamEyeBallX, ParamEyeBallY", "-1.0 s.d. +1.0", "Koordinat kursor mouse pengguna", "Bola mata mengikuti arah pergerakan kursor (gaze tracking)"],
            ["ParamAngleX, ParamAngleY", "-30° s.d. +30°", "Koordinat kursor mouse pengguna", "Orientasi wajah menoleh mengikuti interaksi pengguna"],
            ["ParamAngleZ", "-30° s.d. +30°", "Status sistem: Pengguna berbicara", "Kepala miring menyimak dengan penuh empati"],
            ["ParamBreath", "0.0 s.d. 1.0", "Siklus osilator sinus waktu", "Gerakan pernapasan dada saat kondisi siaga (idle breathing)"]
        ],
        [Inches(1.8), Inches(1.2), Inches(1.5), Inches(1.3)]
    )

    # I. Perancangan Antarmuka Pengguna
    add_heading_4("I. Perancangan Antarmuka Pengguna (Wireframe & High-Fidelity Mockup)")
    add_figure_placeholder(
        "Gambar 3.9 Rancangan Antarmuka Pengguna (UI Mockup)",
        "Kolase Antarmuka Pengguna: (a) Wireframe Alur Navigasi, (b) Mockup Dashboard & Pemilihan 18 Modul, (c) Briefing Studio, (d) Practice Studio Live2D + Waveform, (e) Summary Feedback & Gamifikasi"
    )

    # 3.3.3 Development
    add_heading_3("3.3.3 Development (Tahap Pengembangan Sistem)")
    add_p("Tahap Development merupakan realisasi teknis dari seluruh cetak biru yang telah dirumuskan pada tahap Design. Pada tahap ini, pengembang telah berhasil membangun basis kode sumber (source code), mengoperasikan gerbang AI terisolasi, menyusun basis data kurikulum dan vektor, serta mengintegrasikan model avatar Live2D dengan sistem real audio lip-sync dan antarmuka web interaktif:")

    add_heading_4("1. Penataan Lingkungan Pengembangan dan Struktur Direktori Repositori")
    add_p("Proyek diorganisasikan ke dalam arsitektur repositori modular berbasis Python 3.11 yang dikelola menggunakan manajer paket uv. Struktur direktori proyek pada Visual Studio Code memisahkan secara tegas modul backend (app/), basis pengetahuan dan skrip ingesti (knowledge_base/), aset antarmuka web dan model Live2D (frontend/), proyek model mentah (live2dmodel/), konfigurasi gateway Docker (docker-compose.bifrost.yml), serta berkas pengujian otomatis (tests/).")
    add_figure_placeholder(
        "Gambar 3.10 Struktur Direktori dan Lingkungan Pengembangan Proyek AI-MILO pada VS Code",
        "Screenshot panel Explorer VS Code menampilkan susunan folder app/, frontend/, knowledge_base/, live2dmodel/, tests/, dan berkas konfigurasi proyek"
    )

    add_heading_4("2. Penerapan AI Gateway Bifrost Berbasis Kontainer Docker")
    add_p("Layanan perantara AI Gateway Bifrost dijalankan menggunakan Docker Compose pada port lokal 8080 dengan nama kontainer milo-bifrost-gateway. Konfigurasi ini berfungsi sebagai proksi cerdas antara backend FastAPI dengan server eksternal OpenAI, mengelola kuota pemanggilan (rate limiting 60 req/min), serta menerapkan semantic caching lokal guna mereduksi latensi dan biaya operasional.")
    add_figure_placeholder(
        "Gambar 3.11 Tampilan Eksekusi Kontainer AI Gateway Bifrost (milo-bifrost-gateway) pada Docker Desktop",
        "Screenshot jendela Docker Desktop atau terminal yang menampilkan kontainer milo-bifrost-gateway berstatus Running pada port 8080:8080"
    )

    add_heading_4("3. Realisasi Model Karakter Live2D dan Optimasi Tekstur Atlas")
    add_p("Model karakter \"MILO\" dirancang pada berkas mentah live2dmodel/MILO Model.cmo3 dan diekspor ke format biner WebGL frontend/assets/live2d/MILO Model.moc3 bersama berkas deskriptor MILO Model.model3.json. Tekstur karakter dioptimasi ke dalam dua varian resolusi, yaitu 1024x1024 (texture_clean_1024.png berukuran ~301 KB) untuk efisiensi pemuatan ringan dan 2048x2048 (texture_smooth_2048.png berukuran ~988 KB) untuk tampilan grafis beresolusi tinggi yang tajam.")
    add_figure_placeholder(
        "Gambar 3.12 Struktur Berkas Model Live2D dan Tampilan Rendering pada Kanvas WebGL PIXI.js",
        "Screenshot folder aset frontend/assets/live2d/ (MILO Model.moc3, model3.json, cdi3.json, tekstur) bersanding dengan tampilan avatar ter-render di browser"
    )

    add_heading_4("4. Implementasi Real Audio Lip-Sync Engine dan Perekaman Wicara Dual Mode")
    add_p("Pada sisi antarmuka latihan (frontend/js/milo-live2d.js dan frontend/js/practice.js), pengembang mengintegrasikan pustaka PIXI.js dan Live2D Cubism 4 Core SDK dengan Web Audio API. Aliran audio hasil sintesis TTS dihubungkan ke AudioContext dan AnalyserNode (FFT size 256, smoothing time constant 0.35) untuk mengekstraksi nilai amplitudo secara real-time, lalu diinterpolasi menggunakan lerp smoothing ke parameter ParamMouthOpenY dan ParamMouthForm agar gerak bibir avatar sinkron mengikuti ucapan.")
    add_p("Untuk menangkap suara pengguna, diterapkan dua mode perekaman mikrofon: mode tekan-untuk-bicara (Push-to-Talk) dan algoritma Voice Activity Detection (VAD) otomatis yang menghentikan rekaman saat terdeteksi jeda hening (silence threshold) selama 1200 milidetik, sehingga interaksi percakapan pada ruang latihan berlangsung alami tanpa memotong tuturan pengguna.")
    add_figure_placeholder(
        "Gambar 3.13 Tampilan Antarmuka Practice Studio (practice.html) dengan Avatar Live2D, Kontrol Mikrofon, dan Balon Percakapan",
        "Screenshot halaman http://localhost:8000/practice.html saat sesi latihan berlangsung (menampilkan avatar MILO, tombol mikrofon Push-to-Talk/VAD, dan teks dialog)"
    )

    add_heading_4("5. Pembangunan Kurikulum 18 Modul Microlearning dan Halaman Briefing")
    add_p("Materi kurikulum diekstraksi dan distrukturkan ke dalam berkas frontend/js/curriculum-data.js melalui skrip otomatis scripts/generate_curriculum_data.py. Modul ini memuat 18 topik pembelajaran mandiri (9 modul level B1 dan 9 modul level B2) lengkap dengan bank kosakata, sasaran kompetensi, dan frasa pemantik dialog. Halaman briefing.html dan briefing.js dikembangkan untuk menyajikan panduan pengantar sebelum latihan dimulai guna membangun kesiapan kognitif (cognitive priming) pengguna.")
    add_figure_placeholder(
        "Gambar 3.14 Tampilan Kurikulum 18 Modul Microlearning dan Antarmuka Halaman Briefing Studio",
        "Screenshot halaman pemilihan topik microlearning (pilih_topik_microlearning.html) dan halaman pengantar briefing.html pada peramban web"
    )

    add_heading_4("6. Implementasi Backend FastAPI, Closing Protocol, dan Evaluasi Feedback")
    add_p("Layanan backend dibangun pada app/main.py dan app/api/ menggunakan pola asinkron (async/await). Modul app/core/llm.py mengorkestrasi logika prompt adaptif CEFR serta mengimplementasikan Session Closing Protocol yang secara otomatis mendeteksi batas akhir putaran percakapan untuk menutup sesi secara santun. Hasil percakapan dievaluasi oleh modul app/core/feedback.py untuk menghasilkan laporan koreksi tata bahasa terstruktur, skor performa, perolehan poin XP, dan streak harian yang ditampilkan secara interaktif pada halaman summary.html. Keandalan komponen juga diverifikasi melalui pengujian unit otomatis pada tests/test_live2d_assets.py dan tests/test_closing.py.")
    add_figure_placeholder(
        "Gambar 3.15 Tampilan Halaman Summary Feedback (summary.html) yang Menampilkan Koreksi Tata Bahasa, Skor Performa, dan Poin Gamifikasi",
        "Screenshot halaman http://localhost:8000/summary.html yang menampilkan kartu evaluasi Grammar Breakdown, skor sesi, dan perolehan XP/Streak"
    )

    # 3.3.4 Implementation
    add_heading_3("3.3.4 Implementation (Tahap Penerapan Sistem)")
    add_p("Tahap Implementation merupakan proses penerapan dan pengoperasian seluruh hasil pengembangan sistem ke dalam lingkungan uji coba operasional sehingga platform MILO dapat digunakan secara utuh oleh pengguna sasaran, sebagaimana diilustrasikan pada Gambar 3.16.")
    add_figure_placeholder(
        "Gambar 3.16 Diagram Alur Implementasi dan Penerapan Sistem MILO",
        "Diagram 2 Blok: (1) Lingkungan Operasional (FastAPI Port 8000, Bifrost Port 8080, ChromaDB & SQLite/PostgreSQL) dan (2) Protokol Penerapan ke Responden (Pretest -> Diagnostic Test -> Sesi Intervensi -> Posttest & UEQ)"
    )

    add_heading_4("1. Penerapan Lingkungan Operasional dan Integrasi Layanan")
    add_p("Pada tahap ini dilakukan integrasi menyeluruh antara antarmuka pengguna (frontend), layanan backend, basis data, teknologi Artificial Intelligence (ASR, LLM, RAG, TTS), avatar virtual Live2D, serta mekanisme gamifikasi dalam satu ekosistem berbasis web:")
    add_p("1. Layanan Backend & Antarmuka Web (Port 8000): Server FastAPI dijalankan menggunakan Uvicorn untuk melayani seluruh endpoint REST API wicara, autentikasi JWT, serta menyajikan halaman web interaktif (index.html, login.html, register.html, setup-level.html, setup-goal.html, setup.html, dashboard.html, briefing.html, practice.html, dan summary.html).")
    add_p("2. Layanan AI Gateway Bifrost (Port 8080): Kontainer Docker milo-bifrost-gateway dioperasikan secara paralel untuk menjaga stabilitas permintaan ke OpenAI Whisper, GPT-4o-mini, dan TTS-1 melalui pembatasan laju kueri dan caching semantik.")
    add_p("3. Penyimpanan Relasional & Vektor: Basis data SQLAlchemy ORM dan koleksi vektor ChromaDB diaktifkan secara lokal untuk menyimpan riwayat percakapan, profil level CEFR, hasil evaluasi tata bahasa, poin XP, daily streak, badge, serta catatan telemetri aktivitas pengguna (System Log Analytics).")

    add_heading_4("2. Prosedur Penerapan dan Uji Coba kepada Responden")
    add_p("Setelah sistem beroperasi stabil, platform MILO diterapkan kepada kelompok responden mahasiswa dengan kemampuan bahasa Inggris setara CEFR B1–B2 melalui empat fase terstruktur:")
    add_p("1. Fase Orientasi & Pretest (Baseline): Sebelum menggunakan MILO, responden mengisi kuesioner awal (pretest) student engagement berdasarkan pengalaman mereka menggunakan media latihan berbicara yang biasa digunakan sebagai data pembanding awal (baseline).")
    add_p("2. Fase Registrasi & Diagnostic Placement Test: Responden mengakses platform melalui peramban web, melakukan registrasi akun, dan menjalani tes penempatan awal (setup-level.html) serta memilih target belajar (setup-goal.html) guna memetakan rekomendasi materi level B1 atau B2.")
    add_p("3. Fase Latihan Percakapan Mandiri (Intervensi): Responden menjalankan sesi latihan berbicara interaktif berformat microlearning (3–5 menit per sesi) melalui tahapan briefing.html, practice.html (berinteraksi dengan avatar Live2D via Push-to-Talk atau Smart VAD), hingga meninjau umpan balik pada summary.html selama 3 hingga 5 sesi pertemuan. Selama sesi berlangsung, sistem otomatis merekam frekuensi latihan, durasi, jumlah giliran bicara, akurasi tata bahasa, dan capaian gamifikasi.")
    add_p("4. Fase Posttest & Evaluasi Pengalaman Pengguna: Setelah seluruh sesi latihan selesai, responden kembali mengisi kuesioner student engagement yang sama (posttest) untuk mengukur perubahan keterlibatan belajar, disertai pengisian kuesioner User Experience Questionnaire (UEQ) guna mengevaluasi kenyamanan dan kebergunaan sistem.")

    # 3.3.5 Evaluation
    add_heading_3("3.3.5 Evaluation (Rencana Pengujian Sistem)")
    add_p("Rencana pengujian dalam penelitian ini dirancang secara komprehensif mencakup validasi fungsional, performa kecerdasan buatan, kebergunaan antarmuka, dan efektivitas pedagogis terhadap keterlibatan belajar mahasiswa. Evaluasi dibagi menjadi lima pilar pengujian terukur sebagaimana dijabarkan pada matriks Tabel 3.6:")

    add_table_custom(
        "Tabel 3.6 Matriks Rencana Pengujian Komprehensif Sistem MILO",
        ["No", "Dimensi Pengujian", "Tujuan Pengujian", "Parameter & Instrumen", "Kriteria Keberhasilan / Target"],
        [
            ["1", "Black Box Testing", "Memverifikasi seluruh fitur fungsional berjalan tanpa galat logika atau antarmuka.", "Test cases: Autentikasi, Diagnostic Test, ASR Recording, RAG Retrieval, Live2D Lip-sync, Gamifikasi, Export Feedback.", "100% skenario pengujian berstatus Pass (berhasil tanpa galat kritis)."],
            ["2", "Speech Recognition Testing", "Mengukur akurasi dan ketahanan model Whisper ASR terhadap wicara mahasiswa Indonesia.", "Word Error Rate (WER), transkripsi audio dengan variasi aksen, dan waktu latensi pemrosesan audio.", "Rata-rata WER <= 12.0% dan latensi transkripsi audio < 1.5 detik."],
            ["3", "DeepEval Benchmark (LLM-as-a-Judge)", "Menilai mutu pedagogis dan keabsahan respons RAG serta koreksi tata bahasa secara kuantitatif.", "Metrik Faithfulness (keselarasan konteks), Answer Relevancy, dan akurasi koreksi tata bahasa pada berkas test cases.", "Rata-rata skor Faithfulness >= 0.85 dan Answer Relevancy >= 0.85 (skala 0.0–1.0)."],
            ["4", "User Experience Evaluation (UEQ)", "Mengukur tingkat kepuasan dan kebergunaan antarmuka pengguna secara terstandarisasi.", "Kuesioner UEQ (26 butir item pasangan sifat mencakup 6 skala: Daya Tarik, Kejelasan, Efisiensi, Ketepatan, Stimulasi, dan Kebaruan).", "Seluruh skala UEQ berada pada kategori Above Average atau Good dibanding tolok ukur acuan."],
            ["5", "Student Engagement Evaluation", "Mengukur peningkatan keterlibatan belajar berbicara sebelum dan sesudah menggunakan MILO.", "Kuesioner keterlibatan belajar 3 dimensi (Perilaku, Emosional, Kognitif) skala Likert 1–5, dianalisis via Normalized Gain (N-Gain).", "Peningkatan skor signifikan secara statistik (p < 0.05) dengan nilai g > 0.30 (kategori sedang s.d. tinggi)."]
        ],
        [Inches(0.4), Inches(1.3), Inches(1.5), Inches(1.5), Inches(1.5)]
    )

    add_heading_4("Instrumen Keterlibatan Belajar (Student Engagement)")
    add_p("Pengukuran keterlibatan belajar mengadaptasi model tiga dimensi Phil Hiver dkk. (2021) yang dirinci ke dalam 12 butir indikator pernyataan pada Tabel 3.7.")

    add_table_custom(
        "Tabel 3.7 Indikator Evaluasi Student Engagement Tiga Dimensi",
        ["Dimensi Keterlibatan", "No", "Butir Indikator Pernyataan Angket", "Skala Ukur"],
        [
            ["Keterlibatan Perilaku (Behavioral)", "1\n2\n3\n4", "Saya secara aktif berlatih berbicara bahasa Inggris menggunakan platform ini.\nSaya berusaha menyelesaikan setiap sesi latihan microlearning hingga tuntas.\nSaya terdorong untuk mempertahankan rekor latihan harian (streak).\nSaya memanfaatkan tombol mikrofon berulang kali untuk menyempurnakan ujaran saya.", "Skala Likert 1–5\n(1: Sangat Tidak Setuju,\n5: Sangat Setuju)"],
            ["Keterlibatan Emosional (Emotional)", "5\n6\n7\n8", "Saya merasa lebih percaya diri dan tidak takut salah saat berbicara dengan avatar AI.\nKehadiran avatar virtual Live2D membuat suasana latihan terasa menyenangkan.\nSaya merasa dihargai dengan adanya pemberian poin (XP) dan lencana pencapaian.\nLatihan berbicara melalui platform ini terasa menenangkan dan meredakan rasa cemas saya.", "Skala Likert 1–5"],
            ["Keterlibatan Kognitif (Cognitive)", "9\n10\n11\n12", "Saya memperhatikan dan mempelajari catatan evaluasi grammar yang disajikan sistem.\nSaya mencoba menerapkan rekomendasi frasa alternatif pada sesi percakapan berikutnya.\nTopik latihan yang adaptif mendorong saya berpikir kritis dalam menyusun argumen lisan.\nUmpan balik yang diberikan sistem membantu saya memahami kelemahan berbicara saya secara mandiri.", "Skala Likert 1–5"]
        ],
        [Inches(1.8), Inches(0.5), Inches(2.6), Inches(1.3)]
    )

    add_p("Data skor pretest (S_pre) dan posttest (S_post) keterlibatan belajar dihitung efektivitas peningkatannya menggunakan formulasi Normalized Gain (g) Hake pada Persamaan 3.5:")
    add_equation_box(
        "g = (S_post - S_pre) / (S_max - S_pre)",
        "(Persamaan 3.5)"
    )

    add_p("Kategori perolehan skor ternormalisasi diinterpretasikan sebagai berikut:")
    add_p("• g >= 0.70 : Kategori Peningkatan Tinggi")
    add_p("• 0.30 <= g < 0.70 : Kategori Peningkatan Sedang")
    add_p("• g < 0.30 : Kategori Peningkatan Rendah")

    doc.save(output_path)
    print(f"File DOCX successfully updated at: {output_path}")

if __name__ == "__main__":
    out = os.path.abspath("buku/BAB_3_MILO.docx")
    create_bab3_docx(out)
