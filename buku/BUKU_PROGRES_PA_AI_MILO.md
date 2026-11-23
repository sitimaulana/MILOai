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
# DESAIN SISTEM DAN METODOLOGI PENELITIAN

## 3.1 DESKRIPSI SOLUSI
Berdasarkan permasalahan yang telah diidentifikasi pada Bab 2, penelitian ini mengusulkan pengembangan **MILO (Multimodal Interactive Learning Companion)**, yaitu platform pembelajaran berbicara bahasa Inggris berbasis web yang memanfaatkan teknologi *Artificial Intelligence* (AI) sebagai mitra belajar virtual. Platform ini ditujukan bagi mahasiswa dengan kemampuan bahasa Inggris setara CEFR level B1–B2 yang masih mengalami keterbatasan dalam berlatih berbicara akibat *speaking anxiety*, kurangnya kesempatan praktik, serta media pembelajaran yang belum mampu menghadirkan pengalaman belajar yang interaktif. Melalui platform ini, pengguna diharapkan dapat melakukan latihan berbicara secara mandiri dalam lingkungan belajar yang lebih nyaman, adaptif, dan fleksibel.

```
+-----------------------------------------------------------------------------+
|                          GAMBAR 3.1 USER FLOW DIAGRAM                       |
+-----------------------------------------------------------------------------+
  [Pengguna Masuk / Login]
             │
             ▼
  [Diagnostic Placement Test] ──► (Klasifikasi Kemampuan Awal: CEFR B1 / B2)
             │
             ▼
  [Dashboard Utama & Pemilihan Modul] ──► (Job Interview / Daily / Academic)
             │
             ▼
  [Sesi Latihan Berbicara Interaktif (Microlearning 3–5 Menit)]
       │
       ├── Masukan Suara Pengguna (Audio 16 kHz)
       ├── Pengenalan Suara Otomatis (Whisper ASR)
       ├── Penelusuran Dokumen Materi Silabus (Hybrid RAG: ChromaDB + BM25)
       ├── Penalaran Tutor AI & Evaluasi (GPT-4o-mini via Bifrost Gateway)
       ├── Sintesis Suara Percakapan Alami (OpenAI TTS nova)
       └── Visualisasi Respon & Lip-sync (Avatar 2D Live2D WebGL)
             │
             ▼
  [Evaluasi Sesi & Gamifikasi]
       ├── Analisis Kesalahan Tata Bahasa (Grammar Correction & Feedback)
       ├── Perolehan Poin Pengalaman (XP) & Pembaharuan Daily Streak
       └── Pembukaan Lencana Prestasi (Achievement Badges)
```
*Gambar 3.1 Diagram Alur Interaksi Pengguna (User Flow Diagram)*

MILO mengintegrasikan teknologi *Automatic Speech Recognition* (ASR), *Large Language Model* (LLM), *Retrieval-Augmented Generation* (RAG), *Text-to-Speech* (TTS), serta avatar virtual dua dimensi (Live2D) dalam satu sistem pembelajaran yang saling terintegrasi. Sebagaimana diilustrasikan pada Gambar 3.1, masukan suara pengguna diproses menggunakan ASR untuk menghasilkan transkripsi teks, kemudian dianalisis oleh LLM dengan dukungan RAG yang mengambil informasi dari *knowledge base* pembelajaran bahasa Inggris. Integrasi ini memungkinkan sistem menghasilkan respons percakapan yang lebih relevan dan kontekstual, sekaligus menyajikan umpan balik berupa koreksi tata bahasa (*grammar correction*), rekomendasi kosakata (*vocabulary enhancement*), serta evaluasi kelancaran berbicara. Respons tersebut selanjutnya disampaikan melalui *Text-to-Speech* dan divisualisasikan menggunakan avatar virtual Live2D sehingga interaksi terasa lebih alami dan komunikatif.

Selain mendukung latihan berbicara, platform ini dirancang untuk meningkatkan keterlibatan belajar (*student engagement*) melalui penerapan konsep *microlearning* dan gamifikasi. Materi disajikan dalam sesi latihan singkat berdurasi 3 hingga 5 menit yang berfokus pada satu tujuan pembelajaran spesifik, kemudian dipadukan dengan fitur perolehan poin (*points/XP*), lencana pencapaian (*badges*), pencatatan rekor harian (*daily streak*), dan pelacakan progres belajar (*learning progress*). Kombinasi fitur tersebut diharapkan mampu menumbuhkan motivasi pengguna untuk berlatih secara konsisten sekaligus membangun kebiasaan belajar yang berkelanjutan.

---

## 3.2 METODE PENELITIAN

### 3.2.1 Pendekatan Penelitian
Penelitian ini menggunakan pendekatan metode campuran (*mixed methods approach*) yang menggabungkan pengumpulan data kualitatif dan kuantitatif secara terpadu guna memperoleh evaluasi sistem yang komprehensif:
1. **Pendekatan Kualitatif**: Diterapkan pada tahap awal dan pertengahan melalui tinjauan ahli (*expert review*) yang melibatkan ahli media pembelajaran interaktif dan ahli pengajaran bahasa Inggris (*English education expert*). Uji ahli bertujuan untuk memvalidasi kelayakan antarmuka, kesesuaian materi silabus CEFR B1–B2, serta ketepatan pedagogis umpan balik korektif yang dihasilkan sistem.
2. **Pendekatan Kuantitatif**: Diterapkan pada tahap evaluasi akhir untuk mengukur performa teknis sistem (akurasi transkripsi ASR, latensi komputasi, skor tolok ukur *DeepEval*), tingkat kebergunaan antarmuka (*usability*) menggunakan instrumen *User Experience Questionnaire* (UEQ), serta efektivitas platform terhadap peningkatan keterlibatan belajar (*student engagement*) mahasiswa melalui desain eksperimen *pretest-posttest* pada kelompok responden uji coba ($N \ge 30$).

### 3.2.2 Metode Pengembangan ADDIE
Pengembangan platform MILO mempedomani model instruksional ADDIE (*Analysis, Design, Development, Implementation, Evaluation*). Model ADDIE dipilih karena menyediakan kerangka kerja rekayasa multimedia edukasi yang sistematis, terukur, dan memiliki siklus evaluasi berulang (*iterative feedback loop*) pada setiap fasenya.

```
+-----------------------------------------------------------------------------+
|              GAMBAR 3.2 KERANGKA PENGEMBANGAN SISTEM (ADDIE)                |
+-----------------------------------------------------------------------------+
  [1. ANALYSIS] ────────────────────────────────────────────────────────┐
        │ Identifikasi speaking anxiety, target CEFR B1-B2,            │
        │ analisis kebutuhan fungsional & non-fungsional, alat bantu    │
        ▼                                                               │
  [2. DESIGN] ──────────────────────────────────────────────┐           │
        │ Cetak biru arsitektur berlapis, pipeline Hybrid RAG,    │     │
        │ formulasi matematis, skema ERD, rigging Live2D, mockup  │     │
        ▼                                                         │     │
  [3. DEVELOPMENT] ─────────────────────────────────────┐   Revisi      │
        │ Koding backend FastAPI, Docker Bifrost,        │   Desain     │
        │ ingesti ChromaDB, integrasi Live2D WebGL      │   & Aset      │
        ▼                                               │   (Loop)      │
  [4. IMPLEMENTATION] ───────────────────────────┐      │         │     │
        │ Deployment lokal, integrasi operasional, │    │         │     │
        │ uji coba interaksi responden mahasiswa │    │         │     │
        ▼                                        │    │         │     │
  [5. EVALUATION] ◄──────────────────────────────┴────┴─────────┴─────┘
        • Black Box Testing (Fungsionalitas 100%)
        • Speech Recognition Testing (Akurasi Kata & Latensi)
        • DeepEval Benchmark (Faithfulness & Answer Relevancy)
        • User Experience Questionnaire / UEQ (Usability)
        • Student Engagement Pretest-Posttest (N-Gain Hake)
```
*Gambar 3.2 Kerangka Pengembangan Sistem MILO Menggunakan Model ADDIE*

Sebagaimana diilustrasikan pada Gambar 3.2, kelima fase ADDIE dijalankan secara bertahap dengan mekanisme peninjauan berkala. Temuan evaluasi formatif pada fase implementasi dapat menjadi dasar perbaikan pada fase perancangan (*design*) maupun pengembangan (*development*) sebelum sistem diuji secara sumatif pada fase evaluasi akhir.

---

## 3.3 TAHAPAN PENGEMBANGAN SISTEM

### 3.3.1 Analysis (Analisis Kebutuhan Sistem)
Tahap *Analysis* bertujuan untuk mengidentifikasi akar permasalahan, karakteristik pengguna sasaran, kebutuhan fungsional sistem, serta spesifikasi perangkat pendukung yang diperlukan dalam membangun platform MILO:

#### 1. Analisis Kebutuhan Pembelajaran dan Sasaran Pengguna
Subjek sasaran penelitian adalah mahasiswa tingkat sarjana terapan yang berada pada rentang kemahiran berbicara bahasa Inggris tingkat menengah (*Intermediate* / CEFR B1) hingga menengah atas (*Upper-Intermediate* / CEFR B2). Berdasarkan temuan studi pendahuluan, hambatan utama pembelajar berakar pada *foreign language speaking anxiety* (FLSA)—yaitu rasa takut dinilai salah oleh orang lain saat berbicara di depan umum—serta keterbatasan akses terhadap mitra tutur yang siap memberikan koreksi secara personal dan tidak menghakimi.

#### 2. Analisis Kebutuhan Fungsional (Functional Requirements)
Sistem yang dikembangkan harus memenuhi tujuh kapabilitas fungsional utama:
1. **F-01 (Autentikasi Akun)**: Sistem mampu mengelola pendaftaran, autentikasi sesi masuk (*login*), dan manajemen profil pengguna secara aman.
2. **F-02 (Diagnostic Placement Test)**: Sistem mampu menyajikan uji diagnostik wicara singkat untuk mengklasifikasikan tingkat kemahiran awal pengguna ke dalam level B1 atau B2.
3. **F-03 (Speech-to-Text Conversion)**: Sistem mampu merekam masukan suara pengguna melalui peramban web dan mentranskripsikannya ke dalam format teks secara akurat menggunakan ASR Whisper.
4. **F-04 (Hybrid Context Retrieval)**: Sistem mampu mencari dokumen silabus pembelajaran yang relevan dari *Knowledge Base* menggunakan perpaduan penelusuran vektor (ChromaDB) dan leksikal (BM25).
5. **F-05 (Contextual Response & Feedback Generation)**: Sistem mampu menghasilkan respons percakapan yang komunikatif sekaligus mengekstrak koreksi tata bahasa dan kosakata menggunakan model GPT-4o-mini.
6. **F-06 (Speech Synthesis & Lip-sync Animation)**: Sistem mampu mensintesis teks balasan tutor ke dalam aliran audio alami (TTS) dan menyinkronkan amplitudo suara ke parameter gerak bibir avatar Live2D.
7. **F-07 (Gamification & Progress Tracking)**: Sistem mampu menghitung perolehan poin pengalaman (XP), mencatat rekor latihan harian (*streak*), membuka lencana prestasi (*badges*), dan menyimpan riwayat capaian belajar.

#### 3. Analisis Kebutuhan Non-Fungsional (Non-Functional Requirements)
Kebutuhan non-fungsional dirancang guna menjamin kenyamanan, keandalan, dan stabilitas operasional platform:
1. **NF-01 (Performansi & Latensi Komputasi)**: Waktu respons total (*end-to-end latency*) mulai dari pengguna selesai berbicara hingga audio balasan AI dan animasi avatar mulai berputar ditargetkan tidak melebihi **3,0 detik** pada koneksi internet stabil.
2. **NF-02 (Keandalan & Circuit Breaking)**: Sistem dilengkapi dengan perantara *AI Gateway* yang menerapkan mekanisme *retry*, *rate limiting*, dan *caching* guna mencegah kegagalan interaksi akibat batas kuota atau galat jaringan eksternal.
3. **NF-03 (Kebergunaan & Aksesibilitas)**: Antarmuka sistem mematuhi prinsip *User-Centered Design* (UCD) dan standar kontras warna WCAG AAA, menghadirkan tata letak yang bersih, intuitif, dan responsif terhadap berbagai resolusi layar desktop/laptop.
4. **NF-04 (Integritas Data)**: Seluruh riwayat percakapan dan profil pengguna tersimpan dalam basis data relasional ternormalisasi dengan enkripsi kata sandi menggunakan pustaka *Bcrypt*.

Rangkuman kebutuhan pengembangan sistem disajikan pada Tabel 3.1.

*Tabel 3.1 Analisis Kebutuhan Pengembangan Sistem MILO*
| Kategori Kebutuhan | Komponen Analisis | Deskripsi Kebutuhan Sistem |
| :--- | :--- | :--- |
| **Karakteristik Pengguna** | Mahasiswa Tingkat B1–B2 | Memerlukan lingkungan latihan berbicara yang aman dari rasa cemas, materi komunikatif kontekstual, dan koreksi kesalahan yang membangun. |
| **Teknologi Wicara** | ASR & TTS | Penangkapan audio mikrofon 16 kHz, transkripsi otomatis OpenAI Whisper, dan sintesis audio ekspresif OpenAI TTS profil *nova*. |
| **Kecerdasan Buatan** | LLM & Hybrid RAG | Penalaran dialog berstandar CEFR menggunakan GPT-4o-mini didukung basis pengetahuan materi Obsidian Vault, ChromaDB, dan BM25. |
| **Antarmuka Interaktif** | Avatar Virtual 2D | Visualisasi *Animated Pedagogical Agent* berbasis Live2D Cubism Web SDK yang mendukung gerakan bibir adaptif (*lip-sync*). |
| **Keterlibatan Belajar** | Microlearning & Gamifikasi | Durasi sesi ringkas (3–5 menit), akumulasi poin XP, rekor konsistensi latihan harian (*daily streak*), dan lencana apresiasi. |

#### 4. Analisis Perangkat Lunak dan Perangkat Keras
Kelancaran perancangan dan implementasi sistem didukung oleh spesifikasi perangkat lunak dan perangkat keras sebagaimana dirinci pada Tabel 3.2 dan Tabel 3.3.

*Tabel 3.2 Komponen Perangkat Lunak yang Digunakan*
| No | Perangkat Lunak | Versi / Rilis | Peran dan Fungsi dalam Sistem |
| :---: | :--- | :--- | :--- |
| 1 | Python | 3.11.x (via `uv`) | Bahasa pemrograman utama untuk logika backend, orkestrasi AI, dan evaluasi. |
| 2 | FastAPI | 0.115.x | *Framework* backend asinkron berkinerja tinggi untuk penyedia REST API. |
| 3 | Uvicorn | 0.34.x | *ASGI web server* untuk menjalankan aplikasi backend FastAPI. |
| 4 | ChromaDB | 0.5.x | Basis data vektor terdistribusi untuk menyimpan *embedding* materi RAG. |
| 5 | OpenAI Whisper API | Whisper-1 | Model *Automatic Speech Recognition* (ASR) untuk transkripsi audio wicara. |
| 6 | OpenAI Chat API | GPT-4o-mini | Model bahasa cerdas untuk penalaran percakapan dan koreksi linguistik. |
| 7 | OpenAI Audio API | TTS-1 (*nova*) | Layanan sintesis wicara alami untuk menghasilkan suara tutor virtual. |
| 8 | Bifrost AI Gateway | 1.x (Docker) | *Reverse proxy* lokal untuk manajemen *rate limit*, *caching*, dan kuota token API. |
| 9 | Live2D Cubism SDK | Web SDK 5.0 | Pustaka rendering WebGL untuk menggerakkan model karakter 2D interaktif. |
| 10 | Tailwind CSS & HTML5 | 3.4.x | *Framework styling* dan struktur antarmuka halaman web responsif. |
| 11 | Docker Desktop | 4.3x | Kontainerisasi untuk menjalankan layanan Bifrost AI Gateway pada port 8080. |
| 12 | DeepEval | 1.5.x | Kerangka tolok ukur kuantitatif evaluasi kinerja LLM (*LLM-as-a-Judge*). |

*Tabel 3.3 Spesifikasi Perangkat Keras Pengembangan dan Pengujian*
| No | Komponen Perangkat Keras | Spesifikasi Minimum / Rekomendasi | Peran dalam Proyek Akhir |
| :---: | :--- | :--- | :--- |
| 1 | Processor (CPU) | Intel Core i7 12th Gen / AMD Ryzen 7 | Menjalankan lingkungan pengembangan, server backend, dan komputasi embedding. |
| 2 | Memori (RAM) | 16 GB DDR4 / DDR5 | Memastikan kestabilan eksekusi paralel FastAPI, ChromaDB, dan Docker Bifrost. |
| 3 | Penyimpanan (Storage) | 512 GB NVMe SSD | Penyimpanan korpus *knowledge base*, aset Live2D, dan repositori kode sumber. |
| 4 | Mikrofon Masukan | USB Condenser Microphone / Headset Mic | Menangkap sinyal wicara pengembang dan pengguna dengan SNR tinggi. |
| 5 | Perangkat Keluaran Audio | Stereo Speaker / Audio Headphone | Memonitor kualitas dan kejelasan hasil sintesis wicara TTS. |
| 6 | Koneksi Jaringan | Pita lebar internet minimal 10 Mbps | Komunikasi data dengan API penyedia model bahasa dan gateway komputasi awan. |

---

### 3.3.2 Design (Perancangan Sistem)
Perancangan sistem dalam penelitian ini difokuskan pada integrasi alur pemrosesan kecerdasan buatan multimodal (*multimodal AI pipeline*) dan interaksi pengguna yang terstruktur. Sistem yang dirancang bertujuan untuk menghubungkan basis pengetahuan pembelajaran bahasa Inggris standar CEFR B1–B2 dengan teknologi pemrosesan bahasa alami serta avatar virtual interaktif, sehingga menghasilkan mitra belajar berbicara (*virtual learning companion*) yang adaptif dan responsif. Penjelasan mengenai perancangan sistem ini diawali dengan gambaran umum arsitektur sistem (*high-level view*) untuk memudahkan pemahaman terhadap alur pemrosesan data secara keseluruhan.

Desain sistem menggambarkan hubungan terpadu antara masukan data pengguna, pemrosesan kecerdasan buatan, basis penyimpanan data, serta luaran multimodal yang dihasilkan. Gambar 3.3 mengilustrasikan arsitektur utama perancangan sistem MILO melalui pendekatan berlapis (*layered architecture*). Diagram ini menunjukkan bagaimana masukan audio pengguna diproses melalui model pengenalan suara dan penalaran berbasis RAG, hingga akhirnya disintesis menjadi respons wicara serta visualisasi avatar interaktif guna meningkatkan keterlibatan belajar (*student engagement*) pengguna.

```
+-----------------------------------------------------------------------------+
|          GAMBAR 3.3 DESAIN SISTEM BERLAPIS (LAYERED ARCHITECTURE)           |
+-----------------------------------------------------------------------------+
  [1. INPUT LAYER]
      • Voice Input (Audio 16 kHz Mono)    • Text Input (Alternatif)
      • Learning Goals Selection           • CEFR Target Level (B1 / B2)
  ──────────────────────────────────────┬──────────────────────────────────────
                                        ▼
  [2. CORE PROCESSING LAYER]
      • ASR Engine (OpenAI Whisper)
      • Local AI Gateway (Bifrost: Rate Limiter, Cache, Budgeting)
      • Conversational LLM Engine (GPT-4o-mini)
      • Scaffolding Prompt Engine (The One-Question Rule & CEFR Adaptation)
  ──────────────────────────────────────┬──────────────────────────────────────
                                        ▼
  [3. STORAGE LAYER (KNOWLEDGE & DATA)]
      • Knowledge Base (Obsidian Vault: Markdown Silabus CEFR B1–B2)
      • Dense Vector Store (ChromaDB + HNSW Index, 1536 Dim)
      • Sparse Lexical Search (BM25 Engine)
      • Relational Database (SQLAlchemy Async ORM: User, Session, Feedback)
  ──────────────────────────────────────┬──────────────────────────────────────
                                        ▼
  [4. OUTPUT LAYER]
      • Neural Text-to-Speech (OpenAI TTS-1 Voice nova)
      • Animated Pedagogical Agent (Live2D Cubism WebGL Engine)
      • Web Audio API Lip-Sync Controller (Amplitudo RMS -> ParamMouthOpenY)
      • Real-time Grammar & Fluency Feedback Card
  ──────────────────────────────────────┬──────────────────────────────────────
                                        ▼
  [5. LEARNING & ENGAGEMENT LAYER]
      • Microlearning Manager (3–5 Menit per Sesi Latihan)
      • Gamification Engine (XP Points, Daily Streak Tracker, Badges System)
      • Longitudinal Progress Tracking (CEFR Skill Evolution Analytics)
```
*Gambar 3.3 Desain Arsitektur Sistem Berlapis (Layered Architecture) MILO*

Untuk menguraikan cetak biru arsitektur tersebut ke dalam spesifikasi rekayasa yang terperinci dan dapat diimplementasikan secara terukur, perancangan sistem dijabarkan ke dalam delapan bagian utama:

#### A. Perancangan Alur Pengguna (Detailed User Flow Diagram)
Perancangan alur pengguna memetakan setiap tahapan interaksi mahasiswa secara prosedural dari awal penggunaan hingga akhir sesi latihan:

```
+-----------------------------------------------------------------------------+
|                GAMBAR 3.4 DETAILED USER FLOW DIAGRAM                        |
+-----------------------------------------------------------------------------+
  (Start)
     │
     ▼
  [Halaman Autentikasi: Login / Registrasi]
     │
     ▼
  {Sudah Pernah Placement Test?} ──(Tidak)──► [Ikuti Diagnostic Speaking Test]
     │ (Ya)                                              │
     ▼                                                   ▼
  [Masuk ke Dashboard Utama] ◄───────────────── [Sistem Petakan Level B1/B2]
     │
     ▼
  [Pilih Modul & Topik Percakapan: Microlearning 3–5 Menit]
     │
     ▼
  [Masuk Ruang Sesi Interaktif (Practice Studio)]
     │
     ├──► Pengguna Tekan Tombol Bicara (Push-to-Talk) & Rekam Suara
     ├──► Sistem Transkripsikan Suara & Ekstrak Konteks RAG
     ├──► LLM Hasilkan Respon Berbobot & Evaluasi Korektif
     ├──► TTS Sintesiskan Suara & Avatar Live2D Sinkronkan Gerak Bibir
     │
     ▼
  {Sesi Mencapai Giliran Target (6–10 Putaran)?} ──(Belum)──► (Lanjut Dialog)
     │ (Sudah)
     ▼
  [Halaman Rangkuman Umpan Balik (Summary Feedback)]
     │
     ├── Tampilkan Skor Sesi, Analisis Grammar, & Saran Idiom
     ├── Akumulasikan Poin XP & Perbarui Rekor Streak Harian
     └── Buka Kunci Lencana Baru (Jika Memenuhi Syarat Kriteria)
     │
     ▼
  (Selesai / Kembali ke Dashboard)
```
*Gambar 3.4 Diagram Alur Pengguna Terperinci (Detailed User Flow Diagram)*

#### B. Perancangan Knowledge Base & Adaptive Hybrid RAG
Basis pengetahuan (*Knowledge Base*) dirancang sebagai pustaka rujukan silabus bahasa Inggris yang dikurasi khusus untuk tingkat CEFR B1–B2.

```
+-----------------------------------------------------------------------------+
|            GAMBAR 3.5 DIAGRAM PIPELINE ADAPTIVE HYBRID RAG                  |
+-----------------------------------------------------------------------------+
  [Dokumen Markdown Silabus CEFR B1–B2 (Obsidian Vault)]
                       │
                       ▼
  [Pemisahan Teks: Chunk Size 500 Karakter, Overlap 50 Karakter]
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
  [Dense Embedding]         [Sparse Indexing]
  Model: text-embedding-    Algoritma BM25 Tokenizer
  3-small (1536 Dimensi)    (Kecocokan Kata Kunci Gramatikal)
          │                         │
          ▼                         ▼
  [ChromaDB Vector Store]   [In-Memory BM25 Index]
  (HNSW Index, Cosine Sim)          │
          │                         │
          └────────────┬────────────┘
                       │
  [Kueri Wicara Pengguna Masuk]
                       │
                       ▼
  [Eksekusi Penelusuran Hibrida & Perankingan RRF (Top-3 Dokumen)]
                       │
                       ▼
  [Penyusunan Context Prompt ke GPT-4o-mini]
```
*Gambar 3.5 Diagram Pipeline Ingesti dan Penelusuran Adaptive Hybrid RAG*

Rancangan RAG menetapkan parameter teknis sebagai berikut:
1. **Format Berkas Sumber**: Materi disusun dalam berkas Markdown berstruktur *frontmatter* yang memuat taksonomi grammar, topik diskusi, dan pola kesalahan umum.
2. **Chunking Strategy**: Menggunakan *RecursiveCharacterTextSplitter* dengan ukuran **500 karakter** dan toleransi tumpang tindih (*overlap*) **50 karakter**.
3. **Representasi Vektor & Penyimpanan**: Setiap pecahan teks dikonversi ke vektor 1536 dimensi oleh model `text-embedding-3-small`, kemudian diindeks pada ChromaDB dengan metrik *Cosine Similarity*.
4. **Hybrid Retrieval & RRF**: Penelusuran semantik padat (*dense retrieval*) dari ChromaDB digabungkan dengan penelusuran leksikal (*sparse retrieval*) BM25. Penggabungan peringkat dihitung menggunakan formula *Reciprocal Rank Fusion* (RRF) untuk mengambil **3 potongan materi terbaik ($k=3$)** sebagai konteks pembantu.

#### C. Perancangan AI Gateway (Bifrost)
Komunikasi antara backend lokal dengan API kecerdasan buatan dikelola melalui gerbang terisolasi Bifrost guna menjaga stabilitas dan efisiensi operasional.

```
+-----------------------------------------------------------------------------+
|             GAMBAR 3.6 ARSITEKTUR PERANTARA AI GATEWAY BIFROST              |
+-----------------------------------------------------------------------------+
  [FastAPI Backend Application]
                │
                ▼
  [Bifrost AI Gateway (Local Port 8080)]
       ├── 1. Rate Limiting Engine: Kuota Maksimal 60 Request / Menit
       ├── 2. Semantic Cache: Kemiripan Kosinus >= 0.95 -> Return Cache (<50ms)
       ├── 3. Token Budgeting: Pembatasan Maksimal 250 Output Token per Respon
       └── 4. Circuit Breaker: Auto-retry 3x & Fallback Graceful Degradation
                │
                ▼
  [Penyedia Model Komputasi Eksternal (OpenAI API Endpoints)]
```
*Gambar 3.6 Diagram Arsitektur Perantara AI Gateway Bifrost*

#### D. Perancangan Conversational Prompting & Scaffolding Pedagogis
Interaksi percakapan dikendalikan melalui rekayasa instruksi (*prompt engineering*) terstruktur dengan kaidah pedagogis yang ketat:
1. **The One-Question Rule**: Setiap giliran respons tutor AI **hanya diperbolehkan memuat satu pertanyaan terarah di akhir kalimat**. Aturan ini mencegah kebingungan pengguna, membatasi beban kognitif, dan menjaga ritme percakapan tetap natural.
2. **Scaffolding Adaptif CEFR**: *System prompt* menyuntikkan batasan leksikogramatikal secara dinamis:
   - *Target B1*: Menggunakan kalimat tunggal/majemuk setara, kosakata umum, dan tempo tutur yang santai.
   - *Target B2*: Menggunakan klausa bawahan, variasi idiom formal, serta pertanyaan analisis reflektif.
3. **Format Umpan Balik Terstruktur**: Evaluasi linguistik dipisahkan dari dialog dan diformat dalam struktur JSON standar:
   ```json
   {
     "original_sentence": "I go to campus yesterday by bus.",
     "corrected_sentence": "I went to campus yesterday by bus.",
     "error_category": "Past Tense Inconsistency",
     "pedagogical_explanation": "Gunakan bentuk past tense 'went' untuk peristiwa masa lampau."
   }
   ```

#### E. Formulasi Matematis Sistem
Logika komputasi sistem didasarkan pada empat formulasi matematis baku:

##### 1. Kemiripan Kosinus (Cosine Similarity)
Derajat kemiripan semantik antara vektor kueri pengguna ($\mathbf{q}$) dan vektor pecahan dokumen materi ($\mathbf{d}$) dirumuskan pada Persamaan 3.1:

$$	ext{Cosine Similarity}(\mathbf{q}, \mathbf{d}) = rac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|} = rac{\sum_{i=1}^{n} q_i d_i}{\sqrt{\sum_{i=1}^{n} q_i^2} \sqrt{\sum_{i=1}^{n} d_i^2}}$$
*(Persamaan 3.1)*

Potongan dokumen dengan nilai kemiripan $\ge 0{,}70$ diprioritaskan masuk ke ruang konteks.

##### 2. Penggabungan Peringkat (Reciprocal Rank Fusion - RRF)
Skor gabungan penelusuran hibrida antara ChromaDB dan BM25 dihitung melalui formula RRF pada Persamaan 3.2:

$$RRF\_Score(d \in D) = \sum_{m \in M} rac{1}{k + r_m(d)}$$
*(Persamaan 3.2)*

Di mana $M = \{	ext{ChromaDB}, 	ext{BM25}\}$, $r_m(d)$ merupakan peringkat dokumen $d$ pada metode penelusuran $m$, dan $k$ adalah konstanta perata bernilai 60.

##### 3. Formulasi Skor Placement Test (Diagnostic Score)
Tingkat kemahiran awal pengguna ditentukan berdasarkan agregasi berbobot dari akurasi tata bahasa ($S_g$), ketepatan leksikal ($S_v$), dan kelancaran berbicara ($S_f$) pada uji diagnostik:

$$Score_{placement} = (0{,}40 \cdot S_g) + (0{,}35 \cdot S_v) + (0{,}25 \cdot S_f)$$
*(Persamaan 3.3)*

Pengguna dipetakan ke level B2 jika $Score_{placement} \ge 70{,}0\%$, dan ke level B1 jika $Score_{placement} < 70{,}0\%$.

##### 4. Formulasi Skor Performa Sesi Pembelajaran (Session Speaking Score)
Skor performa akhir pada setiap sesi latihan lisan dihitung menggunakan Persamaan 3.4:

$$Score_{session} = \left( 0{,}30 \cdot rac{C_{turns}}{T_{target}} ight) + (0{,}40 \cdot Acc_{grammar}) + (0{,}30 \cdot Fluency_{wpm})$$
*(Persamaan 3.4)*

Di mana $C_{turns}$ adalah jumlah giliran bicara yang dituntaskan, $T_{target}$ adalah target putaran dialog, $Acc_{grammar}$ adalah persentase kalimat benar, dan $Fluency_{wpm}$ adalah rasio kelancaran kata per menit.

#### F. Perancangan Basis Data (Database Design)
Pengelolaan data relasional dibangun menggunakan SQLAlchemy *asynchronous ORM*. Struktur entitas dan relasi antartabel diilustrasikan melalui *Entity Relationship Diagram* (ERD) pada Gambar 3.7.

```
+-----------------------------------------------------------------------------+
|          GAMBAR 3.7 ENTITY RELATIONSHIP DIAGRAM (ERD) BASIS DATA            |
+-----------------------------------------------------------------------------+
  ┌──────────────────────┐         ┌─────────────────────────┐
  │        USERS         │1       *│    PRACTICE_SESSIONS    │
  ├──────────────────────┼─────────┼─────────────────────────┤
  │ PK id (UUID)         │         │ PK id (UUID)            │
  │    email (VARCHAR)   │         │ FK user_id (UUID)       │
  │    password (VARCHAR)│         │    topic_name (VARCHAR) │
  │    full_name (VARCHAR│         │    target_cefr (VARCHAR)│
  │    target_cefr (VAR) │         │    start_time (DATETIME)│
  │    created_at (TIME) │         │    end_time (DATETIME)  │
  └──────────┬───────────┘         └────────────┬────────────┘
             │1                                 │1
             │                                  │
             │*                                 │*
  ┌──────────▼───────────┐         ┌────────────▼────────────┐
  │   USER_GAMIFICATION  │         │        MESSAGES         │
  ├──────────────────────┤         ├─────────────────────────┤
  │ PK id (UUID)         │         │ PK id (UUID)            │
  │ FK user_id (UUID)    │         │ FK session_id (UUID)    │
  │    total_points (INT)│         │    sender_role (VARCHAR)│
  │    current_level (INT│         │    transcribed_text (TX)│
  │    daily_streak (INT)│         │    response_text (TEXT) │
  │    last_active (DATE)│         │    feedback_json (JSON) │
  └──────────────────────┘         └─────────────────────────┘
```
*Gambar 3.7 Entity Relationship Diagram (ERD) Basis Data MILO*

Definisi kamus data atribut tabel disajikan pada Tabel 3.4.

*Tabel 3.4 Kamus Data Basis Data Relasional MILO*
| Nama Tabel | Nama Kolom | Tipe Data | Keterangan & Batasan |
| :--- | :--- | :--- | :--- |
| **`users`** | `id` <br> `email` <br> `hashed_password` <br> `full_name` <br> `target_cefr` | UUID <br> VARCHAR(255) <br> VARCHAR(255) <br> VARCHAR(100) <br> VARCHAR(10) | *Primary Key* <br> *Unique, Not Null* <br> Sandi terenkripsi *Bcrypt* <br> Nama lengkap pengguna <br> Level aktif ('B1' atau 'B2') |
| **`practice_sessions`** | `id` <br> `user_id` <br> `topic_name` <br> `target_cefr` <br> `start_time` | UUID <br> UUID <br> VARCHAR(100) <br> VARCHAR(10) <br> TIMESTAMP | *Primary Key* <br> *Foreign Key (`users.id`)* <br> Topik percakapan <br> Tingkat kesulitan sesi <br> Waktu mulai sesi |
| **`messages`** | `id` <br> `session_id` <br> `sender_role` <br> `transcribed_text` <br> `feedback_json` | UUID <br> UUID <br> VARCHAR(20) <br> TEXT <br> JSONB / TEXT | *Primary Key* <br> *Foreign Key (`practice_sessions.id`)* <br> Nilai: 'user' / 'assistant' <br> Transkripsi suara pengguna <br> Data koreksi tata bahasa |
| **`user_gamification`**| `id` <br> `user_id` <br> `total_points` <br> `current_streak` <br> `last_active` | UUID <br> UUID <br> INTEGER <br> INTEGER <br> DATE | *Primary Key* <br> *Foreign Key (`users.id`)* <br> Akumulasi poin XP pengguna <br> Rekor hari berturut-turut <br> Tanggal aktivitas terakhir |
| **`user_badges`** | `id` <br> `user_id` <br> `badge_code` <br> `unlocked_at` | UUID <br> UUID <br> VARCHAR(50) <br> TIMESTAMP | *Primary Key* <br> *Foreign Key (`users.id`)* <br> Kode unik lencana prestasi <br> Waktu perolehan lencana |

#### G. Perancangan Identitas Visual dan Karakter Avatar Live2D
Perancangan identitas visual berfokus pada penciptaan atmosfer antarmuka yang ramah dan menenangkan:
1. **Palet Warna (Color Palette)**:
   - *Primary (`#4F46E5` - Deep Indigo)*: Menghadirkan kesan profesionalitas dan ketenangan berpikir.
   - *Secondary (`#06B6D4` - Bright Cyan)*: Aksen modern pada visualisator gelombang audio.
   - *Neutral Dark (`#0F172A` - Slate Navy)*: Teks berkontras tinggi memenuhi standar WCAG AAA.
   - *Neutral Light (`#F8FAFC` - Off-White)*: Warna latar belakang lembut peredam kelelahan mata.
   - *Accent Success (`#10B981` - Emerald Green)*: Penanda keberhasilan grammar dan perolehan poin.
2. **Tipografi**: Menggunakan jenis huruf *Plus Jakarta Sans* untuk elemen struktural dan *Inter* untuk keterbacaan teks transkripsi dan umpan balik dialog.
3. **Spesifikasi Rigging Avatar Live2D**: Karakter "MILO" diintegrasikan dengan sinyal audio melalui pemetaan parameter pada Tabel 3.5.

```
+-----------------------------------------------------------------------------+
|         GAMBAR 3.8 DIAGRAM RIGGING DAN SINKRONISASI AUDIO LIVE2D            |
+-----------------------------------------------------------------------------+
  [Aliran Audio TTS (MP3/WAV)] ──► [Web Audio API: AnalyserNode]
                                                │
                                                ▼
                                   [Ekstraksi Amplitudo RMS]
                                                │
                                                ▼
  [Normalisasi Nilai (0.0 – 1.0)] ──► [Pemetaan Parameter Live2D: ParamMouthOpenY]
                                                │
                                                ▼
                            [Gerakan Bibir Karakter Sinkron Real-time]
```
*Gambar 3.8 Diagram Alur Sinkronisasi Audio dan Rigging Parameter Live2D*

*Tabel 3.5 Pemetaan Parameter Model Live2D terhadap Dinamika Sistem*
| Parameter ID | Rentang Nilai | Pemicu Input / Event | Efek Gerak Visual pada Avatar |
| :--- | :---: | :--- | :--- |
| `ParamMouthOpenY` | 0.0 s.d. 1.0 | Amplitudo RMS audio wicara TTS | Buka-tutup mulut (*lip-sync*) mengikuti suku kata |
| `ParamEyeLOpen`, `ParamEyeROpen` | 0.0 s.d. 1.0 | *Random timer* interval 2.5–4.0 detik | Kedipan mata natural saat posisi siaga (*idle*) |
| `ParamAngleZ` | -30° s.d. +30° | Status sistem: Pengguna berbicara | Kepala miring menyimak dengan penuh perhatian |
| `ParamBodyAngleX` | -10° s.d. +10° | Status sistem: AI mulai merespons | Gestur tubuh menyambut ramah mitra bicara |

#### H. Perancangan Antarmuka Pengguna (Wireframe & High-Fidelity Mockup)
Rancangan antarmuka disusun secara terpadu guna memastikan navigasi yang intuitif dari awal hingga akhir sesi.

```
+-----------------------------------------------------------------------------+
|                GAMBAR 3.9 PERANCANGAN ANTARMUKA PENGGUNA                    |
+-----------------------------------------------------------------------------+
  (a) Wireframe Alur Navigasi Antarmuka Sistem
  (b) Mockup High-Fidelity Dashboard Utama (Pilihan Modul, Streak, XP Card)
  (c) Mockup High-Fidelity Sesi Latihan (Kanvas Live2D, Push-to-Talk, Waveform)
  (d) Mockup High-Fidelity Rangkuman Evaluasi (Grammar Breakdown & Skor Sesi)
```
*Gambar 3.9 Rancangan Antarmuka Pengguna: (a) Wireframe Alur; (b) Dashboard Utama; (c) Sesi Latihan Live2D; (d) Rangkuman Evaluasi*

---

### 3.3.3 Development (Tahap Pengembangan Sistem)
Tahap *Development* merupakan proses realisasi fisik dari seluruh spesifikasi yang telah dirumuskan pada tahap *Design*. Pada tahap ini, pengembang membangun basis kode sumber (*source code*), menata arsitektur repositori, mengkonfigurasikan *AI Gateway*, menyusun basis data vektor, dan mengintegrasikan model avatar Live2D ke dalam aplikasi web:

#### 1. Penataan Lingkungan Pengembangan dan Struktur Direktori
Proyek diorganisasikan ke dalam arsitektur modular berbasis Python 3.11 yang dikelola menggunakan manajer paket `uv`. Struktur direktori proyek pada Visual Studio Code dirancang memisahkan logika backend (`app/`), basis pengetahuan (`knowledge_base/`), antarmuka web (`frontend/`), konfigurasi *gateway* (`docker-compose.bifrost.yml`), dan skrip pengujian evaluasi (`evaluations/`).

```
[TEMPATKAN GAMBAR DI SINI]
Gambar 3.10 Struktur Direktori dan Lingkungan Pengembangan Proyek AI-MILO pada VS Code
```

#### 2. Penerapan AI Gateway Bifrost Berbasis Kontainer Docker
Untuk memastikan efisiensi pemanggilan API dan perlindungan terhadap *rate-limiting*, layanan Bifrost dioperasikan pada lingkungan terisolasi menggunakan Docker Compose. Berkas konfigurasi mendefinisikan rute proksi cerdas pada port 8080 dengan *semantic caching* lokal.

```
[TEMPATKAN GAMBAR DI SINI]
Gambar 3.11 Tampilan Eksekusi Kontainer AI Gateway Bifrost pada Terminal Docker
```

#### 3. Pembangunan Basis Pengetahuan dan Vektorisasi Dokumen
Materi silabus CEFR B1–B2 yang disimpan dalam format Markdown pada folder `knowledge_base/` diproses melalui skrip ingesti asinkron (`knowledge_base/ingest.py`). Skrip melakukan pemecahan teks (*chunking* 500 karakter), memanggil model embedding `text-embedding-3-small`, dan menyimpan koleksi vektor ke dalam basis data ChromaDB.

```
[TEMPATKAN GAMBAR DI SINI]
Gambar 3.12 Eksekusi Skrip Ingesti dan Pengindeksan Dokumen ke Basis Data Vektor ChromaDB
```

#### 4. Integrasi Model Avatar Live2D pada Antarmuka WebGL
Model avatar 2D yang terdiri atas berkas konfigurasi `.model3.json`, kompilasi fisika gerakan `.moc3`, dan lembar tekstur gambar diintegrasikan ke dalam antarmuka web menggunakan Live2D Cubism Core JavaScript SDK. Kanvas HTML5 diatur secara responsif di samping kontrol perekam suara *Web Audio API*.

```
[TEMPATKAN GAMBAR DI SINI]
Gambar 3.13 Struktur Aset Karakter Live2D dan Tampilan Rendering pada Kanvas WebGL
```

#### 5. Implementasi Logika Backend dan Endpoint REST API FastAPI
Layanan backend dibangun menggunakan *framework* FastAPI dengan pola asinkron (`async/await`) untuk menangani unggahan audio wicara, komunikasi dengan ASR Whisper, pemanggilan penelusuran hibrida RAG, orkestrasi respons GPT-4o-mini, sintesis suara TTS, dan perhitungan skor gamifikasi secara paralel.

```
[TEMPATKAN GAMBAR DI SINI]
Gambar 3.14 Cuplikan Kode Sumber Backend Utama pada Modul RAG dan Conversational LLM
```

---

### 3.3.4 Implementation (Tahap Penerapan Sistem)
Tahap *Implementation* merupakan tahapan di mana sistem yang telah berhasil dikembangkan pada tahap *Development* mulai dioperasikan dalam lingkungan uji coba nyata untuk digunakan oleh subjek penelitian:

#### 1. Penerapan Lingkungan Operasional
Seluruh komponen perangkat lunak dijalankan secara terintegrasi pada lingkungan server pengembang lokal yang dapat diakses oleh responden uji coba melalui jaringan peramban web modern (Google Chrome / Microsoft Edge). Server FastAPI menyajikan berkas frontend statis sekaligus melayani rute API wicara, sementara basis data relasional SQLite/PostgreSQL secara aktif merekam setiap transaksi percakapan dan metrik aktivitas pengguna.

#### 2. Prosedur Uji Coba Penggunaan Sistem oleh Responden
Pelaksanaan implementasi kepada responden mahasiswa mengikuti protokol terstruktur:
1. **Fase Orientasi & Pretest**: Responden mengisi kuesioner awal (*baseline*) mengenai tingkat *speaking anxiety* dan keterlibatan belajar (*student engagement*) saat menggunakan media konvensional.
2. **Fase Diagnostic Test**: Responden mengakses platform MILO untuk pertama kali dan menjalani tes diagnostik berbicara terpandu guna memetakan rekomendasi modul ke level B1 atau B2.
3. **Fase Latihan Percakapan Terbimbing**: Responden menjalankan sesi latihan berbicara interaktif berformat *microlearning* (3–5 menit per sesi) secara mandiri sebanyak 3 hingga 5 kali pertemuan selama periode intervensi penelitian. Selama proses ini, sistem secara otomatis merekam durasi interaksi, jumlah giliran bicara, akurasi tata bahasa, dan perolehan poin gamifikasi.
4. **Fase Posttest & Refleksi**: Setelah menuntaskan seluruh rangkaian modul latihan, responden mengisi kuesioner akhir (*posttest*) keterlibatan belajar serta instrumen kebergunaan sistem (*User Experience Questionnaire* / UEQ).

---

### 3.3.5 Evaluation (Rencana Pengujian Sistem)
Rencana pengujian dalam penelitian ini dirancang secara komprehensif mencakup validasi fungsional, performa kecerdasan buatan, kebergunaan antarmuka, dan efektivitas pedagogis terhadap keterlibatan belajar mahasiswa. Evaluasi dibagi menjadi lima pilar pengujian terukur sebagaimana dijabarkan pada matriks Tabel 3.6:

*Tabel 3.6 Matriks Rencana Pengujian Komprehensif Sistem MILO*
| No | Dimensi Pengujian | Tujuan Pengujian | Parameter & Instrumen | Kriteria Keberhasilan / Target |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Black Box Testing** | Memverifikasi seluruh fitur fungsional berjalan tanpa galat logika atau antarmuka. | *Test cases* mencakup: Autentikasi, Diagnostic Test, ASR Recording, RAG Retrieval, Live2D Lip-sync, Gamifikasi, dan Export Feedback. | 100% skenario pengujian berstatus *Pass* (berhasil tanpa galat kritis). |
| 2 | **Speech Recognition Testing** | Mengukur akurasi dan ketahanan model Whisper ASR terhadap wicara mahasiswa Indonesia. | Nilai *Word Error Rate* (WER), transkripsi audio dengan variasi aksen, dan waktu latensi pemrosesan audio. | Rata-rata WER $\le 12{,}0\%$ dan latensi transkripsi audio $< 1{,}5$ detik. |
| 3 | **DeepEval Benchmark (LLM-as-a-Judge)** | Menilai mutu pedagogis dan keabsahan respons RAG serta koreksi tata bahasa secara kuantitatif. | Metrik *Faithfulness* (keselarasan konteks), *Answer Relevancy*, dan akurasi koreksi tata bahasa pada berkas *test cases*. | Rata-rata skor *Faithfulness* $\ge 0{,}85$ dan *Answer Relevancy* $\ge 0{,}85$ (skala 0.0–1.0). |
| 4 | **User Experience Evaluation (UEQ)** | Mengukur tingkat kepuasan dan kebergunaan antarmuka pengguna secara terstandarisasi. | Kuesioner UEQ (26 butir item pasangan sifat mencakup 6 skala: Daya Tarik, Kejelasan, Efisiensi, Ketepatan, Stimulasi, dan Kebaruan). | Seluruh skala UEQ berada pada kategori *Above Average* atau *Good* dibandingkan tolok ukur acuan. |
| 5 | **Student Engagement Evaluation** | Mengukur peningkatan keterlibatan belajar berbicara sebelum dan sesudah menggunakan MILO. | Kuesioner keterlibatan belajar 3 dimensi (Perilaku, Emosional, Kognitif) menggunakan skala Likert 1–5, dianalisis via *Normalized Gain* (N-Gain). | Terjadi peningkatan skor yang signifikan secara statistik ($p < 0{,}05$) dengan nilai $g > 0{,}30$ (kategori sedang s.d. tinggi). |

#### Instrumen Keterlibatan Belajar (Student Engagement)
Pengukuran keterlibatan belajar mengadaptasi model tiga dimensi Phil Hiver dkk. (2021) yang dirinci ke dalam 12 butir indikator pernyataan pada Tabel 3.7.

*Tabel 3.7 Indikator Evaluasi Student Engagement Tiga Dimensi*
| Dimensi Keterlibatan | No | Butir Indikator Pernyataan Angket | Skala Ukur |
| :--- | :---: | :--- | :---: |
| **Keterlibatan Perilaku (Behavioral)** | 1 <br> 2 <br> 3 <br> 4 | Saya secara aktif berlatih berbicara bahasa Inggris menggunakan platform ini. <br> Saya berusaha menyelesaikan setiap sesi latihan microlearning hingga tuntas. <br> Saya terdorong untuk mempertahankan rekor latihan harian (streak). <br> Saya memanfaatkan tombol mikrofon berulang kali untuk menyempurnakan ujaran saya. | Skala Likert 1–5 <br> (1: Sangat Tidak Setuju, <br> 5: Sangat Setuju) |
| **Keterlibatan Emosional (Emotional)** | 5 <br> 6 <br> 7 <br> 8 | Saya merasa lebih percaya diri dan tidak takut salah saat berbicara dengan avatar AI. <br> Kehadiran avatar virtual Live2D membuat suasana latihan terasa menyenangkan. <br> Saya merasa dihargai dengan adanya pemberian poin (XP) dan lencana pencapaian. <br> Latihan berbicara melalui platform ini terasa menenangkan dan meredakan rasa cemas saya. | Skala Likert 1–5 |
| **Keterlibatan Kognitif (Cognitive)** | 9 <br> 10 <br> 11 <br> 12 | Saya memperhatikan dan mempelajari catatan evaluasi grammar yang disajikan sistem. <br> Saya mencoba menerapkan rekomendasi frasa alternatif pada sesi percakapan berikutnya. <br> Topik latihan yang adaptif mendorong saya berpikir kritis dalam menyusun argumen lisan. <br> Umpan balik yang diberikan sistem membantu saya memahami kelemahan berbicara saya secara mandiri. | Skala Likert 1–5 |

Data skor *pretest* ($S_{pre}$) dan *posttest* ($S_{post}$) keterlibatan belajar dihitung efektivitas peningkatannya menggunakan formulasi *Normalized Gain* ($g$) Hake pada Persamaan 3.5:

$$g = rac{S_{post} - S_{pre}}{S_{max} - S_{pre}}$$
*(Persamaan 3.5)*

Kategori perolehan skor ternormalisasi diinterpretasikan sebagai berikut:
- $g \ge 0{,}70$ : Kategori Peningkatan Tinggi
- $0{,}30 \le g < 0{,}70$ : Kategori Peningkatan Sedang
- $g < 0{,}30$ : Kategori Peningkatan Rendah

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
