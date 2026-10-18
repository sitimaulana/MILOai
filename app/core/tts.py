"""
MILO AI Backend - TTS Module (Text-to-Speech)

Converts MILO's text responses to speech using OpenAI TTS API.
Returns audio as base64-encoded MP3 string for easy API transport.

Usage:
    from app.core.tts import synthesize_speech

    audio_b64 = await synthesize_speech("Hello! Let's practice English today.")
    # Decode on the client side: base64.b64decode(audio_b64) → MP3 bytes
"""

import asyncio
import base64
import logging

try:
    import edge_tts
except ImportError:
    edge_tts = None

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# Maximum text length to send to TTS in one call (OpenAI limit: 4096 chars)
MAX_TTS_LENGTH = 4000


class TTSSynthesizer:
    """OpenAI TTS wrapper for MILO voice output."""

    def __init__(self) -> None:
        if settings.ai_provider == "openai":
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        else:
            self._client = None  # We will use edge-tts directly

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        model: str | None = None,
    ) -> str:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize (max 4000 characters).
            voice: TTS voice name. Defaults to settings.tts_voice ("nova").
            model: TTS model. Defaults to settings.tts_model ("tts-1").

        Returns:
            Base64-encoded MP3 audio string.

        Raises:
            ValueError: If text is empty.
        """
        text = text.strip()
        if not text:
            raise ValueError("TTS input text cannot be empty.")

        # Truncate to avoid exceeding API limits
        if len(text) > MAX_TTS_LENGTH:
            logger.warning(
                f"TTS text truncated from {len(text)} to {MAX_TTS_LENGTH} characters."
            )
            text = text[:MAX_TTS_LENGTH]

        voice = voice or settings.tts_voice
        model = model or settings.tts_model

        logger.debug(f"TTS synthesizing {len(text)} chars with voice='{voice}'")

        try:
            if settings.ai_provider in ("local", "openrouter"):
                if edge_tts is None:
                    raise ImportError("edge-tts is not installed. Run `uv sync` to install it.")
                
                # Edge-TTS voice mapping (fallback to Aria if standard OpenAI voice is requested)
                edge_voice = "en-US-AriaNeural"
                if voice == "nova" or voice == "shimmer":
                    edge_voice = "en-US-AriaNeural"
                elif voice == "onyx" or voice == "echo":
                    edge_voice = "en-US-ChristopherNeural"
                
                communicate = edge_tts.Communicate(text, edge_voice)
                audio_data = bytearray()
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data.extend(chunk["data"])
                audio_bytes = bytes(audio_data)
            else:
                response = await self._client.audio.speech.create(
                    model=model,
                    voice=voice,  # type: ignore[arg-type]
                    input=text,
                    response_format="mp3",
                )
                audio_bytes = response.content

        except Exception as e:
            logger.error(f"TTS API error: {e}")
            raise

        # Encode to base64 for JSON transport
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        logger.debug(f"TTS complete: {len(audio_bytes)} bytes → {len(audio_b64)} base64 chars")

        return audio_b64

    async def synthesize_to_bytes(
        self,
        text: str,
        voice: str | None = None,
        model: str | None = None,
    ) -> bytes:
        """
        Synthesize speech and return raw MP3 bytes (useful for streaming).
        """
        text = text.strip()
        if not text:
            raise ValueError("TTS input text cannot be empty.")

        if len(text) > MAX_TTS_LENGTH:
            text = text[:MAX_TTS_LENGTH]

        voice = voice or settings.tts_voice
        model = model or settings.tts_model

        if settings.ai_provider in ("local", "openrouter"):
            if edge_tts is None:
                raise ImportError("edge-tts is not installed.")
            edge_voice = "en-US-AriaNeural"
            communicate = edge_tts.Communicate(text, edge_voice)
            audio_data = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])
            return bytes(audio_data)
        else:
            response = await self._client.audio.speech.create(
                model=model,
                voice=voice,  # type: ignore[arg-type]
                input=text,
                response_format="mp3",
            )
            return response.content


# Global singleton
tts_synthesizer = TTSSynthesizer()


async def synthesize_speech(
    text: str,
    voice: str | None = None,
) -> str:
    """
    High-level TTS helper — returns base64-encoded MP3.
    This is the main entry point used by the pipeline service.
    """
    return await tts_synthesizer.synthesize(text, voice=voice)
