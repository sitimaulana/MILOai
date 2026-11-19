"""
MILO AI Backend - FastAPI Application Entry Point (Reload triggered)

Initializes the FastAPI app with:
  - CORS middleware
  - Lifespan events (load Whisper, RAG on startup)
  - API routers
  - Health check endpoint
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import sys

# Ensure ffmpeg is accessible in PATH for Whisper
def _ensure_ffmpeg():
    import shutil
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        project_root,
        os.path.join(project_root, ".venv", "Scripts"),
    ]
    try:
        import imageio_ffmpeg
        img_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        img_dir = os.path.dirname(img_ffmpeg)
        target_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
        target_path = os.path.join(img_dir, target_name)
        if not os.path.exists(target_path) and os.path.exists(img_ffmpeg):
            try:
                shutil.copy2(img_ffmpeg, target_path)
            except Exception:
                pass
        candidates.append(img_dir)
    except Exception:
        pass

    for d in candidates:
        if os.path.isdir(d) and d not in os.environ.get("PATH", ""):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")

_ensure_ffmpeg()

from app.api import auth, chat, curriculum, evaluation, feedback, voice
from app.config import settings
from app.core.asr import whisper_asr
from app.core.rag import rag_retriever
from app.db.database import init_db
from app.models.schemas import HealthResponse

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup and shutdown lifecycle handler.
    
    Startup:
      - Initialize database tables (MySQL/SQLite)
      - Load Whisper model into memory
      - Load ChromaDB vector store
    """
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)

    # Initialize database tables
    try:
        await init_db()
        logger.info("✅ Database tables initialized.")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning("Continuing without database — some endpoints may fail.")

    # Load Whisper model
    try:
        whisper_asr.load()
    except Exception as e:
        logger.error(f"❌ Whisper model failed to load: {e}")
        logger.warning("Voice endpoint will be unavailable.")

    # Load RAG vector store
    try:
        rag_retriever.load()
    except Exception as e:
        logger.error(f"❌ RAG retriever failed to load: {e}")
        logger.warning("RAG context will be unavailable (responses will be LLM-only).")

    logger.info("✅ MILO is ready to serve requests!")
    logger.info(f"   Docs: http://localhost:8000/docs")

    yield

    # Shutdown
    logger.info("MILO shutting down...")


# ─── App Instance ─────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "**MILO** — Multimodal Interactive Learning Companion\n\n"
        "AI-powered English speaking practice platform with:\n"
        "- 🎙️ Voice input (Whisper ASR)\n"
        "- 🤖 Intelligent tutoring (GPT-4o Mini)\n"
        "- 📚 CEFR B1–B2 knowledge retrieval (RAG)\n"
        "- 🔊 Voice output (OpenAI TTS)\n"
        "- 📝 Language feedback (Grammar & Vocabulary)\n"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ─── CORS Middleware ───────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(feedback.router)
app.include_router(evaluation.router)
app.include_router(curriculum.router)



# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
)
async def health_check() -> HealthResponse:
    """Check the health status of MILO and its dependencies."""
    # Test DB connection
    db_ok = False
    try:
        from app.db.database import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="ok",
        version=settings.app_version,
        whisper_loaded=whisper_asr.is_loaded,
        chroma_ready=rag_retriever.is_ready,
        db_connected=db_ok,
    )


@app.get("/", tags=["System"], summary="Root endpoint - Redirect to UI")
async def root() -> RedirectResponse:
    """Redirect root access directly to the MILO web interface."""
    return RedirectResponse(url="/ui/index.html")

# ─── Frontend ─────────────────────────────────────────────────────────────────

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
logger.info(f"Frontend directory: {frontend_dir} (exists={os.path.exists(frontend_dir)})")
if os.path.exists(frontend_dir):
    app.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    logger.info("✅ Frontend mounted at /ui")
