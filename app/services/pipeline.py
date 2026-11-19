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
import re
import time
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.asr import transcribe_audio, TranscriptionResult
from app.core.feedback import analyze_utterance, FeedbackResult
from app.core.llm import generate_response, LLMResponse
from app.core.rag import rag_retriever, retrieve_adaptive, retrieve_context, RetrievedContext
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
    rag_details: list[dict] = field(default_factory=list)
    transcript: Optional[str] = None  # Only set for voice input
    avatar_emotion: str = "friendly"
    is_session_closed: bool = False


def format_friendly_rag_meta(ctx: RetrievedContext) -> dict:
    """Format rich human-readable metadata for frontend RAG inspection."""
    src = (ctx.source or "").lower()
    clean_title = (ctx.source or "").replace(".md", "").replace("_", " ").title()
    category = "Curriculum Material"
    if "vocabulary" in src or src.startswith("unit_"):
        book = "Cambridge English Vocabulary in Use (B2)"
        category = "Vocabulary & Collocations"
    elif "collins" in src or re.match(r"^[abc][1-6]", src):
        book = "Collins Speaking for IELTS"
        category = "Speaking & Fluency Strategies"
    elif "usage_" in src or "english usage" in src:
        book = "The Cambridge Guide to English Usage"
        category = "Grammar & Confusing Words"
    elif "cefr_" in src or "council" in src:
        book = "CEFR Companion Volume"
        category = "CEFR Spoken Descriptors"
    else:
        book = "MILO Grounded Knowledge Base"

    clean_snippet = re.sub(r"#+\s*", "", ctx.content or "")
    clean_snippet = re.sub(r"\s+", " ", clean_snippet).strip()
    if len(clean_snippet) > 260:
        clean_snippet = clean_snippet[:257] + "..."

    return {
        "source": ctx.source,
        "book": book,
        "title": clean_title,
        "category": category,
        "skill": ctx.skill_type or "general",
        "level": ctx.cefr_level or "B1-B2",
        "score": round(float(ctx.relevance_score), 3) if ctx.relevance_score else 0.0,
        "snippet": clean_snippet,
    }


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
        input_type: str = "text",
        transcript: Optional[str] = None,
        is_closing: bool = False,
        trigger: Optional[str] = None,
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

        # 3. Retrieve conversation history and Adaptive Hybrid RAG context concurrently
        t_rag_start = time.perf_counter()

        # Extract optional topic_id if stored in session or learning goal (e.g. A1, B2, C3)
        topic_id = getattr(session, "topic_id", None)
        if not topic_id and session and session.learning_goal:
            match = re.search(r"\b([A-C][1-6])\b", session.learning_goal)
            if match:
                topic_id = match.group(1)

        # Detect if user asks about an error, mistake, or previous correction
        user_lower = user_message.lower().strip()
        detected_error = None
        if any(w in user_lower for w in ("why is that wrong", "why was that wrong", "what did i do wrong", "my mistake", "my error", "why did you correct", "is it incorrect")):
            detected_error = "error_remediation"

        async def _fetch_rag():
            return await retrieve_adaptive(
                query=user_message,
                cefr_level=effective_cefr_level,
                topic_name=topic_name,
                topic_id=topic_id,
                detected_error=detected_error,
                k=settings.rag_top_k,
            )

        history, rag_contexts = await asyncio.gather(
            self._conv.get_history(
                actual_session_id,
                max_turns=settings.max_conversation_history,
            ),
            _fetch_rag(),
        )
        t_rag = time.perf_counter() - t_rag_start
        rag_context_str = rag_retriever.format_context_for_prompt(rag_contexts)
        rag_sources = [ctx.source for ctx in rag_contexts]
        rag_details = [format_friendly_rag_meta(ctx) for ctx in rag_contexts]

        # Extract preceding assistant turn to give context to feedback engine
        last_assistant_turn = next(
            (turn["content"] for turn in reversed(history) if turn["role"] == "assistant"),
            None,
        )

        # 4. Concurrently kick off feedback analysis with topic and preceding context (skip if auto-close trigger)
        is_auto_close_trigger = (trigger == "time_limit_reached")
        feedback_task = None
        if not is_auto_close_trigger:
            feedback_task = asyncio.create_task(
                analyze_utterance(
                    user_text=user_message,
                    cefr_level=effective_cefr_level,
                    topic=topic_name,
                    context=last_assistant_turn,
                )
            )

        # 5. LLM response generation (runs while feedback_task is computing)
        t_llm_start = time.perf_counter()
        llm_response: LLMResponse = await generate_response(
            user_message=user_message,
            history=history,
            rag_context=rag_context_str,
            learning_goal=effective_learning_goal,
            cefr_level=effective_cefr_level,
            is_closing=is_closing,
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
        tasks_map = {"tts": tts_task}
        if feedback_task:
            tasks_map["feedback"] = feedback_task
        if translation_task:
            tasks_map["translation"] = translation_task

        results_list = await asyncio.gather(*tasks_map.values(), return_exceptions=True)
        results = dict(zip(tasks_map.keys(), results_list))
        t_tts_fb = time.perf_counter() - t_tts_fb_start

        feedback_result: Optional[FeedbackResult] = None
        if "feedback" in results:
            feedback_raw = results["feedback"]
            if isinstance(feedback_raw, Exception):
                logger.warning(f"Feedback analysis encountered an error: {feedback_raw}")
            else:
                feedback_result = feedback_raw

        audio_b64: Optional[str] = None
        audio_raw = results.get("tts")
        if isinstance(audio_raw, Exception):
            logger.warning(f"TTS synthesis failed (falling back to text): {audio_raw}")
        else:
            audio_b64 = audio_raw

        translation_id: Optional[str] = None
        if "translation" in results:
            tr_raw = results["translation"]
            if isinstance(tr_raw, Exception):
                logger.warning(f"Translation failed: {tr_raw}")
            else:
                translation_id = tr_raw

        # 8. Persist to database
        saved_user_content = "(Practice time ended)" if is_auto_close_trigger else user_message
        user_msg = await self._conv.add_message(
            session_id=actual_session_id,
            role="user",
            content=saved_user_content,
            input_type=input_type,
            transcript=transcript if input_type == "voice" else None,
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
        avatar_emotion = "happy" if is_closing else "friendly"
        if not is_closing and feedback_result:
            if feedback_result.overall_score >= 88:
                avatar_emotion = "happy"
            elif feedback_result.corrections:
                avatar_emotion = "supportive"
        if not is_closing and "?" in llm_response.content and avatar_emotion == "friendly":
            avatar_emotion = "curious"

        return PipelineResult(
            session_id=actual_session_id,
            message_id=str(user_msg.id),
            response_text=llm_response.content,
            translation=translation_id,
            audio_base64=audio_b64,
            feedback=feedback_result,
            rag_sources=rag_sources,
            rag_details=rag_details,
            avatar_emotion=avatar_emotion,
            is_session_closed=is_closing,
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
        is_closing: bool = False,
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
                is_session_closed=is_closing,
            )

        logger.info(f"ASR result: '{transcript[:80]}...' (lang={asr_result.language})")

        # 2. Process as text with voice provenance
        result = await self.process_text(
            session_id=session_id,
            user_message=transcript,
            learning_goal=learning_goal,
            cefr_level=cefr_level,
            return_audio=return_audio,
            user_id=user_id,
            input_type="voice",
            transcript=transcript,
            is_closing=is_closing,
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
