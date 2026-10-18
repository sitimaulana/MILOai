"""
MILO AI Backend - Test Suite: ASR Module

Tests for the Whisper ASR wrapper.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_whisper_model():
    """Mock the Whisper model."""
    model = MagicMock()
    model.transcribe.return_value = {
        "text": "Hello, my name is Alice and I want to practice English.",
        "language": "en",
        "segments": [
            {"avg_logprob": -0.3, "text": "Hello, my name is Alice"},
            {"avg_logprob": -0.2, "text": "and I want to practice English."},
        ],
    }
    return model


def test_transcription_result_fields(mock_whisper_model):
    """Test that TranscriptionResult contains expected fields."""
    from app.core.asr import WhisperASR, TranscriptionResult

    asr = WhisperASR()
    asr._model = mock_whisper_model

    result = asr._transcribe_sync("fake_path.wav", language="en")

    assert isinstance(result, TranscriptionResult)
    assert result.text == "Hello, my name is Alice and I want to practice English."
    assert result.language == "en"
    assert isinstance(result.confidence, float)
    assert len(result.segments) == 2


def test_unsupported_format_raises():
    """Test that unsupported audio formats raise ValueError."""
    import asyncio
    from app.core.asr import WhisperASR

    asr = WhisperASR()
    asr._model = MagicMock()

    with pytest.raises(ValueError, match="Unsupported audio format"):
        asyncio.get_event_loop().run_until_complete(
            asr.transcribe(b"fake_bytes", "audio.xyz")
        )


def test_not_loaded_raises():
    """Test that calling transcribe before load() raises RuntimeError."""
    import asyncio
    from app.core.asr import WhisperASR

    asr = WhisperASR.__new__(WhisperASR)
    asr._model = None

    with pytest.raises(RuntimeError, match="not loaded"):
        asyncio.get_event_loop().run_until_complete(
            asr.transcribe(b"fake_bytes", "audio.wav")
        )
