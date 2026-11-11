# Laporan Pengujian Kuantitatif AI-MILO (DeepEval Benchmark)
**Waktu Pengujian**: 2026-11-08 01:30:56  
**Kerangka Kerja Evaluasi**: DeepEval (LLM-as-a-Judge)  
**Threshold Kelulusan (Pass Rate)**: Skor >= 0.70 (Skala 0.0 - 1.0)  

---

## 1. Ringkasan Metrik Pengujian (Tabel untuk Bab 4)

| Modul | Metrik Evaluasi | Jumlah Sampel | Rata-Rata Skor | Standar Deviasi | Nilai Min | Nilai Max | Pass Rate (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| RAG | Faithfulness | 1 | 1.0 | 0.0 | 1.0 | 1.0 | 100.0% |
| RAG | Answer Relevancy | 1 | 1.0 | 0.0 | 1.0 | 1.0 | 100.0% |

---

## 2. Interpretasi Hasil Evaluasi untuk Skripsi / PA

### A. Modul RAG (Retrieval-Augmented Generation)
- **Faithfulness**: Mengukur tingkat kepatuhan respons MILO terhadap konteks materi di Obsidian Vault. Skor mendekati 1.0 membuktikan bahwa model tidak mengalami halusinasi dan konsisten menggunakan materi pembelajaran.
- **Answer Relevancy**: Mengukur seberapa tepat respons menjawab pertanyaan atau kebutuhan speaking learner tanpa melenceng dari konteks percakapan.

### B. Modul Language Feedback (CEFR Engine)
- **Correction Accuracy**: Menunjukkan keakuratan deteksi kesalahan gramatikal dan ketepatan koreksi yang disarankan.
- **False Positive Resistance**: Menunjukkan keandalan sistem dalam tidak menghukum atau membetulkan kalimat yang sebenarnya sudah benar dan natural.
- **Pedagogical Tone**: Mengukur keramahan, kejelasan tip, dan sifat suportif dalam gaya pengajaran MILO.

### C. Modul Tutor Speaking Companion
- **CEFR Adaptation**: Menunjukkan bahwa kompleksitas kalimat dan kosakata yang dihasilkan berhasil beradaptasi dengan level pengguna (A1/A2/B1/B2).
- **One Question Rule**: Menunjukkan konsistensi MILO dalam menjaga alur percakapan dua arah dengan selalu mengakhiri respons menggunakan satu pertanyaan pemantik.

---
*File laporan ini digenerate secara otomatis oleh modul `evaluations.run_evaluation`.*