---
title: MILO CEFR Knowledge Base - Map of Content (MOC)
tags:
  - moc
  - milo/knowledge-base
  - cefr
created: 2026-10-27
author: MILO Development Team
---

# 🧠 MILO AI — CEFR Knowledge Base (Obsidian Vault)

Selamat datang di **Vault Pengetahuan CEFR MILO**. Vault ini menyimpan seluruh materi panduan pedagogis, tata bahasa (*grammar*), kosakata (*vocabulary*), strategi berbicara (*speaking strategies*), dan rubrik penilaian CEFR (B1–B2) yang digunakan oleh modul **RAG (Retrieval-Augmented Generation)** pada backend AI-MILO.

> [!TIP]
> Buka **Graph View** (`Ctrl + G`) di Obsidian untuk melihat visualisasi jaringan relasi antarkonsep materi belajar secara interaktif.

---

## 🗺️ Peta Materi (Map of Content)

### 1. 🎯 Kerangka & Standar CEFR
- [[01_cefr/cefr_descriptors|Deskriptor Kemampuan Berbicara CEFR]]
- [[01_cefr/cefr_b1_b2_distinction|Perbedaan Karakteristik B1 vs B2]]
- Tag: `#cefr/overview` `#cefr/b1` `#cefr/b2`

### 2. 📝 Modul Tata Bahasa (Grammar)
Materi aturan tata bahasa yang diacu oleh LLM untuk mengoreksi kalimat pengguna:
- **Tingkat B1**:
  - [[02_grammar/B1/present_perfect|Present Perfect]]
  - [[02_grammar/B1/present_perfect_vs_past|Present Perfect vs Past Simple]]
  - [[02_grammar/B1/first_conditional|First Conditional]]
  - [[02_grammar/B1/second_conditional|Second Conditional]]
  - [[02_grammar/B1/modals|Modals of Ability & Obligation]]
  - [[02_grammar/B1/passive|Passive Voice Basics]]
  - [[02_grammar/B1/relative_clauses|Defining Relative Clauses]]
  - [[02_grammar/B1/reported_speech|Reported Speech Basics]]
  - [[02_grammar/B1/used_to|Used to & Habits]]
- **Tingkat B2**:
  - [[02_grammar/B2/third_conditional|Third Conditional & Mixed Conditionals]]
  - [[02_grammar/B2/inversion|Negative Inversion for Emphasis]]
  - [[02_grammar/B2/future_perfect_continuous|Future Perfect & Continuous]]
  - [[02_grammar/B2/participle_clauses|Participle Clauses]]
  - [[02_grammar/B2/cleft_sentences|Cleft Sentences]]
- Tag: `#skill/grammar` `#level/b1` `#level/b2`

### 3. 📚 Kosakata & Peningkatan Kata (Vocabulary)
Pedoman rekomendasi kata untuk *upgrading* kosakata siswa:
- [[03_vocabulary/B1/daily_routine|Kosakata Rutinitas Sehari-hari (B1)]]
- [[03_vocabulary/B1/work_study|Dunia Kerja & Akademik Dasar (B1)]]
- [[03_vocabulary/B2/collocations_idioms|Natural Collocations & Phrasal Idioms (B2)]]
- [[03_vocabulary/B2/academic_discourse|Kosakata Diskusi Akademis & Analitis (B2)]]
- Tag: `#skill/vocabulary` `#upgrade/b1-to-b2`

### 4. 🗣️ Strategi Berbicara & Kelancaran (Speaking Fluency)
Panduan bagi tutor AI untuk memancing elaborasi dan percakapan dua arah:
- [[04_speaking/discourse_markers|Discourse Markers & Connectors]]
- [[04_speaking/turn_taking|Teknik Turn-Taking & Clarification Asking]]
- [[04_speaking/hesitation_strategies|Strategi Menghindari Jeda Lama (Fillers)]]
- Tag: `#skill/fluency` `#pedagogy/speaking`

### 5. 🎙️ Skenario Percakapan (Practice Scenarios)
Topik latihan yang disimulasikan oleh MILO:
- [[07_scenarios/job_interview|Simulasi Wawancara Kerja (Job Interview)]]
- [[07_scenarios/academic_discussion|Diskusi Akademis & Isu Kontemporer]]
- [[07_scenarios/daily_conversation|Percakapan Kehidupan Sehari-hari]]
- Tag: `#scenario/interview` `#scenario/academic` `#scenario/daily`

### 6. 📊 Penilaian & Rubrik (Assessment & Feedback)
Kriteria scoring kuantitatif yang diterapkan pada modul evaluasi:
- [[06_feedback/implicit_recast|Metode Implicit Recast (Koreksi Lembut)]]
- [[09_assessment/scoring_rubric|Rubrik Skor Grammar, Vocabulary, & Fluency (0-100)]]
- Tag: `#assessment/scoring` `#feedback/pedagogy`

---

## ⚡ Sinkronisasi ke RAG Backend
Setiap kali Anda menambah atau mengedit catatan markdown di Obsidian Vault ini, perbarui database vektor ChromaDB dengan menjalankan perintah:

```bash
# Otomatis mengindeks seluruh isi Obsidian Vault
python knowledge_base/ingest.py --reset
```
