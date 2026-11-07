# Panduan Integrasi Bifrost AI Gateway di AI-MILO 🚀

Dokumen ini menjelaskan implementasi **Bifrost** sebagai AI Gateway layer untuk mengelola token, membatasi laju permintaan (*rate limiting* TPM/RPM), melakukan *token budgeting*, *caching*, dan *multi-provider routing* pada platform **AI-MILO**.

---

## 1. Mengapa Menggunakan Bifrost?

Pada arsitektur AI-MILO, setiap 1 interaksi user memicu 3 pemanggilan LLM:
1. **Percakapan Tutor (`app/core/llm.py`)** — Menghasilkan respon percakapan interaktif adaptif CEFR.
2. **Evaluasi Feedback (`app/core/feedback.py`)** — Menilai grammar, vocabulary, dan fluency dalam format JSON terstruktur.
3. **Penerjemah Bahasa Indonesia (`app/core/translator.py`)** — Menerjemahkan kalimat tutor sebagai *safety net* pembelajaran.

### Keuntungan Bifrost:
- **Token Budgeting & Virtual Keys**: Membatasi penggunaan token per sesi atau per mahasiswa agar kuota API tidak jebol.
- **Throttling & Rate Limiting**: Mencegah *error* `429 Too Many Requests` saat menggunakan OpenRouter Free Tier atau OpenAI Tier standar.
- **Semantic Caching**: Menyimpan respon evaluasi / translasi kalimat umum sehingga tidak memakan token berulang kali.
- **Resilience / Fallback**: Mengalihkan panggilan otomatis dari OpenRouter -> Ollama Lokal -> OpenAI jika salah satu penyedia sedang *down* atau terkena limit.
- **Observability Dashboard**: Menampilkan grafik penggunaan token, latensi, dan estimasi biaya secara visual.

---

## 2. Cara Menjalankan Bifrost Gateway

Bifrost disediakan dalam bentuk container Docker resmi dari Maxim AI.

### Langkah 1: Pastikan Docker Desktop Aktif
Pastikan aplikasi **Docker Desktop** di Windows sudah terbuka dan berjalan.

### Langkah 2: Jalankan Bifrost via Docker Compose
Jalankan perintah berikut di terminal root proyek:

```bash
docker compose -f docker-compose.bifrost.yml up -d
```

Atau jika ingin menjalankan via `docker run` langsung:
```bash
docker run -d --name milo-bifrost-gateway \
  -p 8080:8080 \
  -v ./bifrost_data:/app/data \
  -e OPENROUTER_API_KEY=sk-or-v1-... \
  -e OPENAI_API_KEY=sk-... \
  -e BIFROST_PORT=8080 \
  -e BIFROST_ENCRYPTION_KEY=milo-bifrost-token-gateway-key-32b! \
  maximhq/bifrost:latest
```

---

## 3. Mengakses Dashboard Web & Konfigurasi

1. Buka browser dan akses Dashboard Bifrost di:
   ```
   http://localhost:8080
   ```
2. **Tambah Penyedia AI (Providers)**:
   - Masukkan API Key **OpenRouter** atau **OpenAI** Anda.
   - Untuk **Ollama** lokal, masukkan base URL: `http://host.docker.internal:11434/v1`.
3. **Atur Virtual Keys & Token Budget**:
   - Masuk ke menu **Virtual Keys** -> **Create Key**.
   - Beri nama: `bk-milo-token-gateway`.
   - Atur batas:
     - **Token Quota**: misal 50.000 tokens per hari/bulan.
     - **Rate Limit**: misal 60 requests/minute (RPM) atau 10.000 tokens/minute (TPM).
4. **Aktifkan Caching**:
   - Di menu Settings / Routing, aktifkan **Cache** untuk menghemat token pada frasa-frasa yang sering berulang.

---

## 4. Mengaktifkan Bifrost di AI-MILO Backend

Buka file [`.env`](file:///d:/Kuliah/PA/AI-MILO/.env) dan ubah opsi `AI_PROVIDER`:

```ini
# Ganti dari "openrouter" atau "local" menjadi "bifrost"
AI_PROVIDER=bifrost

# Konfigurasi Bifrost
BIFROST_BASE_URL=http://localhost:8080/v1
BIFROST_API_KEY=bk-milo-token-gateway

# Format model yang ingin diteruskan oleh Bifrost:
# Contoh format: <provider>/<model_name>
BIFROST_MODEL=openrouter/nvidia/nemotron-3.5-lightning:free
# Atau jika menggunakan OpenAI:
# BIFROST_MODEL=openai/gpt-4o-mini
# Atau jika menggunakan Ollama:
# BIFROST_MODEL=ollama/llama3.1
```

Setelah mengubah `.env`, jalankan backend MILO seperti biasa:
```bash
uv run uvicorn app.main:app --reload --port 8000
```

---

## 5. Menguji Koneksi Gateway

Anda dapat menguji apakah Bifrost menerima panggilan dengan menjalankan cURL berikut:

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer bk-milo-token-gateway" \
  -d '{
    "model": "openai/gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello Bifrost, test token management!"}]
  }'
```

Seluruh log panggilan, token terpakai, dan status *budget* akan langsung muncul di dashboard `http://localhost:8080`.
