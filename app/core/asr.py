"""
MILO AI Backend - ASR Module (Whisper Local)

Handles speech-to-text conversion using the local Whisper model.
Supports common audio formats: WAV, MP3, WebM, OGG, M4A.

Usage:
    from app.core.asr import transcribe_audio

    result = await transcribe_audio(audio_bytes, filename="recording.wav")
    print(result.text)
"""

import asyncio
import contextlib
import io
import logging
import tempfile
import os
from dataclasses import dataclass
from pathlib import Path

try:
    import whisper
except ImportError:
    whisper = None
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

# Supported audio MIME types / extensions
SUPPORTED_FORMATS = {".wav", ".mp3", ".webm", ".ogg", ".m4a", ".flac"}


def _ensure_ffmpeg_in_path() -> None:
    """Ensure ffmpeg executable is available in PATH for Whisper."""
    import shutil
    import sys

    # If ffmpeg is already reachable, nothing to do
    if shutil.which("ffmpeg") is not None:
        return

    project_root = Path(__file__).resolve().parent.parent.parent
    candidates = [
        str(project_root),
        str(project_root / ".venv" / "Scripts"),
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


_ensure_ffmpeg_in_path()


@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float  # Average log probability (0.0 = best, negative = worse)
    segments: list[dict]


class WhisperASR:
    """
    Singleton wrapper around the Whisper model (Local GPU/CPU or Cloud API).
    
    In local mode, the model is loaded once at startup.
    In cloud mode (Groq / OpenAI), requests are dispatched directly via API.
    """

    _instance: "WhisperASR | None" = None
    _model: object | None = None

    def __new__(cls) -> "WhisperASR":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self) -> None:
        """Load the Whisper model into memory. Call once at startup."""
        if getattr(settings, "whisper_provider", "local") in ("groq", "openai"):
            provider = settings.whisper_provider
            model_name = getattr(settings, "whisper_cloud_model", "whisper-large-v3-turbo")
            logger.info(f"Using Cloud Whisper ASR provider: {provider} ({model_name})")
            return

        if self._model is not None:
            logger.info("Whisper model already loaded, skipping.")
            return

        if whisper is None:
            logger.error("Whisper library not installed. Switch WHISPER_PROVIDER=groq or install whisper.")
            return

        model_size = settings.whisper_model_size
        device = settings.whisper_device

        if device == "cuda":
            import torch
            if not torch.cuda.is_available():
                logger.warning(
                    "CUDA requested for Whisper but torch.cuda.is_available() is False. "
                    "Falling back to CPU."
                )
                device = "cpu"
            else:
                gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"GPU acceleration active for Whisper: {gpu_name}")

        logger.info(f"Loading Whisper model '{model_size}' on device '{device}'...")
        download_root = "D:/.whisper_cache" if os.path.exists("D:/") else None
        self._model = whisper.load_model(model_size, device=device, download_root=download_root)
        logger.info("Whisper model loaded successfully.")

    @property
    def is_loaded(self) -> bool:
        if getattr(settings, "whisper_provider", "local") in ("groq", "openai"):
            return True
        return self._model is not None

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio bytes using the local Whisper model.

        Args:
            audio_bytes: Raw audio file content
            filename: Original filename (used to detect format)
            language: Force a specific language (e.g. "en"). None = auto-detect.

        Returns:
            TranscriptionResult with text, detected language, and segments.

        Raises:
            ValueError: If the audio format is unsupported.
            RuntimeError: If the Whisper model is not loaded.
        """
        # If cloud provider is configured, dispatch directly via API
        if getattr(settings, "whisper_provider", "local") in ("groq", "openai"):
            return await self._transcribe_cloud(audio_bytes, filename, language)

        if self._model is None:
            logger.info("Whisper model not pre-loaded; auto-loading now...")
            self.load()
            if self._model is None:
                raise RuntimeError("Whisper model is not loaded. Call load() first.")

        # Validate format
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format '{ext}'. "
                f"Supported: {', '.join(SUPPORTED_FORMATS)}"
            )

        # Write bytes to a temp file (Whisper needs a file path)
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(audio_bytes)

        try:
            # Run in thread pool to avoid blocking the async event loop
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._transcribe_sync(tmp_path, language),
            )
        finally:
            # Always clean up the temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        return result

    def _transcribe_sync(
        self,
        audio_path: str,
        language: str | None,
    ) -> TranscriptionResult:
        """Synchronous transcription (runs in thread pool executor)."""
        is_cuda = False
        try:
            if hasattr(self._model, "device"):
                is_cuda = self._model.device.type == "cuda"
        except Exception:
            pass

        options: dict = {
            "task": "transcribe",
            "fp16": is_cuda,
            "verbose": None,
            "temperature": 0.0,
            "condition_on_previous_text": False,
            "no_speech_threshold": 0.6,
        }

        # English-only models (like small.en or base.en) reject or don't need a language arg
        if getattr(self._model, "is_multilingual", True):
            options["language"] = language or "en"

        # Ensure ffmpeg is in PATH before whisper subprocess calls
        _ensure_ffmpeg_in_path()

        # Redirect stderr and stdout to prevent OSError [Errno 22] Invalid argument on Windows consoles
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            result = self._model.transcribe(audio_path, **options)

        # Calculate average log probability as confidence indicator
        segments = result.get("segments", [])
        text = result.get("text", "").strip()

        # Filter out YouTube subtitle noise and silent hallucinations
        if not segments:
            text = ""
        else:
            clean_check = text.lower().rstrip(".!,? ")
            hallucinations = {
                "thanks for watching",
                "thank you for watching",
                "subtitles by",
                "subscribe",
                "please subscribe",
                "watching",
                "thank you for your time",
                "thanks for listening",
            }
            if clean_check in hallucinations and segments[0].get("no_speech_prob", 0.0) > 0.6:
                text = ""

        if segments:
            avg_logprob = sum(s.get("avg_logprob", 0.0) for s in segments) / len(segments)
        else:
            avg_logprob = 0.0

        return TranscriptionResult(
            text=text,
            language=result.get("language", "en"),
            confidence=avg_logprob,
            segments=segments,
        )

    async def _transcribe_cloud(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio using Groq or OpenAI Whisper API for lightweight hosting."""
        from openai import AsyncOpenAI

        provider = getattr(settings, "whisper_provider", "groq")
        if provider == "groq":
            api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY", "")
            base_url = getattr(settings, "groq_base_url", "https://api.groq.com/openai/v1")
            model_name = getattr(settings, "whisper_cloud_model", "whisper-large-v3-turbo")
        else:
            api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
            base_url = None
            model_name = "whisper-1"

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = AsyncOpenAI(**client_kwargs)

        # Transcribe audio file in-memory
        resp = await client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model=model_name,
            language=language or "en",
            response_format="verbose_json",
        )

        text = getattr(resp, "text", "") or ""
        lang = getattr(resp, "language", language or "en") or "en"
        raw_segments = getattr(resp, "segments", []) or []
        segments = []
        for s in raw_segments:
            if isinstance(s, dict):
                segments.append(s)
            elif hasattr(s, "__dict__"):
                segments.append(s.__dict__)
            else:
                segments.append({"text": getattr(s, "text", "")})

        avg_logprob = 0.0
        if segments:
            logprobs = [s.get("avg_logprob", 0.0) for s in segments if "avg_logprob" in s]
            if logprobs:
                avg_logprob = sum(logprobs) / len(logprobs)

        return TranscriptionResult(
            text=text.strip(),
            language=lang,
            confidence=avg_logprob,
            segments=segments,
        )


# Global singleton instance
whisper_asr = WhisperASR()


async def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "audio.wav",
    language: str | None = "en",
) -> TranscriptionResult:
    """
    High-level helper function for audio transcription.
    
    This is the main entry point used by the voice API endpoint.
    """
    return await whisper_asr.transcribe(audio_bytes, filename, language)
