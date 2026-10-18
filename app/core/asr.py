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

import whisper
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

# Supported audio MIME types / extensions
SUPPORTED_FORMATS = {".wav", ".mp3", ".webm", ".ogg", ".m4a", ".flac"}


@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float  # Average log probability (0.0 = best, negative = worse)
    segments: list[dict]


class WhisperASR:
    """
    Singleton wrapper around the local Whisper model.
    
    The model is loaded once at startup and reused for all requests
    to avoid the expensive model loading overhead per request.
    """

    _instance: "WhisperASR | None" = None
    _model: whisper.Whisper | None = None

    def __new__(cls) -> "WhisperASR":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self) -> None:
        """Load the Whisper model into memory. Call once at startup."""
        if self._model is not None:
            logger.info("Whisper model already loaded, skipping.")
            return

        model_size = settings.whisper_model_size
        device = settings.whisper_device

        logger.info(f"Loading Whisper model '{model_size}' on device '{device}'...")
        self._model = whisper.load_model(model_size, device=device)
        logger.info("✅ Whisper model loaded successfully.")

    @property
    def is_loaded(self) -> bool:
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
        options: dict = {
            "language": language,
            "task": "transcribe",
            "fp16": False,  # Disable FP16 for CPU compatibility
            "verbose": None,  # In Whisper, verbose=None disables tqdm (verbose=False enables it!)
        }

        # Redirect stderr and stdout to prevent OSError [Errno 22] Invalid argument on Windows consoles
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            result = self._model.transcribe(audio_path, **options)

        # Calculate average log probability as confidence indicator
        segments = result.get("segments", [])
        if segments:
            avg_logprob = sum(s.get("avg_logprob", 0.0) for s in segments) / len(segments)
        else:
            avg_logprob = 0.0

        return TranscriptionResult(
            text=result["text"].strip(),
            language=result.get("language", "en"),
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
