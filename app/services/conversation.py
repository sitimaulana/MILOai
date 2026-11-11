"""
MILO AI Backend - Conversation Service

Manages conversation sessions and message history using the database.
Provides methods to:
  - Create, retrieve, and end sessions
  - Add messages with feedback
  - Retrieve conversation history for LLM context
  - Compute session-level feedback summaries & CEFR evaluation
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session as DBSession, Message as DBMessage, LearningProgress, User
from app.core.feedback import FeedbackResult

logger = logging.getLogger(__name__)

# ─── CEFR Score Mapping ───────────────────────────────────────────────────────

CEFR_THRESHOLDS = {
    "A1": (0, 20),
    "A2": (20, 40),
    "B1": (40, 60),
    "B2": (60, 80),
    "C1": (80, 95),
    "C2": (95, 100),
}

TOPIC_LABELS = {
    "job_interview": "Job Interview Practice",
    "academic_discussion": "Academic Discussion",
    "daily_conversation": "Daily Conversation",
}


def score_to_cefr(score: float) -> str:
    """Map an overall score (0–100) to a CEFR level."""
    for level, (low, high) in CEFR_THRESHOLDS.items():
        if low <= score < high:
            return level
    return "C2" if score >= 95 else "A1"


class ConversationService:
    """Handles all conversation persistence and retrieval."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ─── Session Management ────────────────────────────────────────────────────

    async def create_session(
        self,
        user_id: Optional[str] = None,
        learning_goal: Optional[str] = None,
        topic: Optional[str] = None,
        cefr_level: str = "B1",
    ) -> DBSession:
        """Create a new conversation session."""
        session = DBSession(
            user_id=uuid.UUID(user_id) if user_id else None,
            learning_goal=learning_goal,
            topic=topic,
            cefr_level=cefr_level,
        )
        self._db.add(session)
        await self._db.flush()
        logger.info(f"Created session {session.id} (topic={topic}, level={cefr_level})")
        return session

    async def get_session(self, session_id: str) -> Optional[DBSession]:
        """Retrieve a session by ID."""
        result = await self._db.execute(
            select(DBSession).where(DBSession.id == uuid.UUID(session_id))
        )
        return result.scalar_one_or_none()

    async def end_session(self, session_id: str) -> DBSession:
        """
        Mark a session as ended and compute final scores.
        Returns the updated session with scores.
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        # Compute aggregate scores
        summary = await self.get_session_feedback_summary(session_id)

        overall = 0.0
        count = 0
        if summary["avg_grammar_score"] > 0:
            overall += summary["avg_grammar_score"]
            count += 1
        if summary["avg_vocabulary_score"] > 0:
            overall += summary["avg_vocabulary_score"]
            count += 1
        if summary["avg_fluency_score"] > 0:
            overall += summary["avg_fluency_score"]
            count += 1
        overall = round(overall / max(count, 1), 1)

        cefr_result = score_to_cefr(overall)

        await self._db.execute(
            update(DBSession)
            .where(DBSession.id == uuid.UUID(session_id))
            .values(
                is_active=False,
                ended_at=datetime.now(timezone.utc),
                avg_grammar_score=summary["avg_grammar_score"],
                avg_vocabulary_score=summary["avg_vocabulary_score"],
                avg_fluency_score=summary["avg_fluency_score"],
                overall_score=overall,
                cefr_result=cefr_result,
            )
        )

        if session.user_id:
            for skill, score in [
                ("grammar", summary["avg_grammar_score"]),
                ("vocabulary", summary["avg_vocabulary_score"]),
                ("fluency", summary["avg_fluency_score"]),
            ]:
                if score > 0:
                    prog_res = await self._db.execute(
                        select(LearningProgress).where(
                            LearningProgress.user_id == session.user_id,
                            LearningProgress.skill == skill,
                        )
                    )
                    prog = prog_res.scalar_one_or_none()
                    if prog:
                        prog.sessions_count += 1
                        prog.score = round((prog.score * (prog.sessions_count - 1) + score) / prog.sessions_count, 1)
                        prog.total_corrections += len(summary.get("all_corrections", []))
                        prog.last_updated = datetime.now(timezone.utc)
                    else:
                        new_prog = LearningProgress(
                            user_id=session.user_id,
                            skill=skill,
                            score=score,
                            sessions_count=1,
                            total_corrections=len(summary.get("all_corrections", [])),
                        )
                        self._db.add(new_prog)

        await self._db.flush()

        # Reload session with updated values
        return await self.get_session(session_id)

    # ─── Message Management ────────────────────────────────────────────────────

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        input_type: str = "text",
        transcript: Optional[str] = None,
        feedback: Optional[FeedbackResult] = None,
    ) -> DBMessage:
        """
        Persist a message (user or assistant) to the database.

        Args:
            session_id: The session this message belongs to.
            role: "user" or "assistant"
            content: Message content text.
            input_type: "text" or "voice"
            transcript: For voice messages, the Whisper transcript.
            feedback: Optional FeedbackResult for user messages.

        Returns:
            Persisted DBMessage object.
        """
        feedback_dict = None
        if feedback and role == "user":
            feedback_dict = {
                "grammar_score": feedback.grammar_score,
                "vocabulary_score": feedback.vocabulary_score,
                "fluency_score": feedback.fluency_score,
                "overall_score": feedback.overall_score,
                "corrections": [
                    {
                        "original": c.original,
                        "corrected": c.corrected,
                        "explanation": c.explanation,
                        "error_type": c.error_type,
                    }
                    for c in feedback.corrections
                ],
                "positive_note": feedback.positive_note,
                "tip": feedback.tip,
            }

        msg = DBMessage(
            session_id=uuid.UUID(session_id),
            role=role,
            content=content,
            input_type=input_type,
            transcript=transcript,
            feedback=feedback_dict,
        )
        self._db.add(msg)
        await self._db.flush()
        return msg

    async def get_history(
        self,
        session_id: str,
        max_turns: int = 20,
    ) -> list[dict]:
        """
        Retrieve conversation history as a list of role/content dicts
        ready to be injected into the LLM messages array.

        Returns the last `max_turns` messages.
        """
        result = await self._db.execute(
            select(DBMessage)
            .where(DBMessage.session_id == uuid.UUID(session_id))
            .order_by(DBMessage.created_at.desc())
            .limit(max_turns)
        )
        messages = list(reversed(result.scalars().all()))

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def get_session_messages(self, session_id: str) -> list[dict]:
        """Retrieve full chronological conversation transcript with feedback."""
        result = await self._db.execute(
            select(DBMessage)
            .where(DBMessage.session_id == uuid.UUID(session_id))
            .order_by(DBMessage.created_at.asc())
        )
        messages = result.scalars().all()
        return [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "input_type": msg.input_type,
                "transcript": msg.transcript,
                "feedback": msg.feedback,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ]

    async def get_message_count(self, session_id: str) -> int:
        """Count messages in a session."""
        result = await self._db.execute(
            select(func.count(DBMessage.id)).where(
                DBMessage.session_id == uuid.UUID(session_id)
            )
        )
        return result.scalar_one() or 0

    # ─── Session Feedback Summary ──────────────────────────────────────────────

    async def get_session_feedback_summary(self, session_id: str) -> dict:
        """
        Aggregate all per-message feedback for a session into a summary dict.
        """
        result = await self._db.execute(
            select(DBMessage).where(
                DBMessage.session_id == uuid.UUID(session_id),
                DBMessage.role == "user",
                DBMessage.feedback.isnot(None),
            )
        )
        user_messages = result.scalars().all()

        if not user_messages:
            return {
                "total_turns": 0,
                "avg_grammar_score": 0.0,
                "avg_vocabulary_score": 0.0,
                "avg_fluency_score": 0.0,
                "all_corrections": [],
            }

        all_corrections = []
        grammar_scores = []
        vocab_scores = []
        fluency_scores = []

        for msg in user_messages:
            fb = msg.feedback
            if fb:
                grammar_scores.append(fb.get("grammar_score", 0))
                vocab_scores.append(fb.get("vocabulary_score", 0))
                fluency_scores.append(fb.get("fluency_score", 0))
                all_corrections.extend(fb.get("corrections", []))

        def safe_avg(lst: list) -> float:
            return sum(lst) / len(lst) if lst else 0.0

        return {
            "total_turns": len(user_messages),
            "avg_grammar_score": round(safe_avg(grammar_scores), 1),
            "avg_vocabulary_score": round(safe_avg(vocab_scores), 1),
            "avg_fluency_score": round(safe_avg(fluency_scores), 1),
            "all_corrections": all_corrections,
        }

    # ─── Dashboard Data ────────────────────────────────────────────────────────

    async def get_recent_sessions(self, limit: int = 10) -> list[DBSession]:
        """Get recent completed sessions for the dashboard."""
        result = await self._db.execute(
            select(DBSession)
            .where(DBSession.is_active == False)  # noqa: E712
            .order_by(DBSession.ended_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_session_with_messages(self, session_id: str) -> Optional[dict]:
        """Get a session with its message count for display."""
        session = await self.get_session(session_id)
        if not session:
            return None
        count = await self.get_message_count(session_id)
        return {
            "session": session,
            "message_count": count,
        }
