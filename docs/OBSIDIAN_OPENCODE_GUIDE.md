# Panduan Integrasi Obsidian & OpenCode di AI-MILO 📚💻

Dokumen ini menjelaskan bagaimana **Obsidian** dan **OpenCode** diintegrasikan ke dalam ekosistem **AI-MILO**.

---

## 1. Integrasi Obsidian (CEFR Knowledge Base & Learning Journal)

### A. Membuka Vault di Obsidian
Folder [`Knowledge Base MILO/`](file:///d:/Kuliah/PA/AI-MILO/Knowledge%20Base%20MILO) telah dikonfigurasi sebagai **Obsidian Vault** resmi dengan pengaturan visual dan penandaan internal.

1. Buka aplikasi **Obsidian** di laptop Anda.
2. Klik **Open folder as vault**.
3. Pilih folder: `d:\Kuliah\PA\AI-MILO\Knowledge Base MILO`.
4. Buka file utama: [`00_Home_MOC.md`](file:///d:/Kuliah/PA/AI-MILO/Knowledge%20Base%20MILO/00_Home_MOC.md) *(Map of Content)*.
5. Tekan `Ctrl + G` untuk membuka **Interactive Graph View** dan melihat visualisasi graf interkoneksi antartopik grammar, vocabulary, dan rubrik CEFR.

### B. Sinkronisasi Otomatis ke ChromaDB RAG
Script [knowledge_base/ingest.py](file:///d:/Kuliah/PA/AI-MILO/knowledge_base/ingest.py) telah dikonfigurasi untuk:
- Otomatis mendeteksi folder `Knowledge Base MILO` sebagai default.
- Mengabaikan folder internal Obsidian (`.obsidian/`).
- Membaca semua format Markdown (`.md`), teks, dan dokumen referensi.

Untuk menyinkronkan materi baru dari Obsidian ke database vektor:
```bash
uv run python knowledge_base/ingest.py --reset
```

### C. Ekspor Catatan Latihan Sesi Mahasiswa ke Obsidian
Setiap sesi latihan berbicara yang dilakukan di AI-MILO dapat diekspor langsung dalam format Obsidian Markdown (lengkap dengan YAML frontmatter, alert callouts, tabel penilaian, daftar koreksi grammar, dan riwayat percakapan):

- **Endpoint API**:
  ```http
  GET /api/v1/session/{session_id}/export/obsidian
  ```
- File yang diunduh (`milo_session_<id>.md`) dapat langsung diseret ke dalam Obsidian Vault Anda sebagai catatan portofolio harian.

---

## 2. Integrasi OpenCode (AI Coding Agent untuk Developer PA)

### A. Konfigurasi `opencode.json` & `AGENTS.md`
Untuk membantu Anda memprogram, me-refactor, atau menulis tes pada backend/frontend AI-MILO, repositori ini telah dilengkapi dengan:
- [`opencode.json`](file:///d:/Kuliah/PA/AI-MILO/opencode.json): Konfigurasi agen, instruksi stack, dan file yang diabaikan (*ignore list*).
- [`AGENTS.md`](file:///d:/Kuliah/PA/AI-MILO/AGENTS.md): Petunjuk arsitektur pipeline, struktur direktori, dan perintah eksekusi untuk agen otomatis.

### B. Menjalankan OpenCode
Jika Anda menginstal CLI OpenCode (`opencode`):
```bash
# Menjalankan OpenCode di root proyek AI-MILO
opencode
```

OpenCode akan secara otomatis membaca konteks arsitektur AI-MILO (FastAPI, Whisper, ChromaDB RAG, TTS, dan Bifrost Gateway).

---

## 3. Rangkuman Arsitektur Lengkap

| Komponen | Peran | Lokasi / Perintah |
| :--- | :--- | :--- |
| **Bifrost** | LLM Gateway (Token Budgeting, Rate Limiting, Caching) | `docker compose -f docker-compose.bifrost.yml up -d` |
| **Obsidian** | Authoring & Visualisasi Materi RAG CEFR | Folder: `Knowledge Base MILO/` (`00_Home_MOC.md`) |
| **OpenCode** | Asisten AI Coding Terminal untuk Pengembangan PA | `opencode.json` & `AGENTS.md` |
| **Backend MILO** | Voice Practice Core (ASR -> RAG -> LLM -> TTS) | `uv run uvicorn app.main:app --reload` |
