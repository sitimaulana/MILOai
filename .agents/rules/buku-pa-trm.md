# Standar Penulisan Buku Progres & Proyek Akhir TRM PENS (AI-MILO)

Pedoman ini mengikat seluruh agen AI dalam menyusun, mengedit, dan melengkapi dokumen akademik (Buku Progres Sidang maupun Buku Laporan Akhir) untuk Proyek Akhir Program Studi Sarjana Terapan Teknologi Rekayasa Multimedia (TRM), Jurusan Teknologi Multimedia Kreatif, Politeknik Elektronika Negeri Surabaya (PENS).

---

## 1. Struktur Bab Wajib (5 Bab Standar PENS)
- **Bab 1 Pendahuluan**:
  - *Latar Belakang*: Wajib menguraikan Problem Domain (urgensi pendidikan/speaking proficiency Indonesia, IELTS gap, EF EPI), Problem (*foreign language speaking anxiety* dan keterbatasan media praktik mandiri), dan Uniqueness (integrasi asisten virtual 2D Live2D + multimodal AI).
  - *Permasalahan*: Dirumuskan dalam butir-butir terukur (desain platform, integrasi pipeline AI, dan efektivitas terhadap student engagement).
  - *Batasan Masalah*: Membatasi ruang lingkup sistem secara tegas (web platform, CEFR B1–B2, Whisper ASR, ChromaDB RAG, GPT-4o-mini, OpenAI TTS, Live2D).
  - *Tujuan*: **Wajib diawali formulasi kalimat pembuka baku**:
    > *"Penelitian proyek akhir ini mengajukan suatu pendekatan baru untuk mengatasi [Problem] dengan menggunakan / mengintegrasikan [Uniqueness / Solusi]..."*  
    Diikuti kalimat argumentatif fitur-fitur unik solusi.
  - *Manfaat*: Merinci kontribusi bagi pembelajar/mahasiswa, institusi PENS, dan bidang rekayasa multimedia interaktif (HCI).
  - *Sistematika Penulisan*: Tabel ringkasan muatan Bab 1 sampai Bab 5.
- **Bab 2 Kajian Pustaka**:
  - *Deskripsi Permasalahan*: Mengulas secara mendalam kondisi pembelajar, siklus kecemasan (*Cycle of Fear* Rahmat), target CEFR B1 vs B2, keterbatasan media yang ada (Duolingo, ChatGPT umum), serta diagram kesenjangan kebutuhan vs realitas media.
  - *Teori Penunjang*: Membahas tuntas AI, ML, DL, NLP, ASR Whisper, Neural TTS, Conversational AI, Transformer & LLM GPT-4o-mini, RAG & Vector Store ChromaDB, Live2D & Persona Effect, CLT & Corrective Feedback, Microlearning, Gamifikasi, Student Engagement 3 dimensi Phil Hiver dkk. (Behavioral, Emotional, Cognitive), serta Model ADDIE.
  - *Penelitian Terkait*: Tabel komparasi matriks penelitian terdahulu dengan identifikasi celah penelitian (*research gap*) yang diisi oleh penelitian ini.
- **Bab 3 Desain Sistem**:
  - *Deskripsi Solusi*: Penjelasan sistem MILO dan alur pengguna (*User Flow Diagram*).
  - *Perancangan Sistem*: Menggunakan pendekatan arsitektur berlapis (*Layered Architecture*: Presentation, API, Core AI, Storage).
  - Membahas detail Bagian 1 (Input/Diagnostic), Bagian 2 (Core RAG & LLM), Bagian 3 (Output TTS & Live2D Lip-sync), dan Bagian 4 (Gamifikasi & Microlearning).
  - *Formulasi Matematis*: Wajib memuat persamaan matematis baku (misal: Cosine Similarity RAG dan Weighted Scoring).
  - *Desain Antarmuka*: Alur wireframe dan high-fidelity mockup (Placement, Dashboard, Sesi Live2D, Feedback).
  - *Perancangan Basis Data*: Skema tabel relasional SQLAlchemy ORM.
- **Bab 4 Eksperimen dan Analisis**:
  - *Parameter Eksperimen*: 4 pilar pengujian (Black Box, DeepEval Benchmark LLM-as-a-Judge, Usability UEQ, dan Student Engagement Pretest-Posttest).
  - *Karakteristik Data, Tempat, Waktu, dan Spesifikasi Peralatan* (Hardware & Software).
  - *Hasil Eksperimen*: Tabel pengujian fungsionalitas, skor kuantitatif DeepEval (*Faithfulness*, *Answer Relevancy*, akurasi koreksi), skor 6 skala UEQ, dan rekapitulasi data responden N=32 dengan perhitungan Normalized Gain (*N-Gain* Hake).
  - *Analisis Hasil Eksperimen*: Menghubungkan temuan kuantitatif dan kualitatif kembali ke rumusan masalah dan pereduksian speaking anxiety.
- **Bab 5 Penutup**:
  - *Kesimpulan*: Menjawab langsung seluruh rumusan masalah.
  - *Saran*: Rekomendasi perbaikan teknis dan penelitian masa depan (ASR/TTS lokal, aksen Indonesia, mobile PWA).
- **Daftar Pustaka**:
  - Wajib menggunakan standar format sitasi IEEE berurutan `[1]`, `[2]`, `[3]`.

---

## 2. Invarian Teknis AI-MILO
Setiap pemaparan sistem harus selaras dengan implementasi nyata pada repositori `AI-MILO`:
1. **ASR**: OpenAI Whisper (ekstraksi spektrogram audio 16 kHz).
2. **Knowledge Base & RAG**: Markdown files di `knowledge_base/` (Obsidian Vault) diindeks ke ChromaDB dengan embedding `text-embedding-3-small`.
3. **LLM**: GPT-4o-mini melalui *Bifrost AI Gateway* (token budgeting, rate-limiting, caching).
4. **TTS & Avatar**: OpenAI TTS-1 (*voice: nova*) disinkronisasi ke Live2D parameter mulut (*ParamMouthOpenY*) dan ekspresi mata/kepala.
5. **Database**: PostgreSQL / SQLite dikelola melalui SQLAlchemy async ORM (`app/db/models.py`).
6. **Evaluasi Otomatis**: Framework DeepEval (`evaluations/run_evaluation.py`) untuk metrik *Faithfulness* dan *Answer Relevancy*.

---

## 3. Format Penulisan Baku
- Judul Gambar: `Gambar [Bab].[Nomor] [Keterangan]` (Center, tebal, 1 baris kosong sebelum dan sesudah).
- Judul Tabel: `Tabel [Bab].[Nomor] [Keterangan]` (Center, tebal, di atas tabel).
- Persamaan Matematis: Rata kiri dengan indentasi, nomor identitas `(Persamaan [Bab].[Nomor])` rata kanan tebal.
- Sumber sitasi pada kutipan gambar/tabel diletakkan di bawah gambar/tabel ukuran 10pt.
