"""
MILO AI Backend - Voice API Route

POST /api/v1/voice — Process voice input (audio file upload) and return MILO's response.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.asr import transcribe_audio
from app.models.schemas import (
    FeedbackResponse,
    GrammarCorrection,
    VoiceResponse,
)
from app.services.pipeline import MILOPipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Voice"])

# Max audio file size: 25 MB (OpenAI Whisper API limit)
MAX_AUDIO_SIZE_MB = 25
MAX_AUDIO_SIZE_BYTES = MAX_AUDIO_SIZE_MB * 1024 * 1024


@router.post(
    "/voice",
    response_model=VoiceResponse,
    summary="Send a voice recording to MILO",
    description=(
        "Upload an audio file (WAV, MP3, WebM, OGG, M4A) and receive:\n"
        "- The Whisper transcription of your speech\n"
        "- MILO's text response\n"
        "- MILO's audio response (base64 MP3)\n"
        "- Language feedback on your utterance"
    ),
)
async def voice(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, WebM, OGG, M4A)"),
    session_id: Optional[str] = Form(None, description="Existing session ID or null for new"),
    user_id: Optional[str] = Form(None, description="Optional user ID"),
    learning_goal: Optional[str] = Form(None, description="e.g. 'Practice job interview English'"),
    cefr_level: str = Form("B1", description="Target CEFR level: A2, B1, B2"),
    return_audio: bool = Form(True, description="Whether to return TTS audio"),
    db: AsyncSession = Depends(get_db),
) -> VoiceResponse:
    """
    Voice conversation endpoint.

    Accepts multipart/form-data with an audio file and optional metadata fields.
    Internally: Audio → Whisper → Text → LLM + RAG + Feedback + TTS → Response.
    """
    # Validate file size
    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file too large. Maximum size is {MAX_AUDIO_SIZE_MB} MB.",
        )

    if len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty.",
        )

    filename = audio.filename or "audio.wav"
    logger.info(
        f"Voice request: file='{filename}', size={len(audio_bytes)} bytes, "
        f"session={session_id}, level={cefr_level}"
    )

    pipeline = MILOPipeline(db)

    try:
        result = await pipeline.process_voice(
            session_id=session_id or "new",
            audio_bytes=audio_bytes,
            audio_filename=filename,
            learning_goal=learning_goal or "",
            cefr_level=cefr_level,
            return_audio=return_audio,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Voice pipeline error: {e}\n{tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(e)}\nTraceback: {tb}",
        )

    # Convert feedback to response schema
    feedback_response: Optional[FeedbackResponse] = None
    if result.feedback:
        fb = result.feedback
        feedback_response = FeedbackResponse(
            grammar_score=fb.grammar_score,
            vocabulary_score=fb.vocabulary_score,
            fluency_score=fb.fluency_score,
            corrections=[
                GrammarCorrection(
                    original=c.original,
                    corrected=c.corrected,
                    explanation=c.explanation,
                    error_type=c.error_type,
                )
                for c in fb.corrections
            ],
            positive_note=fb.positive_note,
            tip=fb.tip,
            grammar_tip=getattr(fb, "grammar_tip", None),
            vocabulary_tip=getattr(fb, "vocabulary_tip", None),
            fluency_tip=getattr(fb, "fluency_tip", None),
        )

    return VoiceResponse(
        session_id=result.session_id,
        message_id=result.message_id,
        transcript=result.transcript or "",
        response_text=result.response_text,
        translation=result.translation,
        audio_base64=result.audio_base64,
        feedback=feedback_response,
        rag_sources=result.rag_sources,
        avatar_emotion=getattr(result, "avatar_emotion", "friendly"),
    )


@router.post(
    "/voice/transcribe",
    summary="Fast speech-to-text only (ASR)",
    description="Quickly transcribes user audio in ~0.3s on CUDA without waiting for LLM or TTS.",
)
async def transcribe_only(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form("en", description="Target language code (default 'en')"),
) -> dict:
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty.",
        )
    filename = audio.filename or "audio.wav"
    result = await transcribe_audio(audio_bytes, filename=filename, language=language or "en")
    return {
        "transcript": (result.text or "").strip(),
        "confidence": result.confidence,
        "language": result.language,
    }

