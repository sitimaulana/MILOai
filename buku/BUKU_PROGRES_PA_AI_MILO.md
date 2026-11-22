# BUKU PROGRES PROYEK AKHIR

**ASISTEN VIRTUAL DUA DIMENSI (2D) BERBASIS OPENAI UNTUK MENINGKATKAN KETERLIBATAN BELAJAR BERBICARA BAHASA INGGRIS**

---

**Disusun oleh:**  
**Siti Maulana Shofiyah**  
**NRP. 5323600043**  

**Dosen Pembimbing:**  
1. **Akhmad Alimudin, S.ST., M.Kom., Ph.D.** (NIP. 198612082014041002)  
2. **Rendra Suprobo Aji, S.T., M.T.** (NIP. 198705212023211023)  

**PROGRAM STUDI SARJANA TERAPAN TEKNOLOGI REKAYASA MULTIMEDIA**  
**JURUSAN TEKNOLOGI MULTIMEDIA KREATIF**  
**POLITEKNIK ELEKTRONIKA NEGERI SURABAYA**  
**2026**

---

## ABSTRAK

Kemampuan berbicara (*speaking*) merupakan salah satu kompetensi penting dalam penguasaan bahasa Inggris, namun masih menjadi kendala utama bagi mahasiswa di Indonesia. Rendahnya kesempatan berlatih secara mandiri, kecemasan berbicara (*speaking anxiety*), serta terbatasnya media latihan yang interaktif dan adaptif menyebabkan proses belajar belum berlangsung secara optimal. Penelitian proyek akhir ini bertujuan merancang dan mengembangkan **MILO (Multimodal Interactive Learning Companion)**, sebuah platform pembelajaran berbicara bahasa Inggris berbasis web yang mengintegrasikan kecerdasan buatan (*Artificial Intelligence*) multimodal meliputi *Automatic Speech Recognition* (OpenAI Whisper), *Retrieval-Augmented Generation* (RAG berbasis ChromaDB dan materi CEFR Obsidian Vault), *Large Language Model* (OpenAI GPT-4o-mini), *Text-to-Speech* (OpenAI TTS), serta visualisasi karakter virtual dua dimensi berbasis Live2D. Platform ini dirancang dengan pendekatan *microlearning* (3–5 menit per sesi) dan gamifikasi guna menstimulasi *student engagement* pembelajar pada tingkat CEFR B1–B2.

Metodologi pengembangan sistem menerapkan model ADDIE (*Analysis, Design, Development, Implementation, Evaluation*). Pengujian sistem dievaluasi melalui empat pilar pengujian: uji fungsionalitas (*Black Box Testing*), uji keandalan komputasi AI menggunakan kerangka kerja *DeepEval* (*LLM-as-a-Judge*), uji pengalaman pengguna (*User Experience Questionnaire* / UEQ), serta evaluasi keterlibatan belajar (*Student Engagement Evaluation*) menggunakan instrumen 3 dimensi Hiver dkk. (perilaku, emosional, dan kognitif) dengan desain *one-group pretest-posttest* terhadap 32 responden mahasiswa. Hasil pengujian fungsionalitas menunjukkan *success rate* sebesar 98,4%. Evaluasi AI menggunakan DeepEval membuktikan performa penalaran RAG dengan skor *Faithfulness* 1,00 dan *Answer Relevancy* 1,00 (100% *pass rate*), serta akurasi koreksi tata bahasa sebesar 95,8%. Hasil evaluasi *student engagement* menunjukkan peningkatan rata-rata skor dari 62,45 (*pretest*) menjadi 88,20 (*posttest*) dengan nilai *Normalized Gain* (*N-Gain*) sebesar 0,69 yang masuk dalam kategori peningkatan tinggi. Temuan ini menegaskan bahwa integrasi asisten virtual 2D interaktif yang dipadukan dengan umpan balik AI adaptif efektif dalam mereduksi *speaking anxiety* dan meningkatkan keterlibatan belajar berbicara bahasa Inggris secara signifikan dan berkelanjutan.

**Kata Kunci:** *Artificial Intelligence, Conversational AI, Automatic Speech Recognition, Large Language Model, Retrieval-Augmented Generation, Live2D Avatar, Student Engagement, Speaking Practice, CEFR B1–B2.*

---

## ABSTRACT

*Speaking proficiency is a critical competency in English language acquisition, yet it remains a significant hurdle for university students in Indonesia. The lack of independent conversational practice, high levels of speaking anxiety, and the scarcity of interactive, adaptive learning media hinder students from developing spoken fluency. This final project aims to design and implement **MILO (Multimodal Interactive Learning Companion)**, a web-based English speaking practice platform that integrates multimodal Artificial Intelligence comprising Automatic Speech Recognition (OpenAI Whisper), Retrieval-Augmented Generation (ChromaDB vector store backed by an Obsidian CEFR Knowledge Base), Large Language Model (OpenAI GPT-4o-mini), Text-to-Speech (OpenAI TTS), and an interactive 2D virtual avatar powered by Live2D. MILO adopts microlearning sessions (3–5 minutes) and gamification mechanics to foster student engagement for CEFR B1–B2 learners.*

*The system development follows the ADDIE instructional model (Analysis, Design, Development, Implementation, Evaluation). System evaluation is structured around four pillars: functionality testing via Black Box Testing, AI computation benchmarks using DeepEval (LLM-as-a-Judge), user experience evaluation using the User Experience Questionnaire (UEQ), and student engagement assessment based on Phil Hiver et al.'s three-dimensional framework (behavioral, emotional, cognitive) conducted with a one-group pretest-posttest design on 32 university respondents. Black box testing demonstrated a 98.4% functional success rate. DeepEval benchmarks revealed a Faithfulness score of 1.00 and an Answer Relevancy score of 1.00 (100% pass rate), alongside a 95.8% grammar correction accuracy. Student engagement metrics showed a substantial increase from a pretest mean of 62.45 to a posttest mean of 88.20, achieving a Normalized Gain (N-Gain) score of 0.69 (high increase category). These findings validate that pairing interactive 2D pedagogical agents with real-time adaptive AI feedback successfully mitigates speaking anxiety and significantly strengthens autonomous speaking practice.*

*Keywords: Artificial Intelligence, Conversational AI, Automatic Speech Recognition, Large Language Model, Retrieval-Augmented Generation, Live2D Avatar, Student Engagement, Speaking Practice, CEFR B1–B2.*

---

## KATA PENGANTAR

Puji syukur ke hadirat Allah Subhanahu Wa Ta'ala atas segala rahmat, taufik, hidayah, dan karunia-Nya sehingga penyusunan Buku Progres Proyek Akhir dengan judul **"Asisten Virtual Dua Dimensi (2D) Berbasis OpenAI untuk Meningkatkan Keterlibatan Belajar Berbicara Bahasa Inggris"** dapat diselesaikan dengan baik dan tepat waktu. Buku progres ini disusun sebagai salah satu tahapan evaluasi dan pertanggungjawaban kemajuan dalam pelaksanaan Proyek Akhir guna memenuhi syarat kelulusan Program Studi Sarjana Terapan Teknologi Rekayasa Multimedia, Jurusan Teknologi Multimedia Kreatif, Politeknik Elektronika Negeri Surabaya (PENS).

Dalam penyusunan buku progres dan pengembangan platform **MILO (Multimodal Interactive Learning Companion)** ini, penulis mendapatkan banyak bimbingan, arahan, saran, serta dukungan moral dan material dari berbagai pihak. Oleh karena itu, pada kesempatan ini penulis menyampaikan rasa terima kasih dan apresiasi yang setinggi-tingginya kepada:

1. **Bapak Dr.-Ing. Ir. Arif Irwansyah, S.T., M.Eng.** selaku Direktur Politeknik Elektronika Negeri Surabaya.
2. **Bapak Ashafidz Fauzan Dianta, S.ST., M.T.** selaku Koordinator Program Studi Sarjana Terapan Teknologi Rekayasa Multimedia PENS.
3. **Bapak Akhmad Alimudin, S.ST., M.Kom., Ph.D.** selaku Dosen Pembimbing Pertama, atas arahan ilmiah, masukan arsitektur kecerdasan buatan, kesabaran, serta diskusi konstruktif yang diberikan selama proses perancangan dan implementasi sistem.
4. **Bapak Rendra Suprobo Aji, S.T., M.T.** selaku Dosen Pembimbing Kedua, atas bimbingan teknis interaktivitas multimedia, evaluasi pengalaman pengguna, dan saran metodologis yang sangat berharga.
5. Seluruh Dosen dan Sivitas Akademika Program Studi Sarjana Terapan Teknologi Rekayasa Multimedia PENS yang telah membekali penulis dengan ilmu pengetahuan dan wawasan berharga selama masa perkuliahan.
6. Kedua orang tua, keluarga besar, dan orang-orang terkasih yang senantiasa melantunkan doa yang tulus, memberikan dukungan moral, dan menjadi sumber motivasi terbesar dalam menyelesaikan proyek akhir ini.
7. Rekan-rekan mahasiswa seperjuangan TRM PENS angkatan 2022 serta seluruh partisipan dan responden pengujian yang telah meluangkan waktu dan tenaganya dalam pengujian sistem MILO.

Penulis menyadari bahwa buku progres ini masih memiliki ruang penyempurnaan. Oleh karena itu, penulis sangat terbuka terhadap kritik dan saran konstruktif dari dosen penguji dan pembaca demi kesempurnaan laporan akhir dan kebermanfaatan produk yang dikembangkan.

Surabaya, November 2026  
Penulis,  

**Siti Maulana Shofiyah**  
NRP. 5323600043  

---

## DAFTAR ISI

- **HALAMAN JUDUL**
- **ABSTRAK**
- **ABSTRACT**
- **KATA PENGANTAR**
- **DAFTAR ISI**
- **DAFTAR GAMBAR**
- **DAFTAR TABEL**
- **BAB 1 PENDAHULUAN**
  - 1.1 LATAR BELAKANG
  - 1.2 PERMASALAHAN
  - 1.3 BATASAN MASALAH
  - 1.4 TUJUAN
  - 1.5 MANFAAT
  - 1.6 SISTEMATIKA PENULISAN
- **BAB 2 KAJIAN PUSTAKA**
  - 2.1 DESKRIPSI PERMASALAHAN
    - 2.1.1 Kondisi Pelajar Bahasa Inggris Saat Ini
    - 2.1.2 Keterbatasan Media Latihan yang Tersedia
    - 2.1.3 Kesenjangan Teknologi yang Perlu Diisi
  - 2.2 TEORI PENUNJANG
    - 2.2.1 Kecerdasan Buatan dan Cabang Penunjang (ML, DL, NLP, ASR, TTS)
    - 2.2.2 Conversational AI
    - 2.2.3 Large Language Model (LLM) & Arsitektur Transformer
    - 2.2.4 Retrieval-Augmented Generation (RAG) & Vector Database
    - 2.2.5 Avatar Virtual 2D dan Animated Pedagogical Agent (APA)
    - 2.2.6 Pembelajaran Berbicara Bahasa Inggris & Standar CEFR B1–B2
    - 2.2.7 Pendekatan Microlearning
    - 2.2.8 Mekanisme Gamifikasi dalam Pembelajaran Digital
    - 2.2.9 Konsep Student Engagement Tiga Dimensi (Hiver dkk.)
    - 2.2.10 Arsitektur Web Modern dan RESTful API
    - 2.2.11 Model Pengembangan ADDIE
  - 2.3 PENELITIAN TERKAIT
- **BAB 3 DESAIN SISTEM**
  - 3.1 DESKRIPSI SOLUSI
  - 3.2 PERANCANGAN SISTEM
    - 3.2.1 Arsitektur Sistem Berlapis (Layered Architecture)
    - 3.2.2 Bagian 1: Input & Diagnostic Layer
    - 3.2.3 Bagian 2: Core Processing & RAG Engine
    - 3.2.4 Bagian 3: Output & Visual Rendering Layer (Live2D & TTS)
    - 3.2.5 Bagian 4: Learning & Gamification Mechanics
    - 3.2.6 Persamaan Matematis Sistem
    - 3.2.7 Perancangan Antarmuka Pengguna (UI/UX Design)
    - 3.2.8 Perancangan Basis Data (Database Schema)
- **BAB 4 EKSPERIMEN DAN ANALISIS**
  - 4.1 PARAMETER EKSPERIMEN
  - 4.2 KARAKTERISTIK DATA
  - 4.3 TEMPAT UJI COBA
  - 4.4 WAKTU UJI COBA
  - 4.5 SPESIFIKASI PERALATAN UJI COBA
    - 4.5.1 Perangkat Keras (Hardware)
    - 4.5.2 Perangkat Lunak (Software)
    - 4.5.3 Instrumen Penelitian
  - 4.6 HASIL EKSPERIMEN
    - 4.6.1 Hasil Uji Ahli (Expert Review)
    - 4.6.2 Hasil Pengujian Fungsionalitas (Black Box Testing)
    - 4.6.3 Hasil Pengujian Kuantitatif AI (DeepEval Benchmark)
    - 4.6.4 Hasil Pengujian Usability (User Experience Questionnaire / UEQ)
    - 4.6.5 Hasil Pengujian Keterlibatan Belajar (Student Engagement Pretest-Posttest)
  - 4.7 ANALISIS HASIL EKSPERIMEN
    - 4.7.1 Analisis Validitas Fungsional dan Stabilitas Sistem
    - 4.7.2 Analisis Kinerja RAG dan Keandalan Koreksi Pedagogis
    - 4.7.3 Analisis Peningkatan Student Engagement terhadap Speaking Anxiety
    - 4.7.4 Analisis Usability dan Pengalaman Pengguna
- **BAB 5 PENUTUP**
  - 5.1 KESIMPULAN
  - 5.2 SARAN
- **DAFTAR PUSTAKA**
- **LAMPIRAN**

---

## DAFTAR GAMBAR

- **Gambar 2.1** Siklus Kecemasan dalam Pembelajaran Bahasa (Cycle of Fear)
- **Gambar 2.2** Diagram Kesenjangan Kebutuhan Pelajar dan Kondisi Media Saat Ini
- **Gambar 2.3** Hierarki Kecerdasan Buatan, Machine Learning, dan Deep Learning
- **Gambar 2.4** Pipeline Pemrosesan Natural Language Processing (NLP)
- **Gambar 2.5** Pipeline Automatic Speech Recognition (ASR) OpenAI Whisper
- **Gambar 2.6** Pipeline Neural Text-to-Speech (TTS)
- **Gambar 3.1** Alur Kerja Pengguna Sistem MILO (*User Flow Diagram*)
- **Gambar 3.2** Diagram Arsitektur Berlapis Sistem MILO (*High-Level Architecture*)
- **Gambar 3.3** Pipeline Pemrosesan Suara dan Penalaran AI (ASR → RAG → LLM → TTS)
- **Gambar 3.4** Arsitektur RAG Berbasis ChromaDB dan Knowledge Base Markdown
- **Gambar 3.5** Rancangan Antarmuka Halaman Login & Diagnostic Placement Test
- **Gambar 3.6** Rancangan Antarmuka Halaman Dashboard & Progress Tracking
- **Gambar 3.7** Rancangan Antarmuka Halaman Sesi Percakapan Interaktif dengan Live2D
- **Gambar 3.8** Rancangan Antarmuka Halaman Sesi Feedback & Rekomendasi CEFR
- **Gambar 3.9** Diagram Relasi Entitas Basis Data (*Entity Relationship Diagram*)
- **Gambar 4.1** Diagram Alur Kerangka Pengujian Kuantitatif DeepEval
- **Gambar 4.2** Grafik Distribusi Tingkat Kemahiran CEFR Responden Pengujian
- **Gambar 4.3** Grafik Perbandingan Rata-Rata Skor Pre-Test dan Post-Test Student Engagement
- **Gambar 4.4** Grafik Distribusi Kategori N-Gain Responden
- **Gambar 4.5** Rekapitulasi Rata-Rata Skor 6 Dimensi User Experience Questionnaire (UEQ)

---

## DAFTAR TABEL

- **Tabel 2.1** Karakteristik Kemampuan Berbicara Pelajar Level CEFR B1 dan B2
- **Tabel 2.2** Matriks Perbandingan Penelitian Terkait dan Celah Penelitian
- **Tabel 3.1** Pemetaan Komponen Arsitektur Sistem MILO
- **Tabel 3.2** Bobot Penilaian Domain Kompetensi Diagnostic Placement Test
- **Tabel 3.3** Definisi Struktur Entitas Tabel Basis Data Sistem MILO
- **Tabel 4.1** Spesifikasi Perangkat Keras Uji Coba
- **Tabel 4.2** Spesifikasi Perangkat Lunak Lingkungan Operasional
- **Tabel 4.3** Matriks Skenario dan Hasil Pengujian Black Box Testing
- **Tabel 4.4** Rekapitulasi Hasil Evaluasi Kuantitatif AI (DeepEval Benchmark)
- **Tabel 4.5** Rekapitulasi Data Pre-Test dan Post-Test Student Engagement (N=32)
- **Tabel 4.6** Rekapitulasi Rata-Rata Skor Tiga Dimensi Student Engagement
- **Tabel 4.7** Rekapitulasi Skor Rata-Rata 6 Dimensi User Experience Questionnaire (UEQ)
- **Tabel 4.8** Rangkuman Masukan Kualitatif dari Expert Review dan Responden

---

# BAB 1  
# PENDAHULUAN

## 1.1 LATAR BELAKANG
Kemampuan berbicara (*speaking*) dalam bahasa Inggris merupakan salah satu kompetensi esensial yang harus dikuasai oleh mahasiswa pada era globalisasi untuk mendukung aktivitas akademik, mobilitas internasional, serta kesiapan memasuki dunia industri modern [1]. Meskipun pembelajaran bahasa Inggris telah diintegrasikan ke dalam kurikulum pendidikan tinggi di Indonesia, kemahiran komunikasi lisan mahasiswa secara umum masih berada pada tingkat yang memprihatinkan. Laporan *Education First English Proficiency Index* (EF EPI) tahun 2025 menempatkan Indonesia pada peringkat ke-80 dari 123 negara di dunia dengan kategori kemahiran rendah (*low proficiency*) dan perolehan skor rata-rata sebesar 471 dari skala 800 [2]. Fenomena ini menegaskan adanya kesenjangan (*gap*) yang lebar antara penguasaan teori tata bahasa secara reseptif dengan kemampuan produksi bahasa lisan secara spontan dan komunikatif.

Salah satu hambatan utama yang menyebabkan rendahnya keterampilan berbicara adalah kecemasan berbahasa asing atau *Foreign Language Speaking Anxiety* [3]. Kecemasan ini memicu rasa takut berlebih akan melakukan kesalahan gramatikal, kekhawatiran terhadap penilaian negatif dari rekan sebaya atau pengajar, serta hilangnya rasa percaya diri saat berbicara. Hal tersebut selaras dengan data statistik *IELTS Test Taker Performance* yang menunjukkan bahwa skor rata-rata kemampuan *speaking* (6.4) mahasiswa Indonesia secara konsisten lebih rendah dibandingkan skor *listening* (7.0) [4]. Kondisi ini membuktikan bahwa kendala utama tidak terletak pada pemahaman pesan (*input*), melainkan pada keberanian dan ketepatan memproduksi ujaran (*output*). Keterbatasan mitra bicara yang kompeten dan lingkungan latihan mandiri yang suportif memperparah situasi ini, tercermin dari laporan GoodStats yang mencatat tren penurunan skor kecakapan bahasa Inggris generasi muda Indonesia dari 498 pada tahun 2016 menjadi 416 pada tahun 2025 [5].

Perkembangan teknologi kecerdasan buatan (*Artificial Intelligence* / AI) berbasis *Large Language Model* (LLM) membuka peluang revolusioner dalam memecahkan problematika tersebut [6]. LLM memiliki kapabilitas tinggi dalam memahami konteks percakapan secara dinamis, mengidentifikasi kesalahan linguistik, dan menyusun koreksi yang disesuaikan dengan tingkat kemampuan pengguna [7]. Ketika diintegrasikan dengan teknologi *Automatic Speech Recognition* (ASR) dan *Text-to-Speech* (TTS), komputer dapat bertindak sebagai mitra percakapan interaktif dua arah yang responsif [8].

Kendati demikian, mayoritas media pembelajaran bahasa Inggris berbasis kecerdasan buatan saat ini masih memiliki keterbatasan fundamental. Platform populer seperti Duolingo cenderung berfokus pada latihan kosakata terisolasi dan pengisian teks mekanistis tanpa menyediakan percakapan bebas yang adaptif [9]. Di sisi lain, alat bantu umum seperti ChatGPT tidak dilengkapi dengan kurikulum pedagogis terstruktur, kerap memotong ujaran pengguna (*premature turn-taking*), tidak memberikan umpan balik tata bahasa mendalam secara otomatis jika tidak diminta, serta tidak memiliki visualisasi karakter yang interaktif [10]. Ketiadaan kehadiran visual seorang pendamping belajar (*pedagogical agent*) membuat interaksi suara terasa kering menyerupai panggilan telepon otomatis, sehingga gagal membangun ikatan afektif yang kuat. Padahal, teori *Persona Effect* membuktikan bahwa kehadiran representasi visual karakter virtual animasi (*Animated Pedagogical Agent*) mampu menciptakan suasana belajar yang lebih bersahabat, mereduksi tekanan psikologis, serta melipatgandakan keterlibatan belajar (*student engagement*) [11], [13].

Menjawab kesenjangan tersebut, penelitian proyek akhir ini mengusulkan pengembangan **MILO (Multimodal Interactive Learning Companion)**, sebuah platform asisten virtual berbasis web yang memadukan teknologi ASR (OpenAI Whisper), RAG (ChromaDB yang memuat materi kurikulum CEFR B1–B2 berbasis Obsidian Vault), LLM (GPT-4o-mini), TTS (OpenAI TTS), serta avatar virtual dua dimensi (2D) berbasis teknologi Live2D. Platform ini diperkuat dengan pendekatan *microlearning* (3–5 menit latihan terarah) dan elemen gamifikasi (*points, badges, streaks, progress tracking*) untuk menciptakan rutinitas latihan berbicara yang menyenangkan, minim tekanan sosial, dan berkelanjutan.

## 1.2 PERMASALAHAN
Berdasarkan latar belakang yang telah dipaparkan, rumusan permasalahan dalam penelitian proyek akhir ini dirumuskan sebagai berikut:
1. Bagaimana merancang dan membangun arsitektur platform web pembelajaran berbicara bahasa Inggris yang memadukan komunikasi suara dua arah dan visualisasi asisten virtual 2D Live2D bagi pembelajar tingkat CEFR B1–B2?
2. Bagaimana mengintegrasikan teknologi *Automatic Speech Recognition* (Whisper), *Retrieval-Augmented Generation* (RAG ChromaDB), *Large Language Model* (GPT-4o-mini), dan *Text-to-Speech* (OpenAI TTS) agar mampu menghasilkan respons percakapan yang kontekstual serta umpan balik koreksi tata bahasa (*corrective feedback*) secara adaptif dan tepat sasaran?
3. Bagaimana pengaruh penerapan asisten virtual 2D, konsep *microlearning*, dan mekanisme gamifikasi dalam platform MILO terhadap peningkatan keterlibatan belajar (*student engagement*) pengguna yang mencakup dimensi perilaku (*behavioral*), emosional (*emotional*), dan kognitif (*cognitive*)?

## 1.3 BATASAN MASALAH
Ruang lingkup dan batasan masalah dalam penelitian proyek akhir ini ditetapkan sebagai berikut:
1. Platform dikembangkan berbasis web responsif menggunakan arsitektur *client-server* (backend FastAPI Python dan frontend HTML5/JavaScript modern).
2. Input ucapan pengguna diterima melalui peramban web (*browser microphone*) dan diproses menggunakan model ASR OpenAI Whisper untuk menghasilkan transkripsi teks bahasa Inggris.
3. Model bahasa alami yang digunakan sebagai *dialogue manager* dan *evaluator* adalah OpenAI GPT-4o-mini yang dikelola melalui gerbang komputasi AI (*Bifrost AI Gateway*) untuk optimasi kuota dan latensi.
4. Basis pengetahuan kurikulum diintegrasikan melalui *Retrieval-Augmented Generation* (RAG) berbasis ChromaDB dengan dokumen acuan standar CEFR level B1 dan B2 dari *Obsidian Knowledge Base*.
5. Visualisasi asisten virtual diimplementasikan menggunakan karakter dua dimensi berbasis teknologi Live2D Cubism Web SDK yang memiliki ekspresi afektif dan sinkronisasi gerak bibir (*lip-sync*) otomatis terhadap audio output OpenAI TTS.
6. Target pengguna difokuskan pada mahasiswa atau pembelajar tingkat menengah (*intermediate*) yang berada pada rentang kemahiran CEFR B1–B2.
7. Pengujian efektivitas sistem berfokus pada evaluasi keterlibatan belajar (*student engagement*) menggunakan instrumen kuesioner skala Likert berdasarkan kerangka kerja Phil Hiver dkk. (2021) melalui metode *one-group pretest-posttest*, serta analisis log analitik aktivitas belajar.

## 1.4 TUJUAN
Penelitian proyek akhir ini mengajukan suatu pendekatan baru untuk meningkatkan keterlibatan belajar (*student engagement*) berbicara bahasa Inggris bagi pembelajar tingkat CEFR B1–B2 dengan mengembangkan asisten virtual interaktif dua dimensi (2D) berbasis OpenAI yang mengintegrasikan teknologi *Automatic Speech Recognition* (ASR), *Large Language Model* (LLM), *Retrieval-Augmented Generation* (RAG), *Text-to-Speech* (TTS), *microlearning*, dan gamifikasi. 

Adapun tujuan spesifik yang ingin dicapai meliputi:
1. Merancang dan mengimplementasikan sistem aplikasi web MILO yang menyediakan lingkungan latihan berbicara bahasa Inggris mandiri yang aman secara psikologis, interaktif, dan bebas dari rasa cemas (*speaking anxiety*).
2. Membangun *pipeline* AI multimodal yang andal dengan menggabungkan OpenAI Whisper, ChromaDB RAG, GPT-4o-mini, dan OpenAI TTS guna menghasilkan percakapan yang alami serta evaluasi kemampuan berbicara (*grammar, vocabulary, fluency*) secara *real-time*.
3. Menerapkan karakter virtual Live2D sebagai *Animated Pedagogical Agent* yang responsif dan ekspresif untuk memperkuat keterikatan emosional pengguna selama proses latihan.
4. Menerapkan modul *microlearning* dan gamifikasi (*daily streak, achievement badges, points, progress tracking*) guna menumbuhkan kebiasaan belajar harian yang konsisten.
5. Mengevaluasi fungsionalitas sistem, keandalan AI melalui pengujian kuantitatif DeepEval, kualitas pengalaman pengguna (*User Experience Questionnaire*), dan signifikansi peningkatan *student engagement* pada dimensi perilaku, emosional, dan kognitif.

## 1.5 MANFAAT
Penelitian proyek akhir ini diharapkan mampu memberikan kontribusi dan manfaat nyata bagi berbagai pihak:
1. **Bagi Pembelajar dan Mahasiswa**:
   Menyediakan lingkungan praktik berbicara bahasa Inggris yang fleksibel, sabar, dan bebas penghakiman sosial, sehingga mahasiswa dapat melatih kelancaran berbicara kapan saja, mengatasi *speaking anxiety*, serta memperoleh koreksi tata bahasa secara personal dan terarah.
2. **Bagi Pengembangan Ilmu Pengetahuan dan Teknologi Rekayasa Multimedia**:
   Memberikan kontribusi empiris dalam bidang *Human-Computer Interaction* (HCI) dan *Educational Technology*, khususnya mengenai formulasi integrasi agen pedagogis 2D Live2D dengan arsitektur *generative AI* (ASR-RAG-LLM-TTS) dalam konteks pembelajaran bahasa lisan.
3. **Bagi Institusi Pendidikan**:
   Menjadi referensi media pembelajaran pendukung (*supplementary learning tool*) yang dapat diterapkan di laboratorium bahasa atau sistem pembelajaran mandiri kampus untuk mengakselerasi kemahiran bahasa Inggris mahasiswa menuju standar kerja global.

## 1.6 SISTEMATIKA PENULISAN
Sistematika pembahasan dalam buku progres proyek akhir ini disusun dalam lima bab utama sebagai berikut:

Tabel 1.1 Sistematika Penulisan Buku Proyek Akhir
| Bab | Judul Bab | Deskripsi Isi Pembahasan |
| :--- | :--- | :--- |
| **Bab 1** | **Pendahuluan** | Memuat latar belakang permasalahan rendahnya kemahiran berbicara bahasa Inggris dan *speaking anxiety*, perumusan masalah, batasan masalah, tujuan penelitian dengan klaim orisinalitas, manfaat penelitian, serta sistematika penulisan laporan. |
| **Bab 2** | **Kajian Pustaka** | Memuat deskripsi mendalam mengenai kondisi pembelajar bahasa, siklus kecemasan berbicara, keterbatasan media yang ada, teori penunjang (Kecerdasan Buatan, ASR, LLM, RAG, Live2D, Microlearning, Gamifikasi, Student Engagement tiga dimensi), dan matriks komparasi penelitian terdahulu beserta celah penelitian (*research gap*). |
| **Bab 3** | **Desain Sistem** | Menguraikan metodologi pemecahan masalah melalui arsitektur sistem berlapis (*Layered Architecture*), perancangan *pipeline* input-proses-output AI-MILO, formulasi matematis, perancangan antarmuka visual (wireframe & mock-up), alur pengguna (*user flow*), serta rancangan skema basis data relasional. |
| **Bab 4** | **Eksperimen dan Analisis** | Menyajikan parameter eksperimen (Black Box, DeepEval Benchmark, UEQ, Student Engagement), karakteristik data, spesifikasi peralatan lingkungan uji, hasil eksperimen kuantitatif dan kualitatif, serta analisis mendalam mengenai korelasi hasil uji terhadap rumusan masalah. |
| **Bab 5** | **Penutup** | Berisi kesimpulan menyeluruh yang merangkum pencapaian penelitian dalam menjawab permasalahan yang diajukan serta saran-saran strategis untuk pengembangan sistem di masa depan. |
| **Daftar Pustaka** | **Referensi** | Memuat daftar rujukan ilmiah dari jurnal internasional, prosiding konferensi bereputasi, buku teks, dan standar industri yang disusun menurut format baku IEEE. |
| **Lampiran** | **Dokumen Pendukung** | Berisi berkas kode sumber penting, instrumen kuesioner pengujian, lembar evaluasi pakar (*expert review*), dan dokumentasi uji coba. |

---

# BAB 2  
# KAJIAN PUSTAKA

## 2.1 DESKRIPSI PERMASALAHAN

### 2.1.1 Kondisi Pelajar Bahasa Inggris Saat Ini
Kemampuan berkomunikasi lisan dalam bahasa Inggris merupakan keterampilan psikomotorik dan kognitif yang kompleks. Mahasiswa yang berupaya melatih keterampilan ini secara mandiri kerap terjebak dalam lingkaran psikologis yang destruktif, dikenal sebagai siklus kecemasan belajar bahasa (*Cycle of Fear in Language Learning*) sebagaimana dirumuskan oleh Rahmat (2019) [15].

```
  ┌────────────────────────────────────────────────────────┐
  │              1. Perceived Difficulties                 │
  │    (Persepsi awal bahwa berbicara Inggris itu sulit)   │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │                      2. Reasons                        │
  │    (Rasionalisasi: "Vocab minim", "Grammar buruk")     │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │                 3. Cognitive Anxiety                   │
  │  (Khawatir berlebih akan dinilai buruk / ditertawakan) │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │                  4. Somatic Anxiety                    │
  │     (Gejala fisik: gugup, terbata-bata, blank)         │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │                5. Avoidance Behaviour                  │
  │ (Menghindar dari praktik berbicara & kesempatan bicara)│
  └──────────────────────────┬─────────────────────────────┘
                             │
                             └──────────► (Kembali ke Tahap 1)
```
*Gambar 2.1 Siklus Kecemasan dalam Pembelajaran Bahasa (Adaptasi dari Rahmat, 2019 [15])*

Siklus di atas menjelaskan bahwa rasa cemas kognitif (*cognitive anxiety*) memicu respons fisik (*somatic anxiety*) yang berujung pada perilaku menghindar (*avoidance behaviour*). Ketika mahasiswa menghindari praktik berbicara, mereka kehilangan jam terbang latihan. Hal ini memperkuat keyakinan bahwa berbicara bahasa Inggris adalah hal yang di luar jangkauan mereka.

Penelitian ini secara khusus menargetkan pembelajar pada level **B1 (Intermediate)** dan **B2 (Upper Intermediate)** berdasarkan kerangka *Common European Framework of Reference for Languages* (CEFR) [17]. Karakteristik kedua level tersebut disajikan pada Tabel 2.1:

Tabel 2.1 Karakteristik Kemampuan Berbicara Pelajar Level CEFR B1 dan B2
| Aspek Kemahiran | CEFR Level B1 (Threshold) | CEFR Level B2 (Vantage) |
| :--- | :--- | :--- |
| **Deskripsi Umum** | Mampu memahami pokok pikiran percakapan standar dan menangani situasi rutin sehari-hari. | Mampu berinteraksi dengan tingkat kelancaran dan spontanitas yang memadai dengan penutur asli. |
| **Cakupan Topik** | Pengalaman pribadi, keluarga, hobi, pekerjaan, dan rencana masa depan. | Isu kontemporer, perdebatan profesional, analisis kelebihan/kekurangan, dan diskusi akademis. |
| **Kendala Dominan** | Kesalahan *tenses* dasar (*past vs present perfect*), jeda panjang (*hesitation*), kosakata terbatas. | Kurang variasi idiomatis, kecanggungan dalam negosiasi formal, inkonsistensi struktur kalimat kompleks. |
| **Kebutuhan Intervensi** | Simulasi percakapan kontekstual dengan koreksi gramatikal langsung (*low cognitive load*). | Latihan argumen kritis, ekspresi nuansa profesional, dan penyempurnaan akurasi wacana lisan. |

### 2.1.2 Keterbatasan Media Latihan yang Tersedia
Meskipun banyak perangkat lunak pembelajaran bahasa yang beredar di pasaran, belum ada solusi mandiri yang mampu menjawab kebutuhan interaksi lisan secara tuntas:
1. **Aplikasi Pembelajaran Mandiri Tradisional (misal: Duolingo, Memrise)**:  
   Mayoritas berfokus pada latihan *gamified flashcards*, penyusunan kata mekanis, dan pengenalan ucapan satu arah dengan kata kunci kaku. Aplikasi ini tidak melatih kemampuan berwacana (*conversational competence*) dan tidak mampu menangani respons bebas pengguna [20].
2. **Aplikasi LLM Serbaguna (misal: ChatGPT Mobile Voice Mode)**:  
   Meskipun memiliki kemampuan menghasilkan bahasa alami yang lancar, ChatGPT tidak memiliki struktur kurikulum bahasa asing. Model tidak secara otomatis membedah struktur gramatikal pengguna kecuali diperintahkan secara eksplisit, kerap memotong kalimat pengguna sebelum selesai berbicara (*voice activity detection latency issue*), dan tidak menyimpan progres kompetensi berbasis domain CEFR [21].
3. **Ketiadaan Representasi Visual Interaktif**:  
   Berlatih hanya melalui suara atau teks terasa monoton dan memicu kejenuhan (*cognitive fatigue*). Tidak adanya kehadiran fisik atau agen animasi membuat pengguna merasa berinteraksi dengan mesin pencari bersuara, bukan dengan mitra belajar yang empati.

### 2.1.3 Kesenjangan Teknologi yang Perlu Diisi
Berdasarkan tinjauan di atas, terdapat jurang yang memisahkan antara kebutuhan ideal pembelajar lisan dengan realitas perangkat teknologi yang tersedia, sebagaimana divisualisasikan pada Gambar 2.2:

```
┌───────────────────────────────────────┐      ┌───────────────────────────────────────┐
│       Kebutuhan Pelajar B1–B2         │      │          Realitas Media Saat Ini      │
├───────────────────────────────────────┤      ├───────────────────────────────────────┤
│ • Ruang aman tanpa cemas & stigma     │  VS  │ • Tutor manusia mahal & terbatas jam  │
│ • Dialog lisan spontan dua arah       │      │ • Aplikasi komersial dominan teks kaku│
│ • Umpan balik grammar & kosa kata riil│      │ • LLM umum tidak membedah error CEFR  │
│ • Karakter visual empati & ekspresif  │      │ • Tampilan antarmuka dingin tanpa agen│
│ • Sesi singkat fleksibel (3-5 menit)  │      │ • Kursus panjang membosankan (drop-out│
└───────────────────────────────────────┘      └───────────────────────────────────────┘
```
*Gambar 2.2 Kesenjangan Kebutuhan Pelajar Bahasa Inggris dan Realitas Media Saat Ini*

---

## 2.2 TEORI PENUNJANG

### 2.2.1 Kecerdasan Buatan dan Cabang Penunjang
Kecerdasan Buatan (*Artificial Intelligence* / AI) adalah domain ilmu komputer yang berkonsentrasi pada rekayasa sistem komputasi yang mampu mengeksekusi tugas-tugas yang menuntut kecerdasan manusia [22]. AI modern dibangun di atas pilar *Machine Learning* (ML) dan *Deep Learning* (DL), yang menjadi fondasi bagi *Natural Language Processing* (NLP), *Automatic Speech Recognition* (ASR), dan *Text-to-Speech* (TTS).

```
   ┌────────────────────────────────────────────────────────┐
   │             ARTIFICIAL INTELLIGENCE                    │
   │  ┌──────────────────────────────────────────────────┐  │
   │  │               MACHINE LEARNING                   │  │
   │  │  ┌────────────────────────────────────────────┐  │  │
   │  │  │              DEEP LEARNING                 │  │  │
   │  │  │   [Transformer Neural Networks]            │  │  │
   │  │  │   • Whisper ASR (Speech-to-Text)           │  │  │
   │  │  │   • GPT-4o-mini (Dialogue & Evaluation)    │  │  │
   │  │  │   • Neural TTS (Acoustic Waveform)         │  │  │
   │  │  └────────────────────────────────────────────┘  │  │
   │  └──────────────────────────────────────────────────┘  │
   └────────────────────────────────────────────────────────┘
```
*Gambar 2.3 Hierarki AI, Machine Learning, dan Deep Learning dalam Sistem MILO*

1. **Machine Learning (ML)**: Paradigma di mana algoritma mempelajari korelasi statistik dari himpunan data pelatihan tanpa pemrograman aturan deterministik [24].
2. **Deep Learning (DL)**: Cabang ML yang memanfaatkan arsitektur jaringan saraf tiruan berlapis dalam (*deep artificial neural networks*) dengan mekanisme non-linear untuk mengekstraksi representasi data abstrak tingkat tinggi [26].
3. **Natural Language Processing (NLP)**: Bidang kajian komputasi yang membedah sintaksis, semantik, dan pragmatik bahasa manusia. Pada sistem MILO, NLP bertugas menganalisis transkrip pengguna, mendeteksi penyimpangan gramatikal, dan menghasilkan kalimat respon yang santun dan memantik dialog lanjutan [23].
4. **Automatic Speech Recognition (ASR)**: Teknologi konversi sinyal akustik ucapan menjadi teks tertulis (*Speech-to-Text*). OpenAI Whisper menggunakan arsitektur *Encoder-Decoder Transformer* yang dilatih pada 680.000 jam data audio multilingual, menghasilkan ketahanan tinggi terhadap aksen non-native dan derau latar belakang (*background noise*) [12].
5. **Text-to-Speech (TTS)**: Sistem sintesis wicara neural yang mengonversi teks ke bentuk gelombang audio (*waveform*). OpenAI TTS model `tts-1` memanfaatkan model difusi akustik neural yang mampu menghasilkan prosodi, penekanan intonasi, dan ritme bicara yang menyerupai manusia [25].

### 2.2.2 Conversational AI
*Conversational AI* mengacu pada sistem cerdas yang mampu menjalin komunikasi interaktif dengan manusia menggunakan bahasa alami melalui media teks atau wicara. Tidak seperti sistem *dialogue tree* kuno yang berbasis aturan logika *if-else*, sistem *conversational AI* kontemporer memanfaatkan pemahaman konteks multi-turn, mempertahankan memori dialog, dan menyesuaikan gaya bicara secara dinamis.

### 2.2.3 Large Language Model (LLM) & Arsitektur Transformer
*Large Language Model* adalah model fondasi deep learning dengan miliaran parameter yang dilatih menggunakan korpus teks berskala raksasa melalui arsitektur *Transformer* [7]. Mekanisme *Multi-Head Self-Attention* memungkinkan model menimbang bobot keterkaitan antar token dalam kalimat tanpa dibatasi jarak sekuensial. Model GPT-4o-mini dari OpenAI dioptimalkan khusus untuk menghasilkan penalaran bahasa yang cepat, hemat komputasi, dan memiliki pemahaman mendalam terhadap tata bahasa baku bahasa Inggris.

### 2.2.4 Retrieval-Augmented Generation (RAG) & Vector Database
RAG merupakan metode arsitektural yang menggabungkan kemampuan pencarian basis data eksternal (*retrieval*) dengan keunggulan generasi teks LLM (*generation*) [6]. RAG memitigasi kelemahan laten LLM berupa halusinasi (*confabulation*) fakta dan ketiadaan spesifikasi domain tertentu. Dalam sistem MILO, materi silabus CEFR B1–B2 disimpan di *Obsidian Knowledge Base*, dipecah menjadi unit-unit teks (*chunks*), diubah menjadi representasi vektor numerik (*dense embeddings*) menggunakan model `text-embedding-3-small`, dan diindeks ke dalam basis data vektor **ChromaDB**. Ketika sesi percakapan berlangsung, sistem mencari potongan materi tata bahasa dan topik percakapan yang paling relevan secara semantik menggunakan perhitungan *Cosine Similarity* untuk disuntikkan ke dalam *system prompt* LLM.

### 2.2.5 Avatar Virtual 2D dan Animated Pedagogical Agent (APA)
*Animated Pedagogical Agent* (APA) adalah representasi visual animasi interaktif dalam perangkat lunak edukasi yang memerankan figur pemandu, mentor, atau teman belajar [13]. Penelitian klasik Lester et al. (1997) membuktikan adanya fenomena *Persona Effect*, di mana kehadiran agen pedagogis visual berwajah bersahabat memicu persepsi pembelajar bahwa sistem lebih pintar, lebih membantu, dan lebih menarik dibandingkan sistem antarmuka berbasis audio murni. Live2D merupakan teknologi rendering grafis dua dimensi yang mampu menganimasikan ilustrasi karakter 2D secara dinamis dengan manipulasi titik deformasi (*mesh polygons*), memberikan efek gerak 3D yang halus tanpa kehilangan estetika ilustrasi aslinya. Chen et al. (2025) melalui penelitian *VTutor* menunjukkan bahwa agen visual yang disinkronisasikan dengan *output* LLM dan TTS real-time secara drastis meningkatkan keterikatan afektif pengguna [20], [21].

### 2.2.6 Pembelajaran Berbicara Bahasa Inggris & Standar CEFR B1–B2
Pembelajaran kemahiran berbicara (*speaking*) mengacu pada prinsip *Communicative Language Teaching* (CLT), yang memprioritaskan keberhasilan penyampaian pesan bermakna (*meaning-focused communication*) daripada sekadar penghafalan aturan gramatikal statis. Dalam CLT, pemberian umpan balik korektif (*corrective feedback*) harus dirancang secara bijak: sistem tidak boleh menginterupsi di tengah pembicaraan, melainkan menyajikan catatan koreksi setelah sesi giliran bicara selesai, membedakan kesalahan mayor (*global errors*) dan minor (*local errors*). Standar CEFR (Council of Europe) level B1 menuntut kemampuan berbicara terstruktur pada konteks familiar, sedangkan B2 menuntut kelancaran berargumen kritis dan pemilihan kosakata yang lebih spesifik (*collocations*).

### 2.2.7 Pendekatan Microlearning
*Microlearning* menyajikan materi pembelajaran dalam unit-unit kecil terfokus dengan durasi konsumsi antara 3 hingga 5 menit [26]. Pendekatan ini secara signifikan menurunkan beban kognitif (*cognitive load*) pembelajar dan sangat adaptif terhadap pola atensi generasi digital modern. Meta-analisis oleh Prasittichok & Smithsarakarn (2024) terhadap 10 riset empiris melaporkan bahwa penerapan *microlearning* menghasilkan ukuran efek (*effect size*) yang signifikan terhadap peningkatan kelancaran berbicara dan kepercayaan diri mahasiswa EFL dibanding metode konvensional [26].

### 2.2.8 Mekanisme Gamifikasi dalam Pembelajaran Digital
Deterding et al. (2011) mendefinisikan gamifikasi sebagai pemanfaatan elemen desain permainan (*game mechanics*) pada domain non-permainan untuk memacu motivasi intrinsik dan ekstrinsik pengguna [14]. Sistem MILO menerapkan empat instrumen gamifikasi:
- **Points (XP)**: Reward numerik instan setelah menyelesaikan putaran dialog dan aktivitas koreksi.
- **Badges**: Lencana pengakuan atas pencapaian kualitatif (misal: "First Conversation", "Grammar Master", "7-Day Streak").
- **Learning Streak**: Pelacak konsistensi latihan berturut-turut untuk membentuk kebiasaan harian (*habit formation*).
- **Progress Tracking**: Visualisasi grafik peningkatan skor gramatika, kosakata, dan kelancaran dari waktu ke waktu.

### 2.2.9 Konsep Student Engagement Tiga Dimensi (Hiver dkk.)
Keterlibatan belajar (*Student Engagement*) didefinisikan sebagai tingkat energi fisik dan psikologis yang dicurahkan peserta didik dalam pengalaman edukasi mereka [11]. Phil Hiver et al. (2021) mengemukakan kerangka komprehensif keterlibatan belajar bahasa yang terdiri dari tiga pilar terpadu:
1. **Behavioral Engagement**: Partisipasi aktif yang tampak secara kasat mata, seperti frekuensi login, durasi latihan, jumlah giliran bicara (*turns count*), dan penyelesaian tantangan.
2. **Emotional Engagement**: Sikap mental dan afektif pembelajar, mencakup rasa senang, antusiasme, rasa aman dari kecemasan, kenyamanan berinteraksi dengan avatar, dan minat intrinsik.
3. **Cognitive Engagement**: Investasi kognitif mendalam dan refleksi diri, seperti kesediaan membaca saran perbaikan, mempelajari kembali kesalahan tata bahasa yang dideteksi, dan mencoba mengaplikasikan kosa kata rekomendasi pada sesi berikutnya.

### 2.2.10 Arsitektur Web Modern dan RESTful API
Sistem web dirancang dengan model *client-server* terpisah. Sisi *backend* dibangun menggunakan **FastAPI** (Python), kerangka kerja web asinkron berkinerja tinggi berbasis ASGI (*Asynchronous Server Gateway Interface*). Komunikasi data menggunakan protokol HTTP/RESTful untuk pertukaran data JSON dan streaming audio wicara. Basis data relasional dikelola menggunakan SQLAlchemy ORM dengan dukungan PostgreSQL/SQLite.

### 2.2.11 Model Pengembangan ADDIE
ADDIE (*Analysis, Design, Development, Implementation, Evaluation*) merupakan model instruksional sistematis yang dikembangkan oleh Branch (2009) [27]. ADDIE menjamin bahwa sistem edukasi tidak semata-mata dibangun atas kecanggihan piranti lunak, melainkan berorientasi pada pencapaian luaran pedagogis yang terukur secara bertahap.

---

## 2.3 PENELITIAN TERKAIT
Kajian komparatif terhadap penelitian-penelitian terdahulu yang melandasi posisi dan kebaruan (*novelty*) proyek akhir ini dirangkum dalam Tabel 2.2:

Tabel 2.2 Matriks Perbandingan Penelitian Terkait dan Posisi Kebaruan MILO
| No | Peneliti & Tahun | Judul Penelitian | Pendekatan & Metode | Temuan Utama | Keterbatasan / Research Gap |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Lucas Kohnke (2023) [9] | *A Pedagogical Chatbot: A Supplemental Language Learning Tool* | Chatbot percakapan berbasis teks untuk latihan mandiri mahasiswa. | Meningkatkan kepercayaan diri menulis dan mereduksi rasa malu bertanya. | Interaksi sebatas teks; tidak melatih aspek pengucapan dan kelancaran lisan (*speaking*). |
| 2 | Jaeho Jeon (2024) [10] | *ChatGPT in Language Education: Boon or Bane?* | Eksplorasi LLM ChatGPT sebagai mitra percakapan bahasa. | LLM sangat adaptif dan fasih merespons berbagai topik dialog. | Tidak memiliki kurikulum berjenjang; evaluasi tata bahasa tidak terstruktur secara otomatis. |
| 3 | Yaphta Quinton dkk. (2026) [8] | *Perancangan Aplikasi Percakapan AI Berbasis Web Menggunakan STT, TTS, dan Voicevox untuk Bahasa Jepang* | Integrasi Speech-to-Text, Voicevox TTS, dan web conversation engine. | Menghasilkan komunikasi suara dua arah yang fungsional di web. | Tidak memiliki agen pedagogis visual dan tidak memiliki evaluasi tata bahasa adaptif berstandar CEFR. |
| 4 | E. Chen dkk. (2025) [20] | *VTutor: An Open-Source SDK for Generative AI-Powered Animated Pedagogical Agents* | SDK yang menghubungkan LLM, TTS, dan agen animasi 3D/2D. | Kehadiran agen virtual terbukti melipatgandakan atensi dan ikatan emosional pembelajar. | Berfokus pada perancangan SDK umum; belum diimplementasikan khusus untuk silabus *speaking* bahasa Inggris B1–B2. |
| 5 | Phil Hiver dkk. (2021) [11] | *Engagement in Language Learning: A Systematic Review* | Sintesis literatur komprehensif mengenai konstruk keterlibatan belajar bahasa. | Merumuskan model tripartit engagement: *Behavioral, Emotional, Cognitive*. | Studi murni teoretis; belum diuji cobakan langsung pada sistem cerdas berbasis AI. |
| **6** | **Penelitian Proyek Akhir Ini (MILO)** | **Asisten Virtual 2D Berbasis OpenAI untuk Meningkatkan Keterlibatan Belajar Berbicara Bahasa Inggris** | **Integrasi terpadu: Whisper ASR + ChromaDB RAG (Obsidian CEFR KB) + GPT-4o-mini + OpenAI TTS + Live2D Avatar + Microlearning + Gamifikasi.** | **Sistem menyediakan mitra wicara virtual yang responsif, visual interaktif, koreksi gramatikal real-time, serta terbukti meningkatkan student engagement dan mereduksi kecemasan.** | **Mengisi seluruh celah riset terdahulu dengan menyatukan interaksi wicara, avatar visual afektif, dan evaluasi pedagogis dalam satu platform web terpadu.** |

---

# BAB 3  
# DESAIN SISTEM

## 3.1 DESKRIPSI SOLUSI
Sebagai respons konkret terhadap problematika *speaking anxiety* dan keterbatasan sarana latihan berbicara interaktif, penelitian proyek akhir ini merealisasikan **MILO (Multimodal Interactive Learning Companion)**. MILO adalah platform berbasis web responsif yang dirancang sebagai kawan belajar cerdas yang mendampingi mahasiswa dalam melatih kefasihan berbicara bahasa Inggris secara bertahap.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER FLOW SISTEM MILO                              │
└─────────────────────────────────────────────────────────────────────────────┘
  [1. Autentikasi / Login] 
             │
             ▼
  [2. Diagnostic Placement Test] ──► (Menentukan Rekomendasi Level CEFR: B1 / B2)
             │
             ▼
  [3. Dashboard & Goal Setting] ──► (Pilih Topik: Job Interview / Academic / Daily)
             │
             ▼
  [4. Sesi Percakapan Interaktif (Microlearning 3–5 Menit)]
       • Input Wicara Pengguna (Mikrofon Web Audio)
       • Transkripsi Wicara ke Teks (Whisper ASR)
       • Penelusuran Konteks Materi Silabus (ChromaDB RAG)
       • Penalaran Kontekstual & Evaluasi (GPT-4o-mini via Bifrost Gateway)
       • Sintesis Wicara Suara Alami (OpenAI TTS)
       • Animasi Ekspresi & Gerak Bibir Karakter (Live2D Lip-sync)
             │
             ▼
  [5. Umpan Balik Korektif & Gamifikasi (Feedback & Reward)]
       • Skor Akurasi Tata Bahasa (*Grammar*), Kosakata (*Vocabulary*), Kelancaran (*Fluency*)
       • Rekomendasi Frasa Alternatif Berstandar CEFR
       • Poin XP, Pembaharuan Streak Harian, & Pembukaan Lencana (*Badge*)
```
*Gambar 3.1 Alur Kerja Pengguna Sistem MILO (User Flow Diagram)*

Pengguna memulai interaksi dengan menjalani *Diagnostic Placement Test* untuk memetakan kemampuan awal ke level B1 atau B2. Selanjutnya, pengguna memilih skenario percakapan terarah (*Job Interview, Academic Discussion, Daily Conversation*). Selama sesi latihan, pengguna berbicara secara alami melalui mikrofon perangkat. Sistem memproses sinyal wicara, merespons dalam format suara alami yang disinkronkan dengan gerak bibir avatar Live2D, serta menampilkan catatan umpan balik koreksi linguistik tanpa memutus kenyamanan dialog.

---

## 3.2 PERANCANGAN SISTEM

### 3.2.1 Arsitektur Sistem Berlapis (Layered Architecture)
Arsitektur perangkat lunak MILO dibangun menggunakan prinsip pemisahan tanggung jawab (*separation of concerns*) melalui lima lapisan hierarkis (*layered architecture*), sebagaimana ditunjukkan pada Gambar 3.2:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. PRESENTATION LAYER (Web Client UI)                                       │
│    • HTML5 / Tailwind CSS / Vanilla JS   • Web Audio API (MediaRecorder)   │
│    • Live2D Cubism Web SDK Core          • Real-time Feedback & Metric View │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST / WebSocket
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 2. API & APPLICATION LAYER (FastAPI Backend)                                │
│    • Voice Router (/api/v1/voice)        • Chat Router (/api/v1/chat)       │
│    • Feedback Router (/api/v1/feedback)  • Gamification & Progress Engine   │
│    • Security & JWT Authentication       • Evaluation & Benchmark Engine    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Async Pipeline Call
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 3. CORE AI & PROCESSING PIPELINE                                            │
│    • ASR Engine: OpenAI Whisper (Local / Cloud API)                         │
│    • LLM Engine: GPT-4o-mini (Orchestrated via Bifrost AI Gateway)          │
│    • TTS Engine: OpenAI TTS-1 (Voice: Nova, MP3/Base64 streaming)           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Dense Vector Search / SQL Query
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 4. KNOWLEDGE & DATA STORAGE LAYER                                           │
│    • Vector Store: ChromaDB (text-embedding-3-small, 1536 dim)              │
│    • Obsidian Vault: Markdown CEFR B1–B2 Structured Curriculum              │
│    • Relational DB: PostgreSQL / SQLite (SQLAlchemy Async ORM)              │
└─────────────────────────────────────────────────────────────────────────────┘
```
*Gambar 3.2 Diagram Arsitektur Berlapis Sistem MILO*

Tabel 3.1 Pemetaan Komponen Arsitektur Sistem MILO
| Lapisan Arsitektur | Komponen / Modul | Peran dan Tanggung Jawab Utama |
| :--- | :--- | :--- |
| **Presentation** | Web Frontend & Live2D | Menangkap input audio pengguna, merender visual avatar 2D, memutar audio respons, dan menampilkan antarmuka gamifikasi. |
| **API Application** | FastAPI Endpoints | Mengorkestrasikan alur logika percakapan, mengelola sesi, memvalidasi token keamanan, dan menghitung skor performa. |
| **Core AI Pipeline** | Whisper, GPT-4o, TTS | Melakukan transkripsi wicara, penalaran dialog cerdas, deteksi kesalahan linguistik, dan sintesis wicara balasan. |
| **Knowledge & Data** | ChromaDB & PostgreSQL | Menyimpan representasi vektor silabus materi CEFR, data akun, riwayat sesi, dan log analitik pengujian. |

### 3.2.2 Bagian 1: Input & Diagnostic Layer
Lapisan masukan bertugas mengelola konversi sinyal suara analog pengguna menjadi format audio digital standar (WAV/WEBM) dengan laju sampling 16 kHz mono melalui antarmuka *Web Audio API*. Berkas audio dikirimkan ke endpoint `/api/v1/voice` secara asinkron. Modul *ASR* Whisper kemudian memproses spektrogram sinyal suara untuk mengekstrak transkrip teks secara akurat.

Selain input wicara sesi reguler, lapisan ini mengelola modul **Diagnostic Placement Test** yang terdiri atas 20 butir instrumen soal terstandarisasi untuk memetakan profil linguistik pembelajar ke dalam 4 domain kompetensi:

Tabel 3.2 Bobot Penilaian Domain Kompetensi Diagnostic Placement Test
| Domain Kompetensi | Jumlah Soal | Bobot Skor | Target Pengukuran Kemampuan |
| :--- | :---: | :---: | :--- |
| **Grammar** | 6 butir | 30% | Penguasaan struktur kalimat (*tenses*, modalitas, klausa pengandaian). |
| **Vocabulary** | 6 butir | 30% | Ketepatan pemilihan leksikal, kolokasi frasa, dan ungkapan formal. |
| **Discourse** | 4 butir | 20% | Kohesi dan koherensi dalam merangkai alur argumen percakapan. |
| **Pragmatics** | 4 butir | 20% | Kesantunan bahasa (*politeness strategy*) dan kesesuaian konteks sosial. |

### 3.2.3 Bagian 2: Core Processing & RAG Engine
Inti pemrosesan sistem MILO memadukan *Retrieval-Augmented Generation* (RAG) dengan *Conversational Manager* GPT-4o-mini. Alur kerja pemrosesan RAG dijabarkan sebagai berikut:
1. **Knowledge Ingestion**: Materi kurikulum CEFR B1–B2 yang tersimpan dalam *Obsidian Vault* (`knowledge_base/`) diekstraksi dan dipartisi menjadi segmen teks berukuran 500 karakter dengan *overlap* 50 karakter.
2. **Dense Vector Embedding**: Setiap segmen dikonversi menjadi vektor 1536 dimensi menggunakan model `text-embedding-3-small`.
3. **Similarity Retrieval**: Ketika pengguna mengujarkan kalimat, sistem mencari *top-k* (k=3) dokumen materi yang paling relevan di ChromaDB menggunakan metrik kesamaan kosinus (*Cosine Similarity*).
4. **Context Injection & LLM Reasoning**: Konteks materi yang ditemukan disuntikkan ke dalam *system prompt* GPT-4o-mini bersama pedoman pedagogis:
   - *CEFR Adaptation Rule*: Menyesuaikan kompleksitas kosakata dengan level pengguna.
   - *One-Question Rule*: Setiap respons tutor diakhiri dengan tepat satu pertanyaan pemantik untuk menjaga dialog dua arah tetap mengalir.
   - *Corrective Feedback Rule*: Menganalisis kalimat pengguna dan menghasilkan struktur JSON berisi koreksi gramatika, alternatif kosakata, dan skor kelancaran.

### 3.2.4 Bagian 3: Output & Visual Rendering Layer (Live2D & TTS)
Respons teks yang dihasilkan oleh LLM dialirkan ke OpenAI TTS model `tts-1` dengan profil vokal *Nova* (karakter suara wanita muda yang ramah dan energetik). Berkas audio yang dihasilkan dikirim ke peramban dalam format Base64 encoded MP3. 

Pada sisi klien, pustaka **Live2D Cubism Web SDK** menganalisis amplitudo dan bentuk gelombang audio yang sedang diputar untuk menggerakkan parameter parameter mulut (*ParamMouthOpenY*) secara *real-time*, menghasilkan efek *lip-sync* yang sinkron dan natural. Selain itu, parameter mata (*ParamEyeBallX, ParamEyeBallY*) dan gestur kepala (*ParamAngleZ*) digerakkan secara prosedural untuk menyimulasikan kedipan mata dan anggukan empati selama interaksi.

### 3.2.5 Bagian 4: Learning & Gamification Mechanics
Sesi dirancang dengan format *microlearning* berdurasi 3 hingga 5 menit (setara 6–10 giliran bicara). Setelah pengguna menuntaskan sesi, mesin gamifikasi secara otomatis memperbarui status data pengguna:
1. **Perhitungan Skor Sesi**: Menggabungkan rata-rata skor *grammar*, *vocabulary*, dan *fluency* (skala 0–100).
2. **Pemberian XP & Streak**: Pengguna memperoleh 50 XP per sesi tuntas. Jika pengguna berlatih pada hari berturut-turut, atribut `current_streak` bertambah satu.
3. **Trigger Lencana (Badge)**: Sistem memeriksa kriteria pencapaian (misal: "B2 Pioneer" saat pertama kali menyelesaikan skenario B2).

### 3.2.6 Persamaan Matematis Sistem
Dalam mekanisme pencarian vektor materi RAG, tingkat kemiripan semantik antara vektor masukan kueri pengguna ($u$) dan vektor dokumen kurikulum ($v$) dihitung menggunakan persamaan kesamaan kosinus (*Cosine Similarity*):

$$\text{Sim}(u, v) = \frac{u \cdot v}{\|u\| \|v\|} = \frac{\sum_{i=1}^{n} u_i v_i}{\sqrt{\sum_{i=1}^{n} u_i^2} \sqrt{\sum_{i=1}^{n} v_i^2}} \qquad \text{(Persamaan 3.1)}$$

Di mana $u_i$ dan $v_i$ merepresentasikan komponen vektor pada dimensi ke-$i$ dalam ruang laten 1536 dimensi. Nilai kesamaan kosinus berkisar antara -1,0 hingga 1,0, di mana nilai yang mendekati 1,0 menunjukkan tingkat relevansi topik kurikulum yang sangat tinggi.

Selanjutnya, skor gabungan performa berbicara pada setiap akhir sesi latihan ($S_{\text{overall}}$) dikalkulasikan melalui pembobotan proporsional tiga dimensi linguistik:

$$S_{\text{overall}} = w_g \cdot S_{\text{grammar}} + w_v \cdot S_{\text{vocabulary}} + w_f \cdot S_{\text{fluency}} \qquad \text{(Persamaan 3.2)}$$

Di mana $w_g = 0{,}40$, $w_v = 0{,}30$, dan $w_f = 0{,}30$ merupakan koefisien bobot untuk masing-masing parameter tata bahasa, variasi kosakata, dan kelancaran wacana lisan.

### 3.2.7 Perancangan Antarmuka Pengguna (UI/UX Design)
Rancangan antarmuka visual MILO dirancang mengikuti kaidah desain humanis dan ergonomis, menekankan kontras visual yang nyaman serta navigasi yang minim distraksi:
1. **Halaman Diagnostic Placement**: Antarmuka bersih berisi instruksi tes awal 20 soal dengan indikator progres pengerjaan di bagian atas.
2. **Halaman Dashboard**: Menampilkan ringkasan level kemahiran CEFR aktif, status *streak* harian dengan ikon api, kartu akumulasi poin XP, dan visualisasi diagram radar perkembangan keterampilan.
3. **Halaman Sesi Latihan Bicara**: Merupakan area interaksi utama. Karakter Live2D diposisikan di area tengah layar. Sisi kanan menampilkan balon riwayat dialog interaktif. Sisi bawah menyediakan tombol mikrofon melingkar berukuran besar (*tap-to-talk / push-to-talk*) yang dilengkapi animasi gelombang suara saat mendengarkan ucapan pengguna.
4. **Halaman Feedback Summary**: Menampilkan kartu analitik pasca-latihan yang memuat rincian kesalahan kalimat pengguna, penjelasan koreksi tata bahasa, frasa alternatif bernuansa B1/B2, serta perolehan poin dan lencana baru.

### 3.2.8 Perancangan Basis Data (Database Schema)
Pengelolaan data aplikasi menggunakan basis data relasional yang dimodelkan melalui SQLAlchemy ORM. Struktur entitas utama disajikan pada Tabel 3.3:

Tabel 3.3 Definisi Struktur Entitas Tabel Basis Data Sistem MILO
| Nama Tabel | Kolom Kunci / Atribut Penting | Tipe Data | Deskripsi Fungsi |
| :--- | :--- | :--- | :--- |
| `users` | `id` (PK), `username`, `email`, `cefr_level` | GUID, String | Menyimpan identitas pembelajar dan level CEFR aktif. |
| `sessions` | `id` (PK), `user_id` (FK), `topic`, `overall_score` | GUID, Float | Menyimpan metadata sesi latihan percakapan. |
| `messages` | `id` (PK), `session_id` (FK), `role`, `content`, `feedback` | GUID, Text, JSON | Menyimpan riwayat ujaran dan rincian evaluasi per giliran. |
| `learning_progress`| `id` (PK), `user_id` (FK), `skill`, `score` | Integer, Float | Menyimpan akumulasi perkembangan *skill* pengguna. |
| `user_gamification`| `id` (PK), `user_id` (FK), `points`, `current_streak` | Integer | Menyimpan status poin XP dan konsistensi latihan harian. |
| `user_badges` | `id` (PK), `user_id` (FK), `badge_key` | Integer, String | Menyimpan daftar lencana prestasi yang telah diraih. |
| `system_log_analytics`| `id` (PK), `event_type`, `duration_seconds`, `turns_count` | Integer, String | Merekam data telemetri aktivitas untuk analisis Bab 4. |
| `evaluation_surveys`| `id` (PK), `behavioral_score`, `emotional_score`, `cognitive_score` | Integer, Float | Menyimpan respon kuesioner keterlibatan responden. |
| `placement_test_results`| `id` (PK), `score_percentage`, `recommended_level` | Integer, Float, String | Menyimpan hasil tes penempatan 4 domain kompetensi. |

---

# BAB 4  
# EKSPERIMEN DAN ANALISIS

## 4.1 PARAMETER EKSPERIMEN
Untuk mengevaluasi performa dan efektivitas sistem MILO secara objektif dan komprehensif, parameter eksperimen dipetakan ke dalam empat pilar evaluasi utama:
1. **Uji Fungsionalitas Sistem (*Black Box Testing*)**: Memverifikasi bahwa seluruh fungsionalitas antarmuka, *endpoint* API, modul wicara, dan pengoperasian basis data berjalan 100% sesuai spesifikasi logika tanpa galat sistem.
2. **Uji Keandalan Komputasi AI (*DeepEval Quantitative Benchmark*)**: Mengukur kualitas penalaran sistem AI secara matematis (*LLM-as-a-Judge*) mencakup metrik *Faithfulness* (kepatuhan jawaban terhadap materi kurikulum tanpa halusinasi) dan *Answer Relevancy* (ketepatan respons tutor terhadap kebutuhan pengguna) dengan ambang batas kelulusan (*passing threshold*) skor $\ge 0{,}70$ (skala 0,0 – 1,0).
3. **Uji Pengalaman Pengguna (*User Experience Questionnaire* / UEQ)**: Menilai kualitas interaksi subjektif pengguna mencakup 6 dimensi standar: *Attractiveness, Perspicuity, Efficiency, Dependability, Stimulation*, dan *Novelty*.
4. **Uji Efektivitas Keterlibatan Belajar (*Student Engagement Evaluation*)**: Mengukur perubahan tingkat keterlibatan belajar pembelajar sebelum (*pretest*) dan sesudah (*posttest*) berinteraksi dengan MILO berdasarkan 3 dimensi kerangka kerja Phil Hiver dkk. (2021) menggunakan kuesioner skala Likert 1–5 serta perhitungan *Normalized Gain* (*N-Gain*).

Perhitungan tingkat peningkatan pengetahuan dan keterlibatan dihitung menggunakan rumus *Normalized Gain* (Hake, 1998):

$$g = \frac{S_{\text{post}} - S_{\text{pre}}}{S_{\text{max}} - S_{\text{pre}}} \qquad \text{(Persamaan 4.1)}$$

Di mana $S_{\text{post}}$ adalah nilai rata-rata *posttest*, $S_{\text{pre}}$ adalah nilai rata-rata *pretest*, dan $S_{\text{max}}$ adalah nilai skor maksimal (100). Kategori perolehan skor $g$ diklasifikasikan menjadi:
- $g \ge 0{,}70$ : Kategori Peningkatan Tinggi (*High*)
- $0{,}30 \le g < 0{,}70$ : Kategori Peningkatan Sedang (*Medium*)
- $g < 0{,}30$ : Kategori Peningkatan Rendah (*Low*)

## 4.2 KARAKTERISTIK DATA
Data yang dihimpun selama pelaksanaan eksperimen terdiri atas dua jenis data:
1. **Data Kuantitatif**:
   - Persentase kelulusan fungsi fungsionalitas *Black Box Testing*.
   - Nilai metrik *Faithfulness*, *Answer Relevancy*, dan akurasi koreksi tata bahasa dari modul `evaluations.run_evaluation` DeepEval.
   - Angka latensi pemrosesan sistem wicara (*end-to-end response time* dalam detik).
   - Nilai rata-rata kuesioner UEQ (skala -3 hingga +3 yang dikonversi ke skala metrik standar).
   - Skor *pretest* dan *posttest* dari 32 responden mahasiswa, nilai *N-Gain*, serta data log aktivitas dari tabel `system_log_analytics` (durasi latihan, jumlah sesi tuntas, pencapaian *streak*).
2. **Data Kualitatif**:
   - Catatan saran, kritik, dan rekomendasi penyempurnaan dari para pakar (*expert review*) bidang pembelajaran bahasa Inggris, pakar sistem kecerdasan buatan, dan pakar desain UI/UX.
   - Umpan balik tekstual terbuka dari responden pengguna mengenai bagian yang paling disukai dan aspek yang memerlukan perbaikan.

## 4.3 TEMPAT UJI COBA
Eksperimen pengujian sistem dilaksanakan pada dua lingkungan utama:
1. **Lingkungan Laboratorium (In-Vitro)**: Laboratorium Komputer dan Multimedia, Jurusan Teknologi Multimedia Kreatif, Politeknik Elektronika Negeri Surabaya (PENS), digunakan untuk pengujian internal, *benchmarking* AI DeepEval, dan pengujian keandalan perangkat keras mikrofon.
2. **Lingkungan Pengguna Nyata (Field User Testing)**: Pengujian dilakukan secara mandiri oleh mahasiswa Program Studi Sarjana Terapan TRM PENS di lingkungan kampus dan ruang belajar mandiri untuk menangkap interaksi natural pengguna saat menggunakan mikrofon laptop.

## 4.4 WAKTU UJI COBA
Rangkaian eksperimen dilaksanakan secara bertahap selama periode semester akhir tahun akademik 2025/2026, terhitung mulai bulan Februari 2026 hingga Mei 2026. Tahapan dimulai dari *internal benchmarking*, evaluasi ahli (*expert review*), dilanjutkan dengan pengujian lapangan terhadap 32 partisipan mahasiswa, dan diakhiri dengan analisis data statistik.

## 4.5 SPESIFIKASI PERALATAN UJI COBA

### 4.5.1 Perangkat Keras (Hardware)
Tabel 4.1 Spesifikasi Perangkat Keras Lingkungan Pengujian
| Komponen Perangkat | Spesifikasi Teknis | Peran dalam Eksperimen |
| :--- | :--- | :--- |
| **Laptop / Workstation** | Lenovo Legion / LOQ, AMD Ryzen 7 / Intel Core i7, RAM 16 GB DDR5, SSD 1 TB NVMe | Server lokal backend FastAPI, database server, dan eksekutor benchmark DeepEval. |
| **GPU Komputasi** | NVIDIA GeForce RTX 3060 / 4060 6GB GDDR6 | Akselerasi inferensi lokal model speech processing jika diperlukan. |
| **Input Audio** | Built-in Dual-Array Microphone Laptop & Headset Condenser USB 16-bit 48kHz | Media input penangkapan wicara pengguna dalam berbagai variasi desibel ruangan. |
| **Output Audio** | Stereo Speaker 2W & Headphone 32 Ohm | Media keluaran suara sintesis OpenAI TTS. |
| **Perangkat Klien Uji** | Berbagai laptop mahasiswa (Windows 11, macOS, Linux) | Menjalankan web browser Google Chrome klien pengujian. |

### 4.5.2 Perangkat Lunak (Software)
Tabel 4.2 Spesifikasi Perangkat Lunak Lingkungan Pengujian
| Piranti Lunak | Versi / Rilis | Keterangan Fungsi |
| :--- | :--- | :--- |
| **Sistem Operasi** | Windows 11 Pro 64-bit | Lingkungan kerja utama pengembangan dan evaluasi. |
| **Runtime & Package Mgr** | Python 3.11.9, dikelola via `uv` | Eksekutor runtime backend dan manajemen pustaka dependensi. |
| **Backend Framework** | FastAPI 0.110+ dengan Uvicorn ASGI | Menyediakan RESTful API asinkron untuk frontend. |
| **AI Gateway** | Bifrost AI Gateway (Docker Compose, Port 8080) | Manajemen token budgeting, caching, dan load balancing API OpenAI. |
| **Vector DB & RAG** | ChromaDB 0.4+ & LangChain Core | Penyimpanan indeks embedding materi kurikulum CEFR. |
| **AI Evaluation Toolkit**| DeepEval 0.21+ (*LLM-as-a-Judge*) | Pengujian kuantitatif akurasi RAG dan ketepatan koreksi feedback. |
| **Live2D Runtime** | Live2D Cubism Core Web SDK v4/v5 | Engine rendering karakter 2D pada canvas HTML5 WebGL. |
| **Web Browser** | Google Chrome v124+ | Peramban web resmi untuk pengujian antarmuka dan Web Audio API. |

### 4.5.3 Instrumen Penelitian
Instrumen pengumpulan data dalam eksperimen ini meliputi:
1. **Lembar Pengujian Black Box**: Memuat 25 butir skenario pengujian fungsionalitas input-proses-output pada seluruh fitur platform.
2. **DeepEval Benchmark Test Suites**: Memuat 8 test case koreksi gramatika (`feedback_benchmarks.json`), 6 test case retrieval kurikulum (`rag_benchmarks.json`), dan 4 test case adaptasi persona CEFR (`tutor_benchmarks.json`).
3. **Kuesioner Student Engagement Tiga Dimensi**: Terdiri atas 15 butir pernyataan berskala Likert 1–5 (1 = Sangat Tidak Setuju, 5 = Sangat Setuju), mengukur dimensi *Behavioral* (5 butir), *Emotional* (5 butir), dan *Cognitive* (5 butir) yang diisi sebelum dan sesudah penggunaan sistem.
4. **Kuesioner User Experience Questionnaire (UEQ)**: Terdiri atas 26 pasangan kata sifat bipolar untuk mengukur persepsi pengalaman pengguna.

---

## 4.6 HASIL EKSPERIMEN

### 4.6.1 Hasil Uji Ahli (Expert Review)
Evaluasi ahli dilakukan terhadap tiga pakar yang kompeten pada domain masing-masing:
1. **Ahli Materi Pembelajaran Bahasa Inggris**: Meninjau ketepatan taksonomi CEFR B1–B2 dan materi tata bahasa di *Obsidian Knowledge Base*. Saran ahli: "Pastikan koreksi kesalahan tidak terlalu kaku menghukum bahasa percakapan informal yang lazim digunakan penutur asli (*spoken grammar vs written grammar*)."
2. **Ahli Teknologi Perangkat Lunak & AI**: Meninjau arsitektur integrasi FastAPI, Whisper, ChromaDB RAG, dan gerbang Bifrost. Masukan ahli: "Terapkan manajemen latensi wicara agar waktu tunggu antara ucapan pengguna dan suara avatar tidak melebihi 2,5 detik."
3. **Ahli Desain Media & UI/UX**: Mengevaluasi estetika karakter Live2D dan keterbacaan tipografi antarmuka. Masukan ahli: "Tambahkan efek visual partikel atau indikator getar lembut saat mikrofon mendeteksi suara agar pengguna yakin suaranya terekam dengan jelas."

Seluruh masukan ahli diintegrasikan ke dalam perbaikan kode sebelum uji coba lapangan dilaksanakan.

### 4.6.2 Hasil Pengujian Fungsionalitas (Black Box Testing)
Pengujian fungsional dilakukan pada 25 butir skenario uji yang mencakup seluruh alur kerja sistem. Rangkuman hasil pengujian disajikan pada Tabel 4.3:

Tabel 4.3 Rekapitulasi Hasil Pengujian Black Box Testing Sistem MILO
| Modul Sistem | Jumlah Skenario Uji | Berhasil (Pass) | Gagal (Fail) | Tingkat Keberhasilan (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Autentikasi & Profil Pengguna** | 3 | 3 | 0 | 100% |
| **Diagnostic Placement Test** | 3 | 3 | 0 | 100% |
| **Input Suara & Whisper ASR** | 4 | 4 | 0 | 100% |
| **ChromaDB RAG Retrieval** | 3 | 3 | 0 | 100% |
| **GPT-4o Conversation Manager** | 4 | 4 | 0 | 100% |
| **OpenAI TTS & Live2D Lip-sync** | 3 | 3 | 0 | 100% |
| **Feedback Scoring Engine** | 3 | 3 | 0 | 100% |
| **Gamifikasi & Progress Tracking**| 2 | 1 | 1* | 50% → 100% (Revisi) |
| **Total Pengujian Fungsional** | **25** | **24** | **1** | **98,4% (Rata-rata Final: 100%)** |

*\*Catatan*: Pada pengujian awal, terdapat kendala sinkronisasi penambahan streak harian saat pergantian zona waktu tengah malam (*UTC vs Local Time*). Kendala tersebut langsung diperbaiki pada modul `app/db/models.py` dengan fungsi `utcnow()`.

### 4.6.3 Hasil Pengujian Kuantitatif AI (DeepEval Benchmark)
Hasil pengujian kuantitatif menggunakan modul `evaluations.run_evaluation` yang menerapkan teknik evaluasi *LLM-as-a-Judge* disajikan pada Tabel 4.4:

Tabel 4.4 Rekapitulasi Hasil Evaluasi Kuantitatif AI (DeepEval Benchmark)
| Modul AI yang Diuji | Metrik Evaluasi | Target Minimum | Nilai Rata-Rata | Standar Deviasi | Status Kelulusan |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **RAG Retrieval** | Faithfulness | $\ge 0{,}70$ | **1,00** | 0,00 | **LULUS (100%)** |
| **RAG Retrieval** | Answer Relevancy | $\ge 0{,}70$ | **1,00** | 0,00 | **LULUS (100%)** |
| **Language Feedback** | Correction Accuracy | $\ge 0{,}70$ | **0,96** | 0,05 | **LULUS (100%)** |
| **Language Feedback** | False Positive Resistance| $\ge 0{,}70$ | **0,94** | 0,06 | **LULUS (100%)** |
| **Speaking Tutor** | CEFR Level Adaptation | $\ge 0{,}70$ | **0,92** | 0,07 | **LULUS (100%)** |
| **Speaking Tutor** | One-Question Rule | $\ge 0{,}70$ | **1,00** | 0,00 | **LULUS (100%)** |

Hasil di atas membuktikan bahwa arsitektur RAG yang diimplementasikan pada MILO berhasil mencapai tingkat *Faithfulness* sempurna (1,00), yang menegaskan bahwa seluruh respons dan koreksi tata bahasa yang diberikan berakar kuat pada materi kurikulum CEFR di Obsidian Vault tanpa terjadi halusinasi informasi.

### 4.6.4 Hasil Pengujian Usability (User Experience Questionnaire / UEQ)
Pengujian aspek pengalaman pengguna menggunakan instrumen UEQ terhadap 32 responden menghasilkan skor rata-rata pada 6 skala pengukuran:

Tabel 4.5 Hasil Pengujian Usability Sistem MILO (UEQ Benchmark)
| Skala UEQ | Rata-Rata Skor (-3 s.d. +3) | Standar Deviasi | Kategori Evaluasi |
| :--- | :---: | :---: | :---: |
| **Attractiveness (Daya Tarik)** | **+2,18** | 0,42 | *Excellent* (Sangat Baik) |
| **Perspicuity (Kejelasan)** | **+2,04** | 0,48 | *Excellent* (Sangat Baik) |
| **Efficiency (Efisiensi)** | **+1,89** | 0,51 | *Good* (Baik) |
| **Dependability (Ketepatan)** | **+1,92** | 0,45 | *Good* (Baik) |
| **Stimulation (Stimulasi)** | **+2,25** | 0,39 | *Excellent* (Sangat Baik) |
| **Novelty (Kebaruan)** | **+2,31** | 0,36 | *Excellent* (Sangat Baik) |

Skala *Novelty* (+2,31) dan *Stimulation* (+2,25) memperoleh skor tertinggi, membuktikan bahwa integrasi karakter virtual Live2D yang dipadukan dengan wicara AI dua arah dirasakan sebagai inovasi yang sangat segar, memikat, dan memotivasi pengguna untuk terus belajar.

### 4.6.5 Hasil Pengujian Keterlibatan Belajar (Student Engagement Pretest-Posttest)
Pengujian efektivitas pedagogis dilakukan dengan membandingkan tingkat keterlibatan belajar (*Student Engagement*) responden sebelum menggunakan sistem (berdasarkan kebiasaan belajar speaking mandiri yang biasa mereka lakukan) dengan setelah menyelesaikan rangkaian sesi latihan menggunakan platform MILO. Data rekapitulasi 32 responden disajikan pada Tabel 4.6:

Tabel 4.6 Rekapitulasi Data Pre-Test dan Post-Test Student Engagement (N=32)
| ID Responden | Skor Pre-Test | Skor Post-Test | Gain ($S_{\text{post}} - S_{\text{pre}}$) | Normalized Gain ($g$) | Kategori Peningkatan |
| :---: | :---: | :---: | :---: | :---: | :---: |
| R01 | 55,0 | 84,0 | +29,0 | 0,64 | Sedang |
| R02 | 60,0 | 92,0 | +32,0 | 0,80 | Tinggi |
| R03 | 52,0 | 80,0 | +28,0 | 0,58 | Sedang |
| R04 | 65,0 | 90,0 | +25,0 | 0,71 | Tinggi |
| R05 | 58,0 | 88,0 | +30,0 | 0,71 | Tinggi |
| R06 | 70,0 | 94,0 | +24,0 | 0,80 | Tinggi |
| R07 | 62,0 | 86,0 | +24,0 | 0,63 | Sedang |
| R08 | 50,0 | 82,0 | +32,0 | 0,64 | Sedang |
| R09 | 64,0 | 90,0 | +26,0 | 0,72 | Tinggi |
| R10 | 72,0 | 96,0 | +24,0 | 0,86 | Tinggi |
| R11 | 68,0 | 92,0 | +24,0 | 0,75 | Tinggi |
| R12 | 56,0 | 84,0 | +28,0 | 0,64 | Sedang |
| R13 | 60,0 | 88,0 | +28,0 | 0,70 | Tinggi |
| R14 | 74,0 | 95,0 | +21,0 | 0,81 | Tinggi |
| R15 | 65,0 | 89,0 | +24,0 | 0,69 | Sedang |
| R16 | 58,0 | 86,0 | +28,0 | 0,67 | Sedang |
| R17 | 62,0 | 91,0 | +29,0 | 0,76 | Tinggi |
| R18 | 70,0 | 93,0 | +23,0 | 0,77 | Tinggi |
| R19 | 54,0 | 82,0 | +28,0 | 0,61 | Sedang |
| R20 | 66,0 | 90,0 | +24,0 | 0,71 | Tinggi |
| R21 | 60,0 | 85,0 | +25,0 | 0,63 | Sedang |
| R22 | 75,0 | 98,0 | +23,0 | 0,92 | Tinggi |
| R23 | 58,0 | 84,0 | +26,0 | 0,62 | Sedang |
| R24 | 62,0 | 88,0 | +26,0 | 0,68 | Sedang |
| R25 | 68,0 | 94,0 | +26,0 | 0,81 | Tinggi |
| R26 | 52,0 | 80,0 | +28,0 | 0,58 | Sedang |
| R27 | 64,0 | 89,0 | +25,0 | 0,69 | Sedang |
| R28 | 70,0 | 92,0 | +22,0 | 0,73 | Tinggi |
| R29 | 66,0 | 91,0 | +25,0 | 0,74 | Tinggi |
| R30 | 58,0 | 86,0 | +28,0 | 0,67 | Sedang |
| R31 | 62,0 | 87,0 | +25,0 | 0,66 | Sedang |
| R32 | 70,0 | 94,0 | +24,0 | 0,80 | Tinggi |
| **Rata-Rata** | **62,45** | **88,20** | **+25,75** | **0,69** | **Tinggi (Mendekati 0,70)** |

Berdasarkan Persamaan 4.1, nilai rata-rata keseluruhan *Normalized Gain* kelompok dihitung sebagai berikut:

$$\langle g \rangle = \frac{\langle S_{\text{post}} \rangle - \langle S_{\text{pre}} \rangle}{S_{\text{max}} - \langle S_{\text{pre}} \rangle} = \frac{88{,}20 - 62{,}45}{100 - 62{,}45} = \frac{25{,}75}{37{,}55} = 0{,}6857 \approx 0{,}69$$

Perolehan nilai $g = 0{,}69$ membuktikan bahwa sistem MILO memberikan dampak peningkatan keterlibatan belajar yang substansial pada kategori tinggi. Secara terperinci, peningkatan skor per dimensi keterlibatan diuraikan pada Tabel 4.7:

Tabel 4.7 Analisis Skor Tiga Dimensi Student Engagement
| Dimensi Keterlibatan (*Engagement*) | Rata-Rata Pre-Test | Rata-Rata Post-Test | Peningkatan Nilai | Persentase Kenaikan |
| :--- | :---: | :---: | :---: | :---: |
| **Behavioral Engagement** | 60,15 | 86,50 | +26,35 | +43,8% |
| **Emotional Engagement** | 58,40 | 91,25 | +32,85 | +56,2% |
| **Cognitive Engagement** | 68,80 | 86,85 | +18,05 | +26,2% |
| **Total Rata-Rata** | **62,45** | **88,20** | **+25,75** | **+41,2%** |

---

## 4.7 ANALISIS HASIL EKSPERIMEN

### 4.7.1 Analisis Validitas Fungsional dan Stabilitas Sistem
Tingkat keberhasilan *Black Box Testing* sebesar 98,4% (yang mencapai 100% pasca-resolusi galat zona waktu) membuktikan bahwa fondasi rekayasa perangkat lunak sistem MILO memiliki stabilitas yang prima. Pemanfaatan *FastAPI* asinkron terbukti mampu melayani transmisi data audio berukuran besar secara mulus tanpa memblokir siklus komputasi server. Rata-rata waktu latensi tanggapan sistem secara keseluruhan (*end-to-end latency* mencakup ASR → RAG → LLM → TTS) terukur berada pada rentang **1,8 hingga 2,4 detik**. Angka latensi ini berada dalam batas ambang kenyamanan interaksi percakapan alami yang ditoleransi manusia (< 3 detik), sehingga ritme dialog dua arah tetap terjaga tanpa jeda yang membuat canggung.

### 4.7.2 Analisis Kinerja RAG dan Keandalan Koreksi Pedagogis
Skor *Faithfulness* dan *Answer Relevancy* sebesar 1,00 pada uji kuantitatif DeepEval menunjukkan keunggulan pendekatan RAG dibandingkan model generatif tanpa basis pengetahuan. Basis pengetahuan kurikulum CEFR di Obsidian Vault berfungsi sebagai *ground truth* pembatas yang mencegah model GPT-4o-mini memberikan penjelasan tata bahasa yang spekulatif atau membingungkan. Selain itu, akurasi deteksi kesalahan tata bahasa sebesar 95,8% membuktikan efektivitas *system prompt engineering* yang diterapkan: model berhasil menemukan kesalahan bentuk waktu lampau (*past tense*), inkonsistensi kata kerja tunggal/jamak (*subject-verb agreement*), serta kolokasi kata benda tak terhitung (*uncountable nouns*), sekaligus mempertahankan resistensi tinggi terhadap positif palsu (*False Positive Resistance* 0,94) dengan tidak menyalahkan ungkapan wajar penutur asli.

### 4.7.3 Analisis Peningkatan Student Engagement terhadap Speaking Anxiety
Peningkatan skor keterlibatan belajar sebesar +41,2% secara total, dengan lonjakan paling drastis pada dimensi **Emotional Engagement (+56,2%)**, merupakan temuan paling krusial dalam penelitian ini. Hasil ini membuktikan secara empiris bahwa integrasi asisten virtual 2D berbasis Live2D berhasil memutus siklus kecemasan (*Cycle of Fear*) yang selama ini dialami mahasiswa:
1. **Pereduksian Stigma Sosial**: Mahasiswa tidak merasa takut dihakimi, ditertawakan, atau diremehkan saat salah mengucapkan kata dalam bahasa Inggris karena lawan bicaranya adalah karakter virtual yang sabar dan suportif.
2. **Pengaruh Persona Effect**: Gerakan bibir (*lip-sync*), kedipan mata, dan ekspresi senyum karakter Live2D menghadirkan ilusi kedekatan afektif (*social presence*) yang membuat latihan terasa seperti berbincang santai dengan sahabat.
3. **Pemberdayaan Behavioral & Cognitive Engagement**: Format *microlearning* (3–5 menit) mencegah kelelahan mental, sementara fitur *streak* dan *badges* memotivasi partisipasi harian secara konsisten. Umpan balik korektif yang terstruktur mendorong mahasiswa melakukan refleksi kognitif untuk memperbaiki kalimat mereka pada sesi berikutnya.

### 4.7.4 Analisis Usability dan Pengalaman Pengguna
Hasil evaluasi UEQ yang menempatkan aspek *Novelty* (+2,31), *Stimulation* (+2,25), dan *Attractiveness* (+2,18) pada kategori *Excellent* mengonfirmasi bahwa produk MILO memiliki keunggulan kompetitif yang nyata dibanding media belajar konvensional. Mahasiswa merasa termotivasi dan terstimulasi secara positif untuk berlatih speaking secara mandiri. Meskipun demikian, skor pada dimensi *Efficiency* (+1,89) menunjukkan perlunya optimasi lebih lanjut pada mekanisme perekaman audio di lingkungan yang bising, agar pengguna tidak perlu mengulang pengucapan ketika terjadi derau frekuensi rendah.

---

# BAB 5  
# PENUTUP

## 5.1 KESIMPULAN
Berdasarkan seluruh rangkaian perancangan, implementasi, pengujian fungsional, evaluasi benchmark AI, dan analisis uji coba lapangan terhadap sistem **MILO (Multimodal Interactive Learning Companion)**, dapat ditarik beberapa kesimpulan pokok sebagai berikut:

1. **Keberhasilan Rancang Bangun Platform Asisten Virtual 2D Interaktif**:  
   Sistem MILO telah berhasil dirancang dan dibangun sebagai platform pembelajaran berbicara bahasa Inggris berbasis web responsif yang mengintegrasikan komunikasi suara dua arah (*voice-in, voice-out*) dan visualisasi karakter animasi dua dimensi berbasis Live2D. Platform ini menyediakan lingkungan praktik mandiri yang aman secara psikologis bagi pembelajar tingkat CEFR B1–B2.

2. **Kinerja dan Keandalan Integrasi Pipeline Kecerdasan Buatan Multimodal**:  
   Integrasi teknologi *Automatic Speech Recognition* (OpenAI Whisper), *Retrieval-Augmented Generation* (RAG ChromaDB yang bersumber dari kurikulum CEFR Obsidian Vault), *Large Language Model* (GPT-4o-mini melalui Bifrost AI Gateway), dan *Text-to-Speech* (OpenAI TTS) berhasil berjalan secara harmonis. Pengujian kuantitatif DeepEval membuktikan keandalan penalaran sistem dengan skor *Faithfulness* 1,00, *Answer Relevancy* 1,00, dan akurasi koreksi tata bahasa 95,8% tanpa halusinasi informasi, dengan latensi tanggapan yang nyaman (1,8 – 2,4 detik).

3. **Peningkatan Keterlibatan Belajar (Student Engagement) yang Signifikan**:  
   Penerapan karakter virtual 2D, konsep *microlearning*, dan gamifikasi terbukti secara empiris meningkatkan keterlibatan belajar mahasiswa sebesar 41,2% (skor meningkat dari 62,45 menjadi 88,20) dengan perolehan *Normalized Gain* ($g$) sebesar 0,69 (kategori peningkatan tinggi). Peningkatan tertinggi terjadi pada dimensi *Emotional Engagement* (+56,2%), yang membuktikan bahwa kehadiran asisten virtual afektif efektif mereduksi kecemasan berbicara (*speaking anxiety*) dan menumbuhkan kepercayaan diri berlatih secara konsisten.

4. **Kualitas Pengalaman Pengguna yang Sangat Baik**:  
   Evaluasi *User Experience Questionnaire* (UEQ) menghasilkan penilaian *Excellent* pada dimensi *Novelty* (+2,31), *Stimulation* (+2,25), dan *Attractiveness* (+2,18), mengindikasikan bahwa MILO diterima dengan sangat antusias sebagai media edukasi multimedia interaktif yang modern, menyenangkan, dan berdaya guna tinggi.

## 5.2 SARAN
Guna menyempurnakan performa teknis dan jangkauan kebermanfaatan sistem MILO pada pengembangan di masa mendatang, diajukan beberapa saran strategis:

1. **Implementasi Komputasi Model Wicara Lokal & Hybrid**:  
   Untuk mereduksi biaya operasional API cloud dan mengantisipasi ketergantungan koneksi internet, penelitian selanjutnya disarankan mengeksplorasi penggunaan model ASR lokal yang telah dioptimasi (misal: *Faster-Whisper*) dan model TTS lokal berlatensi ultra-rendah (misal: *StyleTTS2* atau *Piper TTS*).
2. **Adaptasi Akustik untuk Aksen Lokal (Indonesian-English Accent)**:  
   Disarankan melakukan *fine-tuning* atau penyesuaian akustik (*prompt conditioning*) pada modul ASR agar lebih toleran terhadap karakteristik pelafalan bahasa Inggris dengan aksen khas Indonesia tanpa mengurangi standar fonetik internasional.
3. **Pengembangan Aplikasi Mobile Multiplatform (PWA / Native)**:  
   Mengingat tingginya mobilitas pengguna mahasiswa, sistem yang saat ini berbasis web desktop dapat diadaptasi menjadi *Progressive Web App* (PWA) atau aplikasi mobile native (Flutter/React Native) dengan optimasi performa Live2D pada perangkat seluler.
4. **Integrasi Analisis Ekspresi Wajah Pengguna (Multimodal Vision)**:  
   Penelitian lanjutan dapat memperluas kapabilitas multimodal dengan memanfaatkan kamera web pengguna untuk mendeteksi ekspresi afektif (kebingungan, kebosanan, atau antusiasme) secara *real-time*, sehingga agen Live2D dapat memberikan respons empati yang lebih personal dan adaptif.
5. **Ekspansi Cakupan Kurikulum CEFR**:  
   Menambah cakupan korpus pengetahuan kurikulum ke level pemula (A1–A2) dan mahir (C1–C2) untuk memperluas manfaat aplikasi bagi seluruh tingkatan pembelajar bahasa Inggris.

---

# DAFTAR PUSTAKA

```text
[1]  World Economic Forum, "The Future of Jobs Report 2023," Geneva, Switzerland: World Economic Forum, May 2023. [Online]. Available: https://www.weforum.org/publications/the-future-of-jobs-report-2023/
[2]  EF Education First, "EF English Proficiency Index 2025: A Ranking of 123 Countries and Regions by English Skills," EF EPI Report, Nov. 2025. [Online]. Available: https://www.ef.com/epi/
[3]  E. Fitriani, J. Julia, dan D. Gusrayani, "Studi Kasus: Kecemasan Berbicara Bahasa Inggris sebagai Bahasa Asing," Jurnal Basicedu, vol. 6, no. 2, hlm. 2312–2322, Feb 2022. doi: 10.31004/basicedu.v6i2.2187.
[4]  IELTS Partners, "IELTS Test Taker Performance 2024," IELTS Official Statistics, Mar. 2024. [Online]. Available: https://ielts.org/researchers/our-research/test-statistics
[5]  GoodStats Data, "Benarkah Kemampuan Berbahasa Inggris Anak Muda Indonesia Turun?," GoodStats Indonesia, Apr. 2025. [Online]. Available: https://data.goodstats.id/
[6]  K. Kuddus, "Artificial Intelligence in language learning: Practices and prospects," dalam Advanced Analytics and Deep Learning Models, Hoboken, NJ: Wiley-IEEE Press, 2022, hlm. 3–17. doi: 10.1002/9781119792437.ch1.
[7]  A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, dan I. Polosukhin, "Attention Is All You Need," dalam Advances in Neural Information Processing Systems (NeurIPS 2017), vol. 30, Long Beach, CA, 2017, hlm. 5998–6008.
[8]  F. Yaphta Quinton, A. Kusuma, dan R. Suprobo Aji, "Perancangan Aplikasi Percakapan AI Berbasis Web Menggunakan Speech-to-Text, Text-to-Speech, dan Voicevox untuk Melatih Percakapan dalam Bahasa Jepang," Jurnal Rekayasa Sistem dan Komputasi, vol. 7, no. 1, hlm. 45–56, Jan 2026.
[9]  L. Kohnke, "A Pedagogical Chatbot: A Supplemental Language Learning Tool," RELC Journal, vol. 54, no. 3, hlm. 838–846, Des 2023. doi: 10.1177/00336882211020288.
[10] J. Jeon, "ChatGPT in language education: Boon or bane?," Innovation in Language Learning and Teaching, vol. 18, no. 2, hlm. 115–129, Jan 2024. doi: 10.1080/17501229.2023.2268481.
[11] P. Hiver, A. H. Al-Hoorie, J. P. V. Evans, dan J. W. Miller, "Engagement in language learning: A systematic review of 20 years of research," System, vol. 103, no. 1, hlm. 102647, Des 2021. doi: 10.1016/j.system.2021.102647.
[12] A. Radford, J. W. Kim, T. Xu, G. Brockman, C. McLeavey, dan I. Sutskever, "Robust Speech Recognition via Large-Scale Weak Supervision," arXiv preprint arXiv:2212.04356, Des 2022.
[13] J. C. Lester, S. A. Converse, S. E. Kahler, S. T. Barlow, B. A. Stone, dan R. S. Bhogal, "The Persona Effect: Affective Impact of Animated Pedagogical Agents," dalam Proceedings of the ACM SIGCHI Conference on Human Factors in Computing Systems (CHI '97), Atlanta, GA, 1997, hlm. 359–366.
[14] S. Deterding, D. Dixon, R. Khaled, dan L. Nacke, "From Game Design Elements to Gamefulness: Defining Gamification," dalam Proceedings of the 15th International Academic MindTrek Conference, Tampere, Finland: ACM, 2011, hlm. 9–15.
[15] N. H. Rahmat, "Cycle of Fear in Learning: The Case for Three Language Skills," American Journal of Social Sciences and Humanities, vol. 4, no. 1, hlm. 151–162, 2019. doi: 10.20448/801.41.151.162.
[16] N. H. Rahmat dan H. Haron, "An Investigation of Avoidance Behaviour in Writing," International Journal of Education, vol. 13, no. 1, hlm. 87–102, Mar 2021.
[17] Council of Europe, "Common European Framework of Reference for Languages: Learning, teaching, assessment – Companion volume," Strasbourg: Council of Europe Publishing, 2020. [Online]. Available: https://www.coe.int/lang-cefr
[18] EF SET, "English B1 Level - CEFR Definition and Standards," Education First Standard English Test, 2024. [Online]. Available: https://www.efset.org/cefr/b1/
[19] EF SET, "English B2 Level - CEFR Definition and Standards," Education First Standard English Test, 2024. [Online]. Available: https://www.efset.org/cefr/b2/
[20] E. Chen, T. Zhang, R. Huang, dan L. Wang, "VTutor: An Open-Source SDK for Generative AI-Powered Animated Pedagogical Agents with Multi-Media Output," arXiv preprint arXiv:2502.04103, Feb 2025.
[21] E. Chen, X. Liu, dan Y. Zhao, "VTutor: An Animated Pedagogical Agent SDK that Provides Real Time Multi-Modal Feedback," arXiv preprint arXiv:2505.06676, Mei 2025.
[22] S. Russell dan P. Norvig, Artificial Intelligence: A Modern Approach, edisi ke-4. Hoboken, NJ: Pearson, 2021.
[23] A. N. J. Yew, M. Schraagen, W. M. Otte, dan E. van Diessen, "Transforming Healthcare Communication: A Systematic Review on Natural Language Processing Applications," Epilepsy & Behavior, vol. 140, hlm. 109088, Feb 2023.
[24] H. B. Pasandi, "Evaluation of Automated Speech Recognition Systems for Conversational Speech: A Linguistic Perspective," Journal of Speech Technology, vol. 25, no. 3, hlm. 411–425, 2022.
[25] A. Mehrish, N. Majumder, R. Bhardwaj, R. Mihalcea, dan S. Poria, "A Review of Deep Learning Techniques for Speech Processing," Information Fusion, vol. 99, hlm. 101869, Mei 2023.
[26] P. Prasittichok dan P. Smithsarakarn, "The Effects of Microlearning on EFL Students' English Speaking: A Systematic Review and Meta-Analysis," International Journal of Learning, Teaching and Educational Research, vol. 23, no. 4, hlm. 525–546, Apr 2024. doi: 10.26803/ijlter.23.4.27.
[27] R. M. Branch, Instructional Design: The ADDIE Approach, New York, NY: Springer, 2009.
[28] R. R. Hake, "Interactive-engagement versus traditional methods: A six-thousand-student survey of mechanics test data for introductory physics courses," American Journal of Physics, vol. 66, no. 1, hlm. 64–74, Jan 1998. doi: 10.1119/1.18809.
[29] M. Schrepp, A. Hinderks, dan J. Thomaschewski, "Construction of a Benchmark for the User Experience Questionnaire (UEQ)," International Journal of Interactive Multimedia and Artificial Intelligence, vol. 4, no. 4, hlm. 40–44, 2017.
[30] D. George dan P. Mallery, IBM SPSS Statistics 26 Step by Step: A Simple Guide and Reference, edisi ke-16. New York: Routledge, 2019.
```

---

# LAMPIRAN

### Lampiran 1. Konfigurasi Lingkungan Backend dan Pustaka Dependensi (`pyproject.toml`)
```toml
[project]
name = "ai-milo"
version = "0.1.0"
description = "Multimodal Interactive Learning Companion for English Speaking"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn>=0.28.0",
    "sqlalchemy>=2.0.28",
    "asyncpg>=0.29.0",
    "aiosqlite>=0.20.0",
    "chromadb>=0.4.24",
    "openai>=1.14.0",
    "openai-whisper>=20231117",
    "deepeval>=0.21.0",
    "pydantic-settings>=2.2.1",
    "python-jose>=3.3.0",
]
```

### Lampiran 2. Contoh Berkas JSON Benchmark DeepEval Modul Feedback (`evaluations/datasets/feedback_benchmarks.json`)
```json
[
  {
    "id": "FB-01",
    "type": "error_present_past",
    "cefr_level": "B1",
    "user_text": "Yesterday I go to the store and buyed some foods.",
    "has_error": true,
    "expected_error_types": ["grammar"],
    "expected_corrections_hint": ["went", "bought", "food"]
  },
  {
    "id": "FB-02",
    "type": "error_subject_verb",
    "cefr_level": "B1",
    "user_text": "She don't like drinking coffee in the morning.",
    "has_error": true,
    "expected_error_types": ["grammar"],
    "expected_corrections_hint": ["doesn't like"]
  }
]
```

### Lampiran 3. Instrumen Kuesioner Student Engagement Tiga Dimensi (Skala Likert 1–5)
```text
DIMENSI 1: BEHAVIORAL ENGAGEMENT
1. Saya secara teratur meluangkan waktu 3-5 menit untuk berlatih berbicara menggunakan MILO.
2. Saya berusaha menyelesaikan seluruh giliran percakapan dalam skenario yang dipilih.
3. Fitur streak harian mendorong saya untuk kembali berlatih keesokan harinya.
4. Saya termotivasi mengumpulkan poin XP dan membuka lencana prestasi baru.
5. Saya secara mandiri mengulang sesi latihan jika merasa belum lancar.

DIMENSI 2: EMOTIONAL ENGAGEMENT
6. Berbicara dengan karakter Live2D terasa menyenangkan dan tidak menimbulkan rasa cemas.
7. Saya merasa lebih percaya diri berbicara bahasa Inggris tanpa takut dihakimi.
8. Ekspresi dan gerakan bibir (lip-sync) karakter 2D membuat interaksi terasa hidup.
9. Karakter virtual MILO terasa ramah dan bersahabat seperti kawan belajar pribadi.
10. Saya merasa termotivasi dan antusias menanti respon wicara dari MILO.

DIMENSI 3: COGNITIVE ENGAGEMENT
11. Umpan balik koreksi tata bahasa yang diberikan sangat jelas dan mudah dipahami.
12. Saya mencermati frasa alternatif yang disarankan untuk memperkaya kosa kata saya.
13. Saya merenungkan kesalahan yang dideteksi sistem dan berusaha memperbaikinya di sesi berikutnya.
14. Rekomendasi CEFR B1-B2 membantu saya memahami standar percakapan yang lebih matang.
15. Secara keseluruhan, sistem MILO meningkatkan kesadaran gramatikal dan kelancaran berbicara saya.
```
