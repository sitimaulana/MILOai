# AGENTS.md — Development Guidelines for AI-MILO

This document provides context and guidelines for autonomous AI coding agents (such as **OpenCode**, Claude Code, or Antigravity) working in this repository.

---

## 1. Project Overview
- **Name**: MILO — Multimodal Interactive Learning Companion
- **Purpose**: AI English speaking practice backend with real-time feedback, CEFR adaptation, and RAG.
- **Language & Runtime**: Python 3.11+, managed via `uv`.

## 2. Architecture & Pipeline
```
User Audio/Text ──► Whisper ASR ──► ChromaDB (RAG) ──► LLM (Tutor) ──► TTS (Voice)
                                          │                   │
                            [Obsidian Vault KB]      [Bifrost Gateway]
```

## 3. Key Components & Paths
- **FastAPI Entry Point**: `app/main.py`
- **Application Configuration**: `app/config.py` (loads from `.env`)
- **Core Pipeline**:
  - `app/core/asr.py`: Whisper speech recognition
  - `app/core/rag.py`: ChromaDB retrieval
  - `app/core/llm.py`: MILO tutor conversation manager
  - `app/core/feedback.py`: CEFR grammar/vocab/fluency evaluation
  - `app/core/translator.py`: English to Indonesian translator
  - `app/core/tts.py`: Text-to-speech synthesis
- **AI Gateway (Bifrost)**: `docker-compose.bifrost.yml` (port 8080)
- **Knowledge Base (Obsidian Vault)**: `Knowledge Base MILO/`
- **Database Models**: `app/db/models.py` (SQLAlchemy async)

## 4. Common Commands
```bash
# Run backend development server
uv run uvicorn app.main:app --reload --port 8000

# Re-index Obsidian Vault into ChromaDB
uv run python knowledge_base/ingest.py --reset

# Run Bifrost Gateway
docker compose -f docker-compose.bifrost.yml up -d

# Run tests
uv run pytest

# Run DeepEval quantitative benchmarks (for thesis/PA data)
uv run python -m evaluations.run_evaluation
```
