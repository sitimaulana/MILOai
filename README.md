# MILO AI Backend 🎙️

**MILO — Multimodal Interactive Learning Companion**

AI-powered English speaking practice backend with full ASR → RAG → LLM → TTS pipeline.

## Architecture

```
User Audio/Text
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                     FastAPI REST API                      │
│  POST /api/v1/voice    POST /api/v1/chat                  │
│  GET  /api/v1/session/{id}/feedback                       │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                   Pipeline Orchestrator                    │
│                                                            │
│  [Voice] → Whisper ASR ──┐                                │
│  [Text]  ────────────────┤                                │
│                          ▼                                │
│               ┌─── RAG (ChromaDB) ←── CEFR KB ───┐      │
│               │                                    │      │
│               ▼                                    │      │
│          GPT-4o Mini (LLM) ◄───────────────────────┘      │
│               │                                            │
│        ┌──────┴──────┐                                     │
│        ▼             ▼                                     │
│   Feedback      TTS (OpenAI)                               │
│   Engine           │                                       │
│        │           ▼                                       │
│        └──── PostgreSQL ────                               │
└──────────────────────────────────────────────────────────┘
       │
       ▼
{ response_text, audio_base64, feedback, transcript }
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Web Framework** | FastAPI + Uvicorn |
| **ASR** | Whisper (local, `openai-whisper`) |
| **LLM** | GPT-4o Mini (OpenAI API) |
| **RAG** | LangChain + ChromaDB |
| **Embeddings** | `text-embedding-3-small` |
| **TTS** | OpenAI TTS (`tts-1`, voice: nova) |
| **Database** | PostgreSQL (SQLAlchemy async) |
| **Package Manager** | `uv` |

## Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL running locally
- FFmpeg installed (required by Whisper)
- OpenAI API Key

Install FFmpeg:
```bash
# Windows (with chocolatey)
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### 2. Install Dependencies

```bash
# Install uv
pip install uv

# Install all project dependencies
uv sync
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY and DATABASE_URL
```

### 4. Setup Database

```bash
# Create the database
createdb milo_db

# Tables are auto-created on first startup
```

### 5. Ingest Knowledge Base

```bash
# Add your CEFR B1-B2 materials to knowledge_base/documents/
# File naming convention: [skill]_[level]_[name].pdf
# Examples:
#   grammar_B1_present_perfect.pdf
#   vocabulary_B2_phrasal_verbs.txt
#   speaking_B1_conversation_topics.docx

# Run ingestion
uv run python knowledge_base/ingest.py

# To reset and re-ingest:
uv run python knowledge_base/ingest.py --reset
```

### 6. Run the Application

To run the app, you need two things running in the background:

**Terminal 1: Start Ollama**
```bash
ollama serve
# or 'ollama run llama3.1'
```

**Terminal 2: Start the MILO Server**
```bash
uv run uvicorn app.main:app --reload --port 8000
```

**Access the UI**
Open your browser and navigate to:
👉 **http://localhost:8000/ui/index.html**

Open API docs: http://localhost:8000/docs

## API Endpoints

### 💬 Text Chat

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "Can you explain the present perfect tense?",
  "session_id": null,
  "cefr_level": "B1",
  "learning_goal": "Practice grammar for job interviews",
  "return_audio": true
}
```

**Response:**
```json
{
  "session_id": "uuid...",
  "message_id": "uuid...",
  "response_text": "Great question! The present perfect...",
  "audio_base64": "//NExAA...",
  "feedback": {
    "grammar_score": 95.0,
    "vocabulary_score": 80.0,
    "fluency_score": 85.0,
    "corrections": [],
    "positive_note": "Excellent question phrasing!",
    "tip": "Try using 'Could you elaborate' for B2 level."
  },
  "rag_sources": ["grammar_B1_present_perfect.pdf"]
}
```

### 🎙️ Voice Input

```http
POST /api/v1/voice
Content-Type: multipart/form-data

audio: <file.wav>
session_id: <optional>
cefr_level: B1
learning_goal: Practice everyday conversation
return_audio: true
```

### 📊 Session Feedback

```http
GET /api/v1/session/{session_id}/feedback
```

Returns aggregated scores and AI-generated session summary.

## Project Structure

```
AI-MILO/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (pydantic-settings)
│   ├── api/
│   │   ├── chat.py          # POST /api/v1/chat
│   │   ├── voice.py         # POST /api/v1/voice
│   │   └── feedback.py      # Session feedback routes
│   ├── core/
│   │   ├── asr.py           # Whisper ASR
│   │   ├── rag.py           # ChromaDB RAG retriever
│   │   ├── llm.py           # GPT-4o Mini conversation
│   │   ├── feedback.py      # Language feedback engine
│   │   └── tts.py           # OpenAI TTS
│   ├── db/
│   │   ├── database.py      # SQLAlchemy async engine
│   │   └── models.py        # ORM models
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response schemas
│   └── services/
│       ├── conversation.py  # Session & message persistence
│       └── pipeline.py      # Pipeline orchestrator
├── knowledge_base/
│   ├── documents/           # Your CEFR B1-B2 materials (PDF/DOCX/TXT)
│   ├── chroma_db/           # ChromaDB vector store (auto-generated)
│   └── ingest.py            # Ingestion script
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

## Knowledge Base File Naming Convention

Name your CEFR documents to enable automatic metadata tagging:

| Pattern | Skill Type | Example |
|---------|-----------|---------|
| `grammar_*` | Grammar | `grammar_B1_past_tense.pdf` |
| `vocabulary_*` | Vocabulary | `vocabulary_B2_idioms.txt` |
| `speaking_*` | Speaking | `speaking_B1_topics.docx` |
| `*_B1_*` | CEFR B1 | `grammar_B1_articles.pdf` |
| `*_B2_*` | CEFR B2 | `vocabulary_B2_advanced.pdf` |

## Running Tests

```bash
uv run pytest tests/ -v
```

## Development

```bash
# Watch mode
uv run uvicorn app.main:app --reload

# Run with specific log level
uv run uvicorn app.main:app --reload --log-level debug
```
