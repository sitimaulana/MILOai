"""
MILO AI Backend - Pydantic Schemas

Request/Response models for all API endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ─── Correction Item ──────────────────────────────────────────────────────────

class GrammarCorrection(BaseModel):
    original: str = Field(..., description="Original user text with error")
    corrected: str = Field(..., description="Corrected version")
    explanation: str = Field(..., description="Brief explanation in simple English")
    error_type: str = Field(..., description="Type: grammar / vocabulary / fluency")


# ─── Feedback ─────────────────────────────────────────────────────────────────

class FeedbackResponse(BaseModel):
    grammar_score: float = Field(..., ge=0, le=100, description="Grammar accuracy score 0–100")
    vocabulary_score: float = Field(..., ge=0, le=100, description="Vocabulary richness score 0–100")
    fluency_score: float = Field(..., ge=0, le=100, description="Fluency score 0–100")
    corrections: list[GrammarCorrection] = Field(default_factory=list)
    positive_note: str = Field(..., description="Encouraging note about what was done well")
    tip: str = Field(..., description="One actionable improvement tip")
    grammar_tip: Optional[str] = Field(None, description="Actionable tip specific to grammar")
    vocabulary_tip: Optional[str] = Field(None, description="Actionable tip specific to vocabulary")
    fluency_tip: Optional[str] = Field(None, description="Actionable tip specific to fluency")


# ─── Chat Endpoint ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Existing session ID. Leave null to create new.")
    user_id: Optional[str] = Field(None, description="Optional user ID for progress tracking.")
    message: str = Field(..., min_length=1, max_length=2000, description="User text message")
    learning_goal: Optional[str] = Field(None, description="e.g. 'Practice job interview English'")
    cefr_level: str = Field("B1", description="Target CEFR level: A2, B1, B2")
    return_audio: bool = Field(True, description="Whether to return TTS audio in response")
    input_type: Optional[str] = Field("text", description="Input type: 'text' or 'voice'")
    transcript: Optional[str] = Field(None, description="Transcript text if from voice audio")
    is_closing: Optional[bool] = Field(False, description="Whether this turn concludes the session due to time limit")
    trigger: Optional[str] = Field(None, description="Optional trigger reason, e.g. 'time_limit_reached'")


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    response_text: str = Field(..., description="MILO's text response")
    translation: Optional[str] = Field(None, description="Indonesian translation of MILO's response")
    audio_base64: Optional[str] = Field(None, description="Base64-encoded MP3 audio of response")
    feedback: Optional[FeedbackResponse] = None
    rag_sources: list[str] = Field(default_factory=list, description="Source CEFR material chunks used")
    rag_details: list[dict] = Field(default_factory=list, description="Detailed metadata and snippets for retrieved RAG chunks")
    avatar_emotion: Optional[str] = Field("friendly", description="Recommended avatar emotion: friendly, happy, thoughtful, supportive")
    is_session_closed: bool = Field(False, description="Whether MILO has delivered the closing turn")


# ─── Voice Endpoint ───────────────────────────────────────────────────────────

class VoiceResponse(BaseModel):
    session_id: str
    message_id: str
    transcript: str = Field(..., description="Whisper transcription of user's audio")
    response_text: str = Field(..., description="MILO's text response")
    translation: Optional[str] = Field(None, description="Indonesian translation of MILO's response")
    audio_base64: Optional[str] = Field(None, description="Base64-encoded MP3 audio of response")
    feedback: Optional[FeedbackResponse] = None
    rag_sources: list[str] = Field(default_factory=list)
    rag_details: list[dict] = Field(default_factory=list, description="Detailed metadata and snippets for retrieved RAG chunks")
    avatar_emotion: Optional[str] = Field("friendly", description="Recommended avatar emotion: friendly, happy, thoughtful, supportive")
    is_session_closed: bool = Field(False, description="Whether MILO has delivered the closing turn")


# ─── Translation Endpoint ─────────────────────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str = Field(..., description="English text to translate to Indonesian")


class TranslateResponse(BaseModel):
    text: str
    translation: str


# ─── Session Management ──────────────────────────────────────────────────────

class SessionStartRequest(BaseModel):
    """Request to start a new practice session."""
    cefr_level: str = Field("B1", description="CEFR level: B1, B2")
    topic: str = Field(..., description="Topic: job_interview, academic_discussion, daily_conversation")
    topic_id: Optional[str] = Field(None, description="Specific microlearning topic ID (e.g. A1, B2, C3)")
    daily_goal: Optional[str] = Field("5_min", description="Daily goal: 3_min, 5_min, 15_min")
    user_id: Optional[str] = Field(None, description="Optional user ID")


class SessionStartResponse(BaseModel):
    """Response after creating a new session."""
    session_id: str
    cefr_level: str
    topic: str
    topic_id: Optional[str] = None
    topic_title: Optional[str] = None
    topic_label: str
    daily_goal: Optional[str] = "5_min"
    greeting: str = Field(..., description="MILO's opening message for this topic")
    greeting_translation: Optional[str] = Field(None, description="Indonesian translation of opening message")
    audio_base64: Optional[str] = None


class SessionEndRequest(BaseModel):
    """Request to end a session."""
    session_id: str


class SessionEndResponse(BaseModel):
    """Response with session summary after ending."""
    session_id: str
    total_turns: int
    avg_grammar_score: float
    avg_vocabulary_score: float
    avg_fluency_score: float
    overall_score: float
    cefr_target: str
    cefr_result: str
    cefr_achieved: bool
    session_summary: str
    all_corrections: list[GrammarCorrection] = Field(default_factory=list)
    top_mistakes: list[str] = Field(default_factory=list)
    improvement_areas: list[str] = Field(default_factory=list)
    topic: str
    topic_label: str
    duration_minutes: float = 0.0
    daily_goal: Optional[str] = "15_min"
    target_duration_minutes: Optional[int] = 15
    xp_earned: int = 0
    current_streak: int = 0
    unlocked_badges: list[str] = Field(default_factory=list)
    transcript_history: list[dict] = Field(default_factory=list)


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardSessionItem(BaseModel):
    session_id: str
    topic: str
    topic_label: str
    cefr_level: str
    cefr_result: Optional[str] = None
    overall_score: Optional[float] = None
    created_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: float = 0.0


class UserBadgeItem(BaseModel):
    badge_key: str
    badge_title: str
    earned_at: datetime


class UserGamificationStats(BaseModel):
    points: int = 0
    current_streak: int = 0
    highest_streak: int = 0
    last_practice_date: Optional[datetime] = None
    badges: list[UserBadgeItem] = Field(default_factory=list)


class SkillProgressItem(BaseModel):
    skill: str
    score: float
    sessions_count: int
    total_corrections: int
    last_updated: Optional[datetime] = None


class DashboardResponse(BaseModel):
    total_sessions: int
    avg_overall_score: float
    recent_sessions: list[DashboardSessionItem]
    skill_averages: dict
    gamification: Optional[UserGamificationStats] = None
    skill_progress: list[SkillProgressItem] = Field(default_factory=list)
    user_profile: Optional[dict] = None


class SurveySubmitRequest(BaseModel):
    session_id: Optional[str] = None
    behavioral_score: float = Field(..., ge=1.0, le=5.0)
    emotional_score: float = Field(..., ge=1.0, le=5.0)
    cognitive_score: float = Field(..., ge=1.0, le=5.0)
    survey_responses: Optional[dict] = None
    ueq_scores: Optional[dict] = None
    feedback_text: Optional[str] = None


class SurveySubmitResponse(BaseModel):
    status: str = "ok"
    bonus_xp: int = 30
    message: str


# ─── Feedback Summary Schema ──────────────────────────────────────────────────

class SessionFeedbackResponse(BaseModel):
    session_id: str
    total_turns: int
    avg_grammar_score: float
    avg_vocabulary_score: float
    avg_fluency_score: float
    overall_score: float = 0.0
    cefr_target: str = "B1"
    cefr_result: str = "B1"
    cefr_achieved: bool = True
    session_summary: str = Field(..., description="AI-generated summary of the conversation")
    all_corrections: list[GrammarCorrection] = Field(default_factory=list)
    top_mistakes: list[str] = Field(default_factory=list)
    improvement_areas: list[str] = Field(default_factory=list)
    topic: str = "daily_conversation"
    topic_label: str = "Daily Conversation"
    duration_minutes: float = 0.0
    daily_goal: Optional[str] = "15_min"
    target_duration_minutes: Optional[int] = 15
    created_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    transcript_history: list[dict] = Field(default_factory=list)


class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = None
    learning_goal: Optional[str] = None
    topic: Optional[str] = None
    cefr_level: str = "B1"


class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    learning_goal: Optional[str]
    cefr_level: str
    message_count: int


# ─── Health Check ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    whisper_loaded: bool
    chroma_ready: bool
    db_connected: bool


# Auth Schemas

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: Optional[str] = Field(None, max_length=255, description="User email address")
    password: str = Field(..., min_length=6, max_length=128, description="User password")
    full_name: Optional[str] = Field(None, max_length=150, description="Full name or display name")
    cefr_level: Optional[str] = Field("B1", description="Initial CEFR level: A1, A2, B1, B2, C1")


class UserLoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=1, description="Password")


class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    cefr_level: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileResponse


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    email: Optional[str] = Field(None, max_length=255)
    cefr_level: Optional[str] = Field(None, description="Updated CEFR level")

