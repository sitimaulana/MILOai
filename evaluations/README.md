# Modul Evaluasi Kuantitatif AI-MILO (DeepEval Benchmark)

Modul ini menyediakan rangkaian pengujian ilmiah kuantitatif berbasis **LLM-as-a-Judge** menggunakan **DeepEval** untuk mengukur performa sistem AI-MILO. Hasil pengujian ini dirancang khusus untuk menghasilkan data metrik, tabel statistik, dan visualisasi untuk **Bab 4 (Hasil dan Pembahasan) Laporan Proyek Akhir (PA) / Skripsi**.

---

## 1. Komponen & Metrik yang Diuji

| Modul MILO | Metrik Evaluasi | Rentang Skor | Definisi & Tujuan Akademik |
| :--- | :--- | :---: | :--- |
| **RAG** (ChromaDB + Obsidian) | **Faithfulness** | `0.0 – 1.0` | Mengukur kepatuhan respons terhadap materi di Obsidian Vault (mendeteksi halusinasi materi grammar/vocab). |
| **RAG** | **Answer Relevancy** | `0.0 – 1.0` | Mengukur seberapa tepat respons tutor menjawab input atau kebutuhan speaking learner. |
| **RAG Retrieval** | **Contextual Precision** | `0.0 – 1.0` | Mengukur apakah chunk ChromaDB yang diambil berada pada peringkat relevansi tertinggi. |
| **Language Feedback** | **Correction Accuracy** | `0.0 – 1.0` | Mengukur ketepatan deteksi kesalahan gramatikal dan kebenaran koreksi yang disarankan (*G-Eval*). |
| **Language Feedback** | **False Positive Resistance** | `0.0 – 1.0` | Mengukur ketahanan mesin feedback agar tidak menghukum/mengada-ada kesalahan pada kalimat yang sudah benar. |
| **Language Feedback** | **Pedagogical Tone** | `0.0 – 1.0` | Mengukur keramahan, sifat suportif, dan kejelasan tip pembelajaran untuk learner CEFR. |
| **Speaking Tutor** | **CEFR Adaptation** | `0.0 – 1.0` | Menguji apakah gaya bahasa dan panjang kalimat berhasil beradaptasi dengan level pengguna (A1/A2/B1/B2). |
| **Speaking Tutor** | **One Question Rule** | `0.0 – 1.0` | Memverifikasi apakah MILO selalu mengakhiri respons dengan tepat 1 pertanyaan pemantik untuk menjaga alur dialog. |

*Standar ambang batas kelulusan (passing threshold) yang digunakan adalah **0.70** (70%).*

---

## 2. Struktur Direktori

```text
evaluations/
├── datasets/
│   ├── rag_benchmarks.json        # Dataset uji ground-truth untuk RAG
│   ├── feedback_benchmarks.json   # Dataset uji kalimat benar & salah untuk Feedback
│   └── tutor_benchmarks.json      # Dataset skenario multi-level CEFR untuk Tutor
├── results/
│   ├── summary_metrics.csv        # Tabel ringkasan rata-rata skor, std dev, min, max, pass rate
│   ├── evaluation_details.json    # Log detail setiap test case beserta alasan penilaian
│   └── REPORT_BAB4_PA.md          # Laporan terformat rapi siap salin ke Bab 4 Skripsi/PA
├── model_loader.py                # Konfigurasi LLM-as-a-Judge (OpenRouter/Bifrost/OpenAI/Ollama)
├── eval_rag.py                    # Evaluator modul RAG
├── eval_feedback.py               # Evaluator modul Language Feedback
├── eval_tutor.py                  # Evaluator modul Speaking Tutor
├── test_deepeval_pytest.py        # Pengujian assertions via Pytest
└── run_evaluation.py              # Script utama eksekusi benchmark & generator laporan
```

---

## 3. Cara Menjalankan Evaluasi

### A. Menjalankan Semua Pengujian Benchmark
Perintah ini akan menjalankan evaluasi pada seluruh modul dan otomatis menghasilkan file laporan di folder `evaluations/results/`:
```bash
uv run python -m evaluations.run_evaluation
```

### B. Menjalankan Modul Tertentu Saja
Jika Anda hanya ingin menguji satu komponen:
```bash
# Uji RAG saja
uv run python -m evaluations.run_evaluation --suite rag

# Uji Feedback saja
uv run python -m evaluations.run_evaluation --suite feedback

# Uji Tutor saja
uv run python -m evaluations.run_evaluation --suite tutor
```

### C. Menjalankan Live Pipeline (End-to-End)
Untuk menguji query secara langsung terhadap ChromaDB lokal dan model LLM aktif:
```bash
uv run python -m evaluations.run_evaluation --suite rag --live
```

### D. Uji Coba Cepat (Sample Terbatas)
Untuk menguji 1 atau 2 sampel saja tanpa menunggu lama:
```bash
uv run python -m evaluations.run_evaluation --max-samples 2
```

### E. Menjalankan via Pytest
```bash
uv run pytest evaluations/test_deepeval_pytest.py -v
```

---

## 4. Konfigurasi Model Penilai (LLM-as-a-Judge)

Secara default, DeepEval akan menggunakan provider LLM yang sedang aktif di file `.env` Anda:
- Jika `AI_PROVIDER=openrouter`, menggunakan `OPENROUTER_MODEL` & `OPENROUTER_API_KEY`.
- Jika `AI_PROVIDER=bifrost`, menggunakan endpoint Bifrost (`http://localhost:8080/v1`).
- Jika `AI_PROVIDER=openai`, menggunakan model OpenAI.
- Jika `AI_PROVIDER=local`, menggunakan Ollama lokal.

Anda juga bisa menentukan model penilai secara eksplisit melalui environment variables:
```bash
# Contoh menggunakan model tertentu sebagai judge
$env:EVAL_MODEL="openai/gpt-4o-mini"
uv run python -m evaluations.run_evaluation
```

---

## 5. Penggunaan Hasil untuk Bab 4 Skripsi / PA

Setelah eksekusi selesai, Anda akan mendapatkan:
1. **`evaluations/results/summary_metrics.csv`**: Bisa langsung diimpor ke Excel, SPSS, atau dikonversi menjadi tabel LaTeX.
2. **`evaluations/results/REPORT_BAB4_PA.md`**: Berisi tabel ringkasan metrik lengkap beserta interpretasi akademiknya yang siap disalin ke naskah Bab 4 Anda.

