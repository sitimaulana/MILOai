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

from app.db.models import (
    Session as DBSession,
    Message as DBMessage,
    LearningProgress,
    User,
    UserGamification,
    UserBadge,
    SystemLogAnalytics,
)
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

        if session.user_id:
            start_log = SystemLogAnalytics(
                user_id=session.user_id,
                session_id=session.id,
                event_type="session_start",
                duration_seconds=0,
                turns_count=0,
                extra_meta={"topic": topic, "cefr_level": cefr_level, "learning_goal": learning_goal},
            )
            self._db.add(start_log)

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
        Mark a session as ended, compute final scores, and update gamification.
        Returns the updated session with scores and gamification_info attribute.
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

        gamification_info = {
            "xp_earned": 0,
            "current_streak": 0,
            "unlocked_badges": [],
        }

        if session.user_id:
            # 1. Update skill-by-skill progress
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

            # 2. Gamification: calculate earned XP and streak
            session_xp = 50 + int(overall * 0.5)
            gamification_info["xp_earned"] = session_xp

            now_utc = datetime.now(timezone.utc)
            today_date = now_utc.date()

            gam_res = await self._db.execute(
                select(UserGamification).where(UserGamification.user_id == session.user_id)
            )
            gam = gam_res.scalar_one_or_none()

            if not gam:
                gam = UserGamification(
                    user_id=session.user_id,
                    points=session_xp,
                    current_streak=1,
                    highest_streak=1,
                    last_practice_date=now_utc,
                )
                self._db.add(gam)
                gamification_info["current_streak"] = 1
            else:
                last_date = gam.last_practice_date.date() if gam.last_practice_date else None
                if last_date is None:
                    gam.current_streak = 1
                elif last_date == today_date:
                    pass
                elif (today_date - last_date).days == 1:
                    gam.current_streak += 1
                else:
                    gam.current_streak = 1

                gam.points += session_xp
                gam.highest_streak = max(gam.highest_streak, gam.current_streak)
                gam.last_practice_date = now_utc
                gamification_info["current_streak"] = gam.current_streak

            # 3. Badge milestone evaluations
            existing_badges_res = await self._db.execute(
                select(UserBadge.badge_key).where(UserBadge.user_id == session.user_id)
            )
            existing_badge_keys = set(existing_badges_res.scalars().all())

            candidate_badges = []
            if "first_step" not in existing_badge_keys:
                candidate_badges.append(("first_step", "First Conversation"))

            if gam.current_streak >= 3 and "streak_3" not in existing_badge_keys:
                candidate_badges.append(("streak_3", "3-Day Consistency"))

            if gam.current_streak >= 7 and "streak_7" not in existing_badge_keys:
                candidate_badges.append(("streak_7", "Weekly Champion"))

            if summary["avg_grammar_score"] >= 85 and "grammar_master" not in existing_badge_keys:
                candidate_badges.append(("grammar_master", "Grammar Ace"))

            if summary["avg_fluency_score"] >= 85 and "fluency_star" not in existing_badge_keys:
                candidate_badges.append(("fluency_star", "Fluency Star"))

            if cefr_result in ("B2", "C1", "C2") and "cefr_b2_achieved" not in existing_badge_keys:
                candidate_badges.append(("cefr_b2_achieved", "B2 Level Mastery"))

            for key, title in candidate_badges:
                self._db.add(UserBadge(user_id=session.user_id, badge_key=key, badge_title=title))
                gamification_info["unlocked_badges"].append(title)

            # 4. System Log Analytics record for research tracking
            duration_sec = 0
            if session.created_at:
                s_created = session.created_at.replace(tzinfo=timezone.utc) if session.created_at.tzinfo is None else session.created_at
                duration_sec = max(int((now_utc - s_created).total_seconds()), 1)

            analytics_log = SystemLogAnalytics(
                user_id=session.user_id,
                session_id=session.id,
                event_type="session_complete",
                duration_seconds=duration_sec,
                turns_count=summary["total_turns"],
                extra_meta={
                    "overall_score": overall,
                    "cefr_result": cefr_result,
                    "topic": session.topic,
                    "xp_earned": session_xp,
                    "unlocked_badges": gamification_info["unlocked_badges"],
                },
            )
            self._db.add(analytics_log)

        await self._db.flush()

        updated_session = await self.get_session(session_id)
        if updated_session:
            setattr(updated_session, "gamification_info", gamification_info)
        return updated_session

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
        if role == "user" and input_type == "voice":
            try:
                audio_log = SystemLogAnalytics(
                    session_id=uuid.UUID(session_id),
                    event_type="audio_turn",
                    duration_seconds=0,
                    turns_count=0,
                    extra_meta={"transcript_length": len(transcript or "")},
                )
                self._db.add(audio_log)
            except Exception:
                pass
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

    async def get_user_session_stats(self, user_id: Optional[str] = None) -> dict:
        """
        Aggregate full history metrics for a specific user across all completed sessions.
        Strictly isolated to user_id; returns zeroed stats if user_id is empty or invalid.
        """
        if not user_id:
            return {
                "total_sessions": 0,
                "avg_overall_score": 0.0,
                "avg_grammar_score": 0.0,
                "avg_vocabulary_score": 0.0,
                "avg_fluency_score": 0.0,
            }
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            return {
                "total_sessions": 0,
                "avg_overall_score": 0.0,
                "avg_grammar_score": 0.0,
                "avg_vocabulary_score": 0.0,
                "avg_fluency_score": 0.0,
            }

        query = select(
            func.count(DBSession.id),
            func.avg(DBSession.overall_score),
            func.avg(DBSession.avg_grammar_score),
            func.avg(DBSession.avg_vocabulary_score),
            func.avg(DBSession.avg_fluency_score),
        ).where(
            DBSession.user_id == user_uuid,
            DBSession.is_active == False,  # noqa: E712
        )
        result = await self._db.execute(query)
        row = result.first()
        if not row or not row[0]:
            return {
                "total_sessions": 0,
                "avg_overall_score": 0.0,
                "avg_grammar_score": 0.0,
                "avg_vocabulary_score": 0.0,
                "avg_fluency_score": 0.0,
            }

        count, avg_overall, avg_grammar, avg_vocab, avg_fluency = row
        return {
            "total_sessions": int(count or 0),
            "avg_overall_score": round(float(avg_overall or 0.0), 1),
            "avg_grammar_score": round(float(avg_grammar or 0.0), 1),
            "avg_vocabulary_score": round(float(avg_vocab or 0.0), 1),
            "avg_fluency_score": round(float(avg_fluency or 0.0), 1),
        }

    async def get_recent_sessions(self, limit: int = 10, user_id: Optional[str] = None) -> list[DBSession]:
        """
        Get recent completed sessions strictly for a given user.
        If user_id is not provided or invalid, returns an empty list to prevent cross-user leakage.
        """
        if not user_id:
            return []
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            return []

        query = (
            select(DBSession)
            .where(
                DBSession.user_id == user_uuid,
                DBSession.is_active == False,  # noqa: E712
            )
            .order_by(DBSession.ended_at.desc())
            .limit(limit)
        )
        result = await self._db.execute(query)
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
