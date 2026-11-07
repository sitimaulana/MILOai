"""
MILO AI Backend - Pipeline Orchestrator

The central service that coordinates the full AI processing pipeline:

  [Voice Input] → ASR (Whisper) → text
  [Text Input]  ─────────────────────────────────────┐
                                                       ↓
                      Conversation History ──── LLM (GPT-4o Mini)
                      RAG Context (CEFR) ─────── ↑
                                                  │
                      Feedback Engine ──── user text (async)
                                                  │
                      TTS (OpenAI) ──────── LLM response
                                                  │
                      ← Return: {response, audio, feedback}

Usage:
    from app.services.pipeline import MILOPipeline

    pipeline = MILOPipeline(db_session)
    result = await pipeline.process_text(
        session_id="...",
        user_message="Can you help me with past tense?",
        learning_goal="Practice grammar",
        cefr_level="B1",
        return_audio=True,
    )
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.asr import transcribe_audio, TranscriptionResult
from app.core.feedback import analyze_utterance, FeedbackResult
from app.core.llm import generate_response, LLMResponse
from app.core.rag import rag_retriever, retrieve_context, RetrievedContext
from app.core.translator import translate_to_indonesian
from app.core.tts import synthesize_speech
from app.services.conversation import ConversationService

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Complete result from one pipeline turn."""
    session_id: str
    message_id: str
    response_text: str
    translation: Optional[str] = None
    audio_base64: Optional[str] = None
    feedback: Optional[FeedbackResult] = None
    rag_sources: list[str] = field(default_factory=list)
    transcript: Optional[str] = None  # Only set for voice input
    avatar_emotion: str = "friendly"


class MILOPipeline:
    """
    Main orchestrator for MILO's AI processing pipeline.
    
    One instance is created per request (injected with a DB session).
    """

    def __init__(self, db: AsyncSession) -> None:
        self._conv = ConversationService(db)

    # ─── Public API ────────────────────────────────────────────────────────────

    async def process_text(
        self,
        session_id: str,
        user_message: str,
        learning_goal: str = "",
        cefr_level: str = "B1",
        return_audio: bool = True,
        user_id: Optional[str] = None,
    ) -> PipelineResult:
        """
        Process a text input through the full pipeline.
        
        Steps:
          1. Ensure session exists (create if new)
          2. Retrieve conversation history
          3. RAG: fetch relevant CEFR context
          4. LLM: generate MILO response
          5. Feedback: analyze user's text (runs in parallel with TTS)
          6. TTS: synthesize MILO's response to audio
          7. Persist messages to database
          8. Return PipelineResult
        """
        # 1. Session setup
        session = await self._ensure_session(
            session_id, user_id, learning_goal, cefr_level
        )
        actual_session_id = str(session.id)

        # 2. Derive effective learning goal and CEFR level from session
        effective_learning_goal = learning_goal or (session.learning_goal if session else "") or ""
        effective_cefr_level = cefr_level or (session.cefr_level if session else "B1") or "B1"

        topic_name = getattr(session, "topic", None)
        if topic_name:
            topic_personas = {
                "job_interview": "Topic: Job Interview Practice. You are a professional, courteous job interviewer. Ask realistic interview questions (behavioral, situational, experience-based), probe their answers, and help the user practice formal and confident workplace English.",
                "academic_discussion": "Topic: Academic Discussion. You are a scholarly conversation partner. Engage in structured discussion, exchange viewpoints on academic or intellectual subjects, encourage reasoned arguments, and introduce formal academic vocabulary.",
                "daily_conversation": "Topic: Daily Conversation. You are a warm, casual conversational partner. Talk about daily life, hobbies, travel, opinions, and culture in a relaxed, friendly, and natural conversational manner.",
            }
            persona_ctx = topic_personas.get(topic_name)
            if persona_ctx:
                effective_learning_goal = f"{persona_ctx}\n\nAdditional goal: {effective_learning_goal}".strip()

        t_start = time.perf_counter()

        # 3. Concurrently kick off feedback analysis immediately!
        # analyze_utterance only depends on user_message and effective_cefr_level,
        # so it runs in parallel with history retrieval, RAG, and LLM generation.
        feedback_task = asyncio.create_task(
            analyze_utterance(user_message, effective_cefr_level)
        )

        # 4. Fetch conversation history and RAG context concurrently
        t_rag_start = time.perf_counter()
        history, rag_contexts = await asyncio.gather(
            self._conv.get_history(
                actual_session_id,
                max_turns=settings.max_conversation_history,
            ),
            retrieve_context(
                query=user_message,
                cefr_level=effective_cefr_level,
            ),
        )
        t_rag = time.perf_counter() - t_rag_start
        rag_context_str = rag_retriever.format_context_for_prompt(rag_contexts)
        rag_sources = [ctx.source for ctx in rag_contexts]

        # 5. LLM response generation (runs while feedback_task is already computing!)
        t_llm_start = time.perf_counter()
        llm_response: LLMResponse = await generate_response(
            user_message=user_message,
            history=history,
            rag_context=rag_context_str,
            learning_goal=effective_learning_goal,
            cefr_level=effective_cefr_level,
        )
        t_llm = time.perf_counter() - t_llm_start

        # 6. Concurrently start TTS synthesis (and optional translation only if enabled)
        t_tts_fb_start = time.perf_counter()
        tts_task = asyncio.create_task(
            synthesize_speech(llm_response.content) if return_audio else _noop()
        )
        translation_task = (
            asyncio.create_task(translate_to_indonesian(llm_response.content))
            if getattr(settings, "auto_translate_responses", False)
            else None
        )

        # 7. Await feedback and TTS (and optional translation) in parallel
        tasks = [feedback_task, tts_task]
        if translation_task:
            tasks.append(translation_task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        t_tts_fb = time.perf_counter() - t_tts_fb_start

        feedback_raw = results[0]
        if isinstance(feedback_raw, Exception):
            logger.warning(f"Feedback analysis encountered an error: {feedback_raw}")
            feedback_result: Optional[FeedbackResult] = None
        else:
            feedback_result = feedback_raw

        audio_raw = results[1]
        if isinstance(audio_raw, Exception):
            logger.warning(f"TTS synthesis failed (falling back to text): {audio_raw}")
            audio_b64: Optional[str] = None
        else:
            audio_b64 = audio_raw

        translation_id: Optional[str] = None
        if translation_task:
            tr_raw = results[2]
            if isinstance(tr_raw, Exception):
                logger.warning(f"Translation failed: {tr_raw}")
            else:
                translation_id = tr_raw

        # 8. Persist to database
        user_msg = await self._conv.add_message(
            session_id=actual_session_id,
            role="user",
            content=user_message,
            input_type="text",
            feedback=feedback_result,
        )
        await self._conv.add_message(
            session_id=actual_session_id,
            role="assistant",
            content=llm_response.content,
        )

        t_total = time.perf_counter() - t_start
        logger.info(
            f"⚡ [PIPELINE TIMINGS] RAG={t_rag:.2f}s | LLM={t_llm:.2f}s | TTS/Feedback={t_tts_fb:.2f}s | TurnTotal={t_total:.2f}s"
        )

        # Contextual emotion state for avatar animation (Three.js blendshapes / visemes)
        avatar_emotion = "friendly"
        if feedback_result:
            if feedback_result.overall_score >= 88:
                avatar_emotion = "happy"
            elif feedback_result.corrections:
                avatar_emotion = "supportive"
        if "?" in llm_response.content and avatar_emotion == "friendly":
            avatar_emotion = "curious"

        return PipelineResult(
            session_id=actual_session_id,
            message_id=str(user_msg.id),
            response_text=llm_response.content,
            translation=translation_id,
            audio_base64=audio_b64,
            feedback=feedback_result,
            rag_sources=rag_sources,
            avatar_emotion=avatar_emotion,
        )

    async def process_voice(
        self,
        session_id: str,
        audio_bytes: bytes,
        audio_filename: str = "audio.wav",
        learning_goal: str = "",
        cefr_level: str = "B1",
        return_audio: bool = True,
        user_id: Optional[str] = None,
    ) -> PipelineResult:
        """
        Process voice input through the full pipeline.
        
        Steps:
          1. ASR: transcribe audio using Whisper
          2. Continue with the same text pipeline (steps 2–7 above)
          3. Include transcript in the result
        """
        # 1. Transcribe audio
        t_asr_start = time.perf_counter()
        logger.info(f"🎙️ ASR: transcribing '{audio_filename}'...")
        asr_result: TranscriptionResult = await transcribe_audio(
            audio_bytes, audio_filename, language="en"
        )
        t_asr = time.perf_counter() - t_asr_start
        transcript = (asr_result.text or "").strip()
        logger.info(f"🎙️ ASR complete in {t_asr:.2f}s: '{transcript[:60]}...'")

        if not transcript:
            logger.info("ASR: No speech detected or audio inaudible. Providing polite fallback.")
            session = await self._ensure_session(session_id, user_id, learning_goal, cefr_level)
            clarification = "I couldn't hear any words clearly. Please make sure your microphone is active and try speaking again!"
            audio_b64 = None
            if return_audio:
                try:
                    audio_b64 = await synthesize_speech(clarification)
                except Exception as e:
                    logger.warning(f"Fallback TTS failed: {e}")

            return PipelineResult(
                session_id=str(session.id),
                message_id="fallback",
                response_text=clarification,
                audio_base64=audio_b64,
                transcript="(Inaudible speech)",
                feedback=None,
            )

        logger.info(f"ASR result: '{transcript[:80]}...' (lang={asr_result.language})")

        # 2. Process as text
        result = await self.process_text(
            session_id=session_id,
            user_message=transcript,
            learning_goal=learning_goal,
            cefr_level=cefr_level,
            return_audio=return_audio,
            user_id=user_id,
        )

        # Attach transcript to the result
        result.transcript = transcript
        return result

    # ─── Session Summary ───────────────────────────────────────────────────────

    async def get_session_summary(self, session_id: str) -> dict:
        """Return aggregated feedback for a session."""
        return await self._conv.get_session_feedback_summary(session_id)

    # ─── Private Helpers ───────────────────────────────────────────────────────

    async def _ensure_session(
        self,
        session_id: str,
        user_id: Optional[str],
        learning_goal: str,
        cefr_level: str,
    ):
        """
        Return existing session or create a new one.
        
        If session_id is "new" or the session doesn't exist, a new session is created.
        """
        if session_id and session_id.lower() != "new":
            existing = await self._conv.get_session(session_id)
            if existing:
                return existing

        # Create new session
        return await self._conv.create_session(
            user_id=user_id,
            learning_goal=learning_goal,
            cefr_level=cefr_level,
        )


async def _noop() -> None:
    """No-op coroutine for when TTS is disabled."""
    return None
