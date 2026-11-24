#!/usr/bin/env python3
"""
Script to generate comprehensive Spreadsheet (XLSX and CSV)
for AI-MILO Final Project Progress Tracking (PENS TRM).
"""

import os
import csv
import zipfile
import html

def col_idx_to_name(idx):
    """Convert 0-based column index to Excel column name (e.g. 0 -> A, 1 -> B, 26 -> AA)."""
    name = ""
    while idx >= 0:
        name = chr(ord('A') + (idx % 26)) + name
        idx = (idx // 26) - 1
    return name

def escape_xml(s):
    if s is None:
        return ""
    return html.escape(str(s))

def make_sheet_xml(rows):
    """Generate worksheet XML from list of rows. 
    Each row is a list of values or dicts {'v': val, 'b': bool, 't': 's'/'n'}."""
    xml_parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    xml_parts.append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')
    xml_parts.append('<sheetData>')
    
    for r_idx, row in enumerate(rows, start=1):
        xml_parts.append(f'<row r="{r_idx}">')
        for c_idx, cell in enumerate(row):
            col_letter = col_idx_to_name(c_idx)
            cell_ref = f"{col_letter}{r_idx}"
            
            val = cell
            is_bold = False
            if isinstance(cell, dict):
                val = cell.get('v', '')
                is_bold = cell.get('b', False)
                
            style_idx = "1" if is_bold else "0"
            
            # Check if number
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                xml_parts.append(f'<c r="{cell_ref}" s="{style_idx}"><v>{val}</v></c>')
            else:
                str_val = escape_xml(str(val))
                xml_parts.append(f'<c r="{cell_ref}" t="inlineStr" s="{style_idx}"><is><t>{str_val}</t></is></c>')
        xml_parts.append('</row>')
        
    xml_parts.append('</sheetData>')
    xml_parts.append('</worksheet>')
    return "".join(xml_parts)

def build_xlsx(sheets_data, output_path):
    """Build a multi-sheet XLSX file without external dependencies."""
    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '  <Default Extension="xml" ContentType="application/xml"/>',
        '  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    ]
    for i in range(1, len(sheets_data) + 1):
        content_types.append(f'  <Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
    content_types.append('</Types>')
    
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''

    wb_sheets = []
    wb_rels = []
    for i, (sheet_name, _) in enumerate(sheets_data, start=1):
        wb_sheets.append(f'    <sheet name="{escape_xml(sheet_name)}" sheetId="{i}" r:id="rId{i}"/>')
        wb_rels.append(f'  <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
    wb_rels.append(f'  <Relationship Id="rId{len(sheets_data)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>')

    workbook_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
{chr(10).join(wb_sheets)}
  </sheets>
</workbook>'''

    wb_rels_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{chr(10).join(wb_rels)}
</Relationships>'''

    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><name val="Calibri"/><sz val="11"/></font>
    <font><b/><name val="Calibri"/><sz val="11"/></font>
  </fonts>
  <fills count="2">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
  </fills>
  <borders count="1">
    <border><left/><right/><top/><bottom/><diagonal/></border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="2">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
  </cellXfs>
</styleSheet>'''

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', "\n".join(content_types))
        z.writestr('_rels/.rels', rels)
        z.writestr('xl/workbook.xml', workbook_xml)
        z.writestr('xl/_rels/workbook.xml.rels', wb_rels_xml)
        z.writestr('xl/styles.xml', styles_xml)
        for i, (_, rows) in enumerate(sheets_data, start=1):
            sheet_xml = make_sheet_xml(rows)
            z.writestr(f'xl/worksheets/sheet{i}.xml', sheet_xml)

def main():
    # ── 1. Data Sheet: Ringkasan Progres ──────────────────────────────────────────
    summary_rows = [
        [{'v': "REKAPITULASI PROGRES PROYEK AKHIR AI-MILO", 'b': True}],
        [{'v': "Judul:", 'b': True}, "Asisten Virtual 2D Berbasis OpenAI untuk Meningkatkan Keterlibatan Belajar Berbicara Bahasa Inggris"],
        [{'v': "Nama Pengembang:", 'b': True}, "Siti Maulana Shofiyah (NRP. 5323600043) - PENS TRM"],
        [{'v': "Tanggal Audit:", 'b': True}, "23 November 2026"],
        [],
        [
            {'v': "Research Question", 'b': True},
            {'v': "Fokus Pengembangan", 'b': True},
            {'v': "Bobot (%)", 'b': True},
            {'v': "Skor Progres (%)", 'b': True},
            {'v': "Poin Kontribusi (%)", 'b': True},
            {'v': "Status Evaluasi", 'b': True}
        ],
        [
            "RQ-A",
            "Platform Web & Latihan Mandiri CEFR B1-B2",
            30.0,
            85.0,
            25.50,
            "Sangat Baik (Backend & DB Siap, Tinggal Kalibrasi Bank Soal & Error Handling)"
        ],
        [
            "RQ-B",
            "Core AI Pipeline (Whisper ASR, Hybrid RAG, GPT-4o-mini, TTS, Adaptive Feedback)",
            40.0,
            86.0,
            34.40,
            "Sangat Baik (Integrasi Wicara & RAG Siap, DeepEval Dikecualikan)"
        ],
        [
            "RQ-C",
            "Avatar 2D Live2D, Microlearning, Gamifikasi, & Student Engagement",
            30.0,
            51.25,
            15.38,
            "Perlu Penyempurnaan (Live2D Lip-sync & UI Web Gamifikasi Masih Belum Matang)"
        ],
        [],
        [
            {'v': "TOTAL PROGRES RIIL", 'b': True},
            "",
            {'v': 100.0, 'b': True},
            "",
            {'v': 75.28, 'b': True},
            {'v': "75.28% (~75% - Tahap Integrasi Visual & Finishing Antarmuka)", 'b': True}
        ],
        [],
        [{'v': "CATATAN KHUSUS AUDIT:", 'b': True}],
        ["1.", "Live2D WebGL: Model karakter ter-render & kedipan mata aktif, namun sinkronisasi audio lip-sync nyata masih berupa gelombang sinus dummy (belum terhubung ke Web Audio API)."],
        ["2.", "Microlearning & Gamifikasi: Logika database dan perhitungan kalkulasi poin XP/streak sudah selesai di backend, namun antarmuka visual di web belum dipoles/masih kasar."],
        ["3.", "DeepEval: Sesuai arahan, metrik DeepEval tidak dimasukkan ke dalam penilaian persentase ini; fokus pada keandalan fungsional pipeline."]
    ]

    # ── 2. Data Sheet: RQ-A Platform & Latihan Mandiri ──────────────────────────
    rqa_rows = [
        [{'v': "DETAIL BREAKDOWN PERTANYAAN A (RQ-A)", 'b': True}],
        [{'v': "Pertanyaan:", 'b': True}, "Bagaimana merancang dan mengembangkan platform pembelajaran berbicara bahasa Inggris berbasis asisten virtual yang interaktif dan mendukung latihan mandiri bagi pembelajar level B1-B2?"],
        [],
        [
            {'v': "No", 'b': True},
            {'v': "Komponen / Fitur", 'b': True},
            {'v': "Detail Kebutuhan Spesifik (Sistem, DB, Logika, UI)", 'b': True},
            {'v': "Kondisi Nyata di Repositori Saat Ini", 'b': True},
            {'v': "Bobot (%)", 'b': True},
            {'v': "Progres (%)", 'b': True},
            {'v': "Kontribusi (%)", 'b': True},
            {'v': "Status", 'b': True},
            {'v': "Alasan / Rationale Pemberian Persentase", 'b': True}
        ],
        [
            1,
            "Sistem Autentikasi & Akun Pengguna",
            "DB: Tabel users (email, hashed_password, cefr_level, is_active). Backend: app/api/auth.py (Bcrypt, JWT token). UI: login.html, register.html dengan validasi form.",
            "Backend lengkap, tabel DB ada, halaman login dan register berfungsi baik menangani sesi token.",
            25.0,
            90.0,
            22.50,
            "Selesai (Done)",
            "(+75%) DB, backend, dan UI dasar selesai. (-10%) Tinggal pembersihan session expiry otomatis di frontend jika token kedaluwarsa."
        ],
        [
            2,
            "Diagnostic Placement Test (B1 vs B2)",
            "DB: Tabel placement_test_results (skor 4 domain: grammar, vocab, discourse, pragmatics). Logika: Formula bobot 0.40 Sg + 0.35 Sv + 0.25 Sf. UI: setup-level.html (alur tes interaktif).",
            "Skema DB di models.py siap. Endpoint /api/placement siap. Antarmuka setup-level.html tersedia.",
            25.0,
            85.0,
            21.25,
            "Selesai (Done)",
            "(+75%) Model DB dan endpoint perhitungan level bekerja. (-15%) Perlu kalibrasi variasi butir soal tes wicara agar membedakan level B1 dan B2 lebih tajam."
        ],
        [
            3,
            "Manajemen Sesi Latihan Mandiri",
            "DB: Tabel sessions (user_id, topic, cefr_level, is_active, waktu mulai/selesai). Logika: Inisialisasi sesi, isolasi riwayat percakapan. UI: briefing.html (panduan sebelum sesi).",
            "Tabel sessions berelasi dengan users. Endpoint pembuatan & penutupan sesi aktif di app/api/chat.py. Halaman briefing.html terhubung.",
            25.0,
            85.0,
            21.25,
            "Selesai (Done)",
            "(+75%) Manajemen sesi di backend & alur navigasi halaman terhubung. (-15%) Belum ada fitur auto-save pemulihan jika koneksi internet terputus di tengah sesi."
        ],
        [
            4,
            "Dashboard Pembelajaran Mandiri",
            "DB: Query riwayat dari tabel sessions dan learning_progress. Backend: Endpoint ringkasan profil & aktivitas. UI: dashboard.html (kartu level, riwayat latihan, ringkasan skor).",
            "Tampilan dashboard.html memiliki layout kartu level, tabel riwayat percakapan, dan penampil skor rata-rata.",
            25.0,
            80.0,
            20.00,
            "Selesai (Done)",
            "(+70%) Data riwayat sesi dan level berhasil ditarik dari DB. (-20%) Visualisasi grafik perkembangan skor longitudinal harian belum menggunakan chart visual."
        ],
        [],
        [
            {'v': "RATA-RATA PROGRES RQ-A", 'b': True},
            "",
            "",
            "",
            {'v': 100.0, 'b': True},
            {'v': 85.0, 'b': True},
            {'v': 85.00, 'b': True},
            "",
            {'v': "Kontribusi terhadap Proyek Akhir: 85% x 30% = 25.50%", 'b': True}
        ]
    ]

    # ── 3. Data Sheet: RQ-B Core AI Pipeline ───────────────────────────────────
    rqb_rows = [
        [{'v': "DETAIL BREAKDOWN PERTANYAAN B (RQ-B)", 'b': True}],
        [{'v': "Pertanyaan:", 'b': True}, "Bagaimana mengintegrasikan teknologi Artificial Intelligence (AI) berbasis Large Language Model (LLM), Retrieval-Augmented Generation (RAG), Automatic Speech Recognition (ASR), dan Text-to-Speech (TTS) untuk menghasilkan sistem pembelajaran berbicara bahasa Inggris yang mampu memberikan umpan balik pembelajaran secara adaptif?"],
        [{'v': "Catatan:", 'b': True}, "Pengujian DeepEval tidak dimasukkan ke dalam penilaian persentase; fokus murni pada kesiapan teknis fungsional pipeline."],
        [],
        [
            {'v': "No", 'b': True},
            {'v': "Komponen / Fitur", 'b': True},
            {'v': "Detail Kebutuhan Spesifik (Sistem, DB, Logika, UI)", 'b': True},
            {'v': "Kondisi Nyata di Repositori Saat Ini", 'b': True},
            {'v': "Bobot (%)", 'b': True},
            {'v': "Progres (%)", 'b': True},
            {'v': "Kontribusi (%)", 'b': True},
            {'v': "Status", 'b': True},
            {'v': "Alasan / Rationale Pemberian Persentase", 'b': True}
        ],
        [
            1,
            "Automatic Speech Recognition (Whisper ASR)",
            "Sistem: Web Audio capture (16kHz mono). Backend: app/core/asr.py & app/api/voice.py (Whisper API). UI: Push-to-Talk button & visualizer audio waveform.",
            "Audio direkam via browser, dikirim ke /api/v1/voice/transcribe, dan ditranskripsi oleh Whisper.",
            20.0,
            85.0,
            17.00,
            "Selesai (Done)",
            "(+75%) Perekaman audio dan transkripsi berjalan lancar. (-15%) Penanganan noise lingkungan & silence detection masih manual (tekan-lepas tombol)."
        ],
        [
            2,
            "Hybrid RAG Knowledge Base",
            "Data: Obsidian Markdown silabus CEFR B1-B2 (knowledge_base/). Sistem: ChromaDB vector store + BM25 index. Logika: Ingestion chunker (500 char), ranking RRF (k=60).",
            "18 berkas silabus tersedia, skrip knowledge_base/ingest.py jalan, penelusuran hibrida RRF di app/core/rag.py siap.",
            20.0,
            90.0,
            18.00,
            "Selesai (Done)",
            "(+90%) Seluruh materi terindeks, pengambilan konteks semantik dan leksikal berfungsi optimal. (-10%) Variasi percakapan spesifik per topik masih bisa diperkaya."
        ],
        [
            3,
            "Conversational LLM Dialogue Manager",
            "Logika: GPT-4o-mini prompt scaffolding, 'The One-Question Rule', penyesuaian leksikogramatikal B1 vs B2. Infrastruktur: Bifrost Gateway (Docker 8080) / direct OpenAI.",
            "Prompt di app/core/llm.py sudah menerapkan aturan 1 pertanyaan di akhir kalimat dan batasan level CEFR B1-B2.",
            20.0,
            90.0,
            18.00,
            "Selesai (Done)",
            "(+90%) Respon tutor kontekstual dan menjaga alur dialog interaktif. (-10%) Perlu pengujian ketahanan terhadap masukan teks di luar topik materi (out-of-domain)."
        ],
        [
            4,
            "Speech Synthesis (OpenAI TTS)",
            "Backend: app/core/tts.py (OpenAI TTS-1 profil suara 'nova'). UI/Audio: Pemutar audio streaming otomatis di peramban setelah respon LLM diterima.",
            "Sintesis suara bekerja, audio MP3 dialirkan ke klien dan diputar di browser pada practice.js.",
            20.0,
            85.0,
            17.00,
            "Selesai (Done)",
            "(+75%) Suara jernih dan responsif. (-15%) Belum ada opsi kontrol kecepatan audio (playback rate: 0.8x / 1.0x) bagi pembelajar pemula."
        ],
        [
            5,
            "Adaptive Feedback Engine",
            "DB: Kolom feedback (JSON) di tabel messages. Logika: Ekstraksi kesalahan grammar, kategori eror, penjelasan pedagogis, dan kalkulasi kelancaran (WPM). UI: Kartu koreksi real-time & summary.html.",
            "app/core/feedback.py menghasilkan struktur JSON koreksi grammar. Data tersimpan di DB dan muncul di summary.",
            20.0,
            80.0,
            16.00,
            "Selesai (Done)",
            "(+70%) Deteksi eror dan saran perbaikan kalimat berjalan akurat di backend. (-20%) Tampilan kartu koreksi saat dialog langsung masih kaku dan butuh polesan tipografi."
        ],
        [],
        [
            {'v': "RATA-RATA PROGRES RQ-B", 'b': True},
            "",
            "",
            "",
            {'v': 100.0, 'b': True},
            {'v': 86.0, 'b': True},
            {'v': 86.00, 'b': True},
            "",
            {'v': "Kontribusi terhadap Proyek Akhir: 86% x 40% = 34.40%", 'b': True}
        ]
    ]

    # ── 4. Data Sheet: RQ-C Live2D, Microlearning, Gamifikasi ───────────────────
    rqc_rows = [
        [{'v': "DETAIL BREAKDOWN PERTANYAAN C (RQ-C)", 'b': True}],
        [{'v': "Pertanyaan:", 'b': True}, "Bagaimana penerapan avatar virtual dua dimensi (2D), microlearning, dan gamifikasi dalam platform pembelajaran berbicara bahasa Inggris dapat meningkatkan keterlibatan belajar (student engagement) pengguna?"],
        [],
        [
            {'v': "No", 'b': True},
            {'v': "Komponen / Fitur", 'b': True},
            {'v': "Detail Kebutuhan Spesifik (Sistem, DB, Logika, UI)", 'b': True},
            {'v': "Kondisi Nyata di Repositori Saat Ini", 'b': True},
            {'v': "Bobot (%)", 'b': True},
            {'v': "Progres (%)", 'b': True},
            {'v': "Kontribusi (%)", 'b': True},
            {'v': "Status", 'b': True},
            {'v': "Alasan / Rationale Pemberian Persentase", 'b': True}
        ],
        [
            1,
            "Avatar 2D Live2D WebGL & Real Lip-Sync",
            "Render: Live2D Cubism Web SDK di kanvas HTML5. Animasi: Kedipan mata (ParamEyeLOpen/R), gaze tracking. Audio Lip-Sync: Web Audio API AnalyserNode -> RMS amplitudo -> ParamMouthOpenY.",
            "Model MILO muncul di kanvas web, gerakan mata dan kedipan aktif. Namun lip-sync belum terhubung ke audio analyzer nyata (masih rumus sinus dummy).",
            25.0,
            45.0,
            11.25,
            "In Progress",
            "(+30%) Render 2D sukses, model termuat, kedip mata & idle jalan. (-55%) Lip-sync audio nyata belum selesai: mulut belum sinkron mengikuti gelombang audio wicara TTS."
        ],
        [
            2,
            "Modul Microlearning Flow & Stepper",
            "Pedagogi: Sesi dibatasi 3-5 menit (6-10 putaran dialog) dengan 1 sasaran spesifik. Backend: Topik ter-chunk kecil + mini kuis. UI: Visual turn stepper ('Putaran 3 dari 8') & timer sesi.",
            "Backend memuat 18 topik ringkas dan ada kuis penutup. Namun antarmuka web belum memiliki visual stepper/timer yang elegan.",
            25.0,
            50.0,
            12.50,
            "In Progress",
            "(+35%) Logika materi ringkas & bank kuis ada di backend. (-50%) UI web belum mencerminkan microlearning: belum ada stepper progres dialog dan transisi antar halaman masih kaku."
        ],
        [
            3,
            "Mekanisme Gamifikasi (XP, Streak, Badges)",
            "DB: Tabel user_gamification (points, current_streak) & user_badges. Logika Backend: Perhitungan poin kuis, penambahan streak harian, pembukaan badge. UI/UX: Widget streak api, bar XP dinamis, rak badge interaktif, pop-up perayaan.",
            "Tabel DB dan kalkulasi perhitungan poin/streak di backend sudah bekerja 100%. Namun tampilan web masih sangat sederhana / belum tertata menarik.",
            25.0,
            45.0,
            11.25,
            "In Progress",
            "(+35%) Logika database & perhitungan backend selesai 100%. (-55%) Tampilan antarmuka web belum bagus: widget masih polosan, belum ada animasi perolehan poin atau pop-up lencana baru."
        ],
        [
            4,
            "Pengukuran Student Engagement (Riset Empiris)",
            "DB: Tabel system_log_analytics & evaluation_surveys. Instrumen: Angket 3 dimensi Phil Hiver dkk. (Behavioral, Emotional, Cognitive). Metode: Desain pretest-posttest N=32 via N-Gain Hake.",
            "Skema database perekam log dan penampung survei sudah ada di models.py. Kuesioner terdefinisi di buku. Data eksperimen responden sedang dihimpun.",
            25.0,
            65.0,
            16.25,
            "In Progress",
            "(+50%) Tabel database analitik dan instrumen ukur sudah siap. (-35%) Pengisian kuesioner riil oleh seluruh responden dan rekapitulasi data final Bab 4 masih berjalan."
        ],
        [],
        [
            {'v': "RATA-RATA PROGRES RQ-C", 'b': True},
            "",
            "",
            "",
            {'v': 100.0, 'b': True},
            {'v': 51.25, 'b': True},
            {'v': 51.25, 'b': True},
            "",
            {'v': "Kontribusi terhadap Proyek Akhir: 51.25% x 30% = 15.38%", 'b': True}
        ]
    ]

    # ── 5. Data Sheet: Action Plan & To-Do List ────────────────────────────────
    todo_rows = [
        [{'v': "ROADMAP & PRIORITAS PENYELESAIAN (TARGET 100%)", 'b': True}],
        [{'v': "Panduan langkah konkret untuk menuntaskan sisa 24.72% pengerjaan Proyek Akhir AI-MILO:", 'b': True}],
        [],
        [
            {'v': "No", 'b': True},
            {'v': "Tugas Pengembangan", 'b': True},
            {'v': "Fokus Komponen", 'b': True},
            {'v': "Target Kenaikan Progres", 'b': True},
            {'v': "Berkas Terkait", 'b': True},
            {'v': "Tingkat Prioritas", 'b': True},
            {'v': "Status Tindakan", 'b': True}
        ],
        [
            1,
            "Implementasi Real Audio Lip-Sync Live2D",
            "Hubungkan HTML5 Audio TTS ke Web Audio API AnalyserNode, hitung RMS volume, dan petakan ke ParamMouthOpenY.",
            "+10.0% (Mendongkrak RQ-C ke 85%)",
            "frontend/js/milo-live2d.js",
            "Prioritas 1 (Kritis)",
            "Siap Dikerjakan"
        ],
        [
            2,
            "Polesan Antarmuka Visual Gamifikasi",
            "Desain widget streak (ikon api menyala), progress bar XP level, rak lencana aktif, dan modal pop-up perayaan.",
            "+10.0% (Mendongkrak RQ-C ke 85%)",
            "frontend/dashboard.html, summary.html, css/",
            "Prioritas 1 (Kritis)",
            "Siap Dikerjakan"
        ],
        [
            3,
            "Penerapan Visual Stepper Microlearning",
            "Tambahkan komponen stepper interaktif ('Turn X of Y') dan session timer pada practice.html.",
            "+5.0% (Menyempurnakan alur latihan)",
            "frontend/practice.html, practice.js",
            "Prioritas 2 (Tinggi)",
            "Siap Dikerjakan"
        ],
        [
            4,
            "Rekapitulasi Data Responden (N=32)",
            "Lengkapi input data respons survei ke tabel evaluation_surveys dan hitung formula N-Gain Hake.",
            "+5.0% (Menuntaskan Bab 4 riset)",
            "app/api/evaluation.py, buku/BUKU_PROGRES_PA_AI_MILO.md",
            "Prioritas 2 (Tinggi)",
            "Menunggu Data"
        ],
        [
            5,
            "Penggantian Placeholder Gambar Bab 3 & 4",
            "Ganti placeholder [TEMPATKAN GAMBAR DI SINI] pada buku laporan dengan tangkapan layar sistem asli.",
            "+3.0% (Finishing Naskah Buku PA)",
            "buku/BUKU_PROGRES_PA_AI_MILO.md",
            "Prioritas 3 (Sedang)",
            "Setelah UI Matang"
        ]
    ]

    # Build XLSX
    xlsx_path = os.path.abspath("buku/PROGRES_PA_AI_MILO.xlsx")
    sheets_data = [
        ("Ringkasan Progres", summary_rows),
        ("RQ-A Platform Mandiri", rqa_rows),
        ("RQ-B Core AI Pipeline", rqb_rows),
        ("RQ-C Live2D & Gamifikasi", rqc_rows),
        ("Action Plan & To-Do", todo_rows)
    ]
    build_xlsx(sheets_data, xlsx_path)
    print(f"XLSX created at: {xlsx_path}")

    # Build CSV Master (Universal CSV with UTF-8 BOM)
    csv_path = os.path.abspath("buku/PROGRES_PA_AI_MILO.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        
        # Write Summary
        writer.writerow(["=== REKAPITULASI PROGRES PROYEK AKHIR AI-MILO ==="])
        for row in summary_rows[1:]:
            writer.writerow([cell.get('v') if isinstance(cell, dict) else cell for cell in row])
        writer.writerow([])
        writer.writerow([])

        # Write RQ-A
        writer.writerow(["=== DETAIL BREAKDOWN PERTANYAAN A (RQ-A) ==="])
        for row in rqa_rows[1:]:
            writer.writerow([cell.get('v') if isinstance(cell, dict) else cell for cell in row])
        writer.writerow([])
        writer.writerow([])

        # Write RQ-B
        writer.writerow(["=== DETAIL BREAKDOWN PERTANYAAN B (RQ-B) ==="])
        for row in rqb_rows[1:]:
            writer.writerow([cell.get('v') if isinstance(cell, dict) else cell for cell in row])
        writer.writerow([])
        writer.writerow([])

        # Write RQ-C
        writer.writerow(["=== DETAIL BREAKDOWN PERTANYAAN C (RQ-C) ==="])
        for row in rqc_rows[1:]:
            writer.writerow([cell.get('v') if isinstance(cell, dict) else cell for cell in row])
        writer.writerow([])
        writer.writerow([])

        # Write Action Plan
        writer.writerow(["=== ROADMAP & ACTION PLAN ==="])
        for row in todo_rows[1:]:
            writer.writerow([cell.get('v') if isinstance(cell, dict) else cell for cell in row])
            
    print(f"Master CSV created at: {csv_path}")

    # Build Individual Sheet CSVs for easy Google Sheets multi-tab import
    sheets_dir = os.path.abspath("buku/sheets")
    os.makedirs(sheets_dir, exist_ok=True)
    file_names = [
        "01_Ringkasan_Progres.csv",
        "02_RQA_Platform_Mandiri.csv",
        "03_RQB_Core_AI_Pipeline.csv",
        "04_RQC_Live2D_Gamifikasi.csv",
        "05_Action_Plan_Roadmap.csv"
    ]
    for filename, (sheet_title, sheet_rows) in zip(file_names, sheets_data):
        tab_path = os.path.join(sheets_dir, filename)
        with open(tab_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for row in sheet_rows:
                writer.writerow([cell.get('v') if isinstance(cell, dict) else cell for cell in row])
        print(f"Individual CSV: {filename}")


if __name__ == '__main__':
    main()
