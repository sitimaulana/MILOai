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
    cefr_level: Mapped[str] = mapped_column(String(10), default="B1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    progress: Mapped[list["LearningProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")


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
