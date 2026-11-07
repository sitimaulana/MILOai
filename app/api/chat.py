"""
MILO AI Backend - Chat API Route

POST /api/v1/chat — Process text input and return MILO's response.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    FeedbackResponse,
    GrammarCorrection,
    TranslateRequest,
    TranslateResponse,
)
from app.core.translator import translate_to_indonesian
from app.services.pipeline import MILOPipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a text message to MILO",
    description=(
        "Send a text message and receive MILO's response as text and optionally as audio. "
        "Includes language feedback (grammar, vocabulary, fluency) on the user's input."
    ),
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Text conversation endpoint.

    - Creates a new session if `session_id` is null or "new".
    - Returns base64-encoded MP3 audio if `return_audio=true`.
    - Always returns feedback on the user's text.
    """
    pipeline = MILOPipeline(db)

    try:
        result = await pipeline.process_text(
            session_id=request.session_id or "new",
            user_message=request.message,
            learning_goal=request.learning_goal or "",
            cefr_level=request.cefr_level,
            return_audio=request.return_audio,
            user_id=request.user_id,
        )
    except Exception as e:
        logger.error(f"Chat pipeline error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(e)}",
        )

    # Convert internal FeedbackResult to response schema
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

    return ChatResponse(
        session_id=result.session_id,
        message_id=result.message_id,
        response_text=result.response_text,
        translation=result.translation,
        audio_base64=result.audio_base64,
        feedback=feedback_response,
        rag_sources=result.rag_sources,
        avatar_emotion=getattr(result, "avatar_emotion", "friendly"),
    )


@router.post(
    "/translate",
    response_model=TranslateResponse,
    summary="Translate text from English to Indonesian",
    description="On-demand translation helper for conversational learning safety net.",
)
@router.post(
    "/chat/translate",
    response_model=TranslateResponse,
    include_in_schema=False,
)
async def translate_text(request: TranslateRequest) -> TranslateResponse:
    """Translate an English phrase or tutor sentence to Indonesian."""
    try:
        translated = await translate_to_indonesian(request.text)
        return TranslateResponse(text=request.text, translation=translated)
    except Exception as e:
        logger.error(f"Translation API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation error: {str(e)}",
        )
