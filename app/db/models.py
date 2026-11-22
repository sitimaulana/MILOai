"""
MILO AI Backend - SQLAlchemy ORM Models

Tables:
  - users            : MILO user accounts
  - sessions         : Conversation sessions (with topic & mode)
  - messages         : Individual chat turns (with per-turn feedback)
  - learning_progress: Per-user skill progress tracking
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    TypeDecorator,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─── Cross-database UUID Type ─────────────────────────────────────────────────

class GUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses String(36) — works with both SQLite and PostgreSQL.
    """
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
        return value


# ─── User ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), default="")
    full_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    cefr_level: Mapped[str] = mapped_column(String(10), default="B1")
    placement_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    progress: Mapped[list["LearningProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    gamification: Mapped[Optional["UserGamification"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    badges: Mapped[list["UserBadge"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    placement_results: Mapped[list["PlacementTestResult"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", order_by="PlacementTestResult.created_at.desc()"
    )


# ─── Session ──────────────────────────────────────────────────────────────────

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[str]] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # ── Session Configuration ──
    cefr_level: Mapped[str] = mapped_column(String(10), default="B1")
    topic: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # topic values: "job_interview", "academic_discussion", "daily_conversation"
    learning_goal: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ── Session State ──
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Session Scores (computed on end) ──
    avg_grammar_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_vocabulary_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_fluency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cefr_result: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    session_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped[Optional["User"]] = relationship(back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at"
    )


# ─── Message ──────────────────────────────────────────────────────────────────

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # For voice messages: store the transcript separately
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    input_type: Mapped[str] = mapped_column(String(10), default="text")  # "text" | "voice"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Feedback data stored as JSON (grammar, vocabulary, fluency scores + corrections)
    feedback: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="messages")


# ─── Learning Progress ─────────────────────────────────────────────────────────

class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skill: Mapped[str] = mapped_column(String(50), nullable=False)  # "grammar" | "vocabulary" | "fluency"
    score: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 – 100.0
    sessions_count: Mapped[int] = mapped_column(Integer, default=0)
    total_corrections: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="progress")


# ─── Gamification & Badges ───────────────────────────────────────────────────

class UserGamification(Base):
    __tablename__ = "user_gamification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    highest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_practice_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="gamification")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    badge_key: Mapped[str] = mapped_column(String(50), nullable=False)
    badge_title: Mapped[str] = mapped_column(String(100), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="badges")


# ─── System Log Analytics (Research Logging) ──────────────────────────────────

class SystemLogAnalytics(Base):
    """Logs detailed user engagement events for Thesis Chapter 4 quantitative analysis."""
    __tablename__ = "system_log_analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        GUID(), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "session_start", "audio_turn", "session_complete", "survey_submit"
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    turns_count: Mapped[int] = mapped_column(Integer, default=0)
    extra_meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ─── Evaluation Survey (Post-Test & UEQ Responses) ────────────────────────────

class EvaluationSurvey(Base):
    """Stores Post-Test Student Engagement & UEQ survey data from 30+ respondents."""
    __tablename__ = "evaluation_surveys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        GUID(), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True
    )
    respondent_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cefr_level: Mapped[str] = mapped_column(String(10), default="B1")
    
    # 3 Student Engagement Dimensions (Likert 1-5 average)
    behavioral_score: Mapped[float] = mapped_column(Float, default=0.0)
    emotional_score: Mapped[float] = mapped_column(Float, default=0.0)
    cognitive_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_engagement_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Detailed item answers & UEQ
    survey_responses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ueq_scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    feedback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ─── Placement Test Result (CEFR B1 vs B2 Diagnostic) ─────────────────────────

class PlacementTestResult(Base):
    """Stores placement test attempts and domain competency scores for progress tracking."""
    __tablename__ = "placement_test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    total_questions: Mapped[int] = mapped_column(Integer, default=20)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    score_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    # 4 CEFR Domain Competency Scores (0.0 – 100.0)
    grammar_score: Mapped[float] = mapped_column(Float, default=0.0)
    vocabulary_score: Mapped[float] = mapped_column(Float, default=0.0)
    discourse_score: Mapped[float] = mapped_column(Float, default=0.0)
    pragmatics_score: Mapped[float] = mapped_column(Float, default=0.0)

    recommended_level: Mapped[str] = mapped_column(String(10), nullable=False)  # "B1" | "B2"
    selected_level: Mapped[str] = mapped_column(String(10), nullable=False)     # "B1" | "B2"

    # Detailed item answers & rationale
    answers_detail: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="placement_results")


