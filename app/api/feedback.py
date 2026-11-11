"""
MILO AI Backend - Session API Routes

POST /api/v1/session/start   — Start a new practice session (select topic & level)
POST /api/v1/session/end     — End session & get scores + CEFR evaluation
GET  /api/v1/dashboard       — Dashboard with recent sessions & progress
GET  /api/v1/session/{id}/feedback — Get session-level feedback summary
POST /api/v1/session         — Create a session (legacy)
GET  /api/v1/session/{id}    — Get session info (legacy)
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import generate_response
from app.core.tts import synthesize_speech
from app.db.database import get_db
from app.models.schemas import (
    DashboardResponse,
    DashboardSessionItem,
    GrammarCorrection,
    SessionCreateRequest,
    SessionEndRequest,
    SessionEndResponse,
    SessionFeedbackResponse,
    SessionInfo,
    SessionStartRequest,
    SessionStartResponse,
)
from app.services.conversation import ConversationService, TOPIC_LABELS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Session & Feedback"])

def _calc_duration_minutes(start: Optional[datetime], end: Optional[datetime]) -> float:
    """Safely calculate duration in minutes, handling naive vs aware datetimes."""
    if not start or not end:
        return 0.0
    s = start.replace(tzinfo=None) if start.tzinfo else start
    e = end.replace(tzinfo=None) if end.tzinfo else end
    diff_sec = abs((e - s).total_seconds())
    return round(max(diff_sec / 60.0, 0.1), 1)


def _extract_goal_info(learning_goal: Optional[str]) -> tuple[str, int]:
    """Extract daily goal key ('5_min', '15_min', '30_min') and target minutes."""
    if not learning_goal:
        return "15_min", 15
    lg = learning_goal.lower()
    if "5 min" in lg or "5_min" in lg:
        return "5_min", 5
    if "30 min" in lg or "30_min" in lg:
        return "30_min", 30
    return "15_min", 15


def _build_session_diagnostics(
    all_corrections: list[dict],
    grammar_score: float,
    vocab_score: float,
    fluency_score: float,
) -> tuple[list[str], list[str]]:
    """Build concrete mistakes list and actionable improvements from actual session performance."""
    top_mistakes = []
    seen = set()
    for c in all_corrections:
        orig = c.get("original", "").strip()
        corr = c.get("corrected", "").strip()
        etype = (c.get("error_type") or "grammar").capitalize()
        if orig and corr and (orig, corr) not in seen:
            seen.add((orig, corr))
            top_mistakes.append(f"{etype}: \"{orig}\" → \"{corr}\"")
        if len(top_mistakes) >= 4:
            break

    improvement_areas = []
    error_types = [(c.get("error_type") or "grammar").lower() for c in all_corrections]
    grammar_count = sum(1 for e in error_types if e == "grammar")
    vocab_count = sum(1 for e in error_types if "vocab" in e)
    fluency_count = sum(1 for e in error_types if "fluen" in e)

    if grammar_count > 0:
        improvement_areas.append(
            f"Akurasi Tata Bahasa ({grammar_count} catatan): Perhatikan bentuk tenses, subject-verb agreement, dan artikel dalam kalimat lisan."
        )
    elif grammar_score < 75:
        improvement_areas.append("Akurasi Tata Bahasa: Latih penggunaan auxiliary verbs dan bentuk kata kerja lampau secara konsisten.")

    if vocab_count > 0:
        improvement_areas.append(
            f"Pengayaan Kosakata ({vocab_count} catatan): Gunakan padanan kata spesifik dan hindari terjemahan harfiah langsung."
        )
    elif vocab_score < 75:
        improvement_areas.append("Pengayaan Kosakata: Perluas sinonim deskriptif dan terminologi kontekstual sesuai topik latihan.")

    if fluency_count > 0 or fluency_score < 75:
        improvement_areas.append(
            "Kelancaran & Struktur: Gunakan discourse markers (seperti 'Moreover', 'In my experience') untuk menyambung gagasan secara mengalir."
        )

    if not improvement_areas:
        improvement_areas.append("Pertahankan Performa: Struktur kalimat Anda sangat rapi dan alami di sepanjang sesi ini.")
        improvement_areas.append("Eksplorasi Lanjutan: Coba integrasikan kalimat kompleks dan ungkapan idiomatik untuk persiapan level berikutnya.")

    return top_mistakes, improvement_areas

# ─── Topic Greetings ──────────────────────────────────────────────────────────

TOPIC_GREETINGS = {
    "job_interview": (
        "Good morning! Thank you for coming in today. Welcome to your job interview practice session. "
        "I'll be your interviewer. Let's start — could you tell me a little bit about yourself?"
    ),
    "academic_discussion": (
        "Welcome to our academic discussion! I'm excited to have a scholarly conversation with you. "
        "Today we can discuss any academic topic you're interested in. What subject would you like to explore?"
    ),
    "daily_conversation": (
        "Hey there! Welcome to our daily conversation practice. "
        "Feel free to talk about anything — your hobbies, weekend plans, or daily life. "
        "So, how's your day going?"
    ),
}

LEVEL_ADAPTED_GREETINGS = {
    "A1": {
        "job_interview": "Hello! Welcome to your job interview practice. I am Milo. Let's start simple — what is your name and what job do you like?",
        "academic_discussion": "Hello! Welcome to our study chat. What school subject or topic do you like to learn?",
        "daily_conversation": "Hi there! Welcome to English practice. How are you today? What do you like to do in your free time?",
    },
    "A2": {
        "job_interview": "Hello and welcome! Thank you for coming today. I am Milo, your interviewer. To begin, could you tell me a little bit about yourself?",
        "academic_discussion": "Welcome! I am excited to talk with you today. What topic or subject would you like to discuss?",
        "daily_conversation": "Hey there! Welcome to our daily practice. How was your day today? Did you do anything fun or interesting?",
    },
    "B1": {
        "job_interview": "Good morning! Thank you for coming in today. Welcome to your job interview practice session. I'll be your interviewer. Let's start — could you tell me a little bit about yourself?",
        "academic_discussion": "Welcome to our academic discussion! I'm excited to have a scholarly conversation with you. Today we can discuss any academic topic you're interested in. What subject would you like to explore?",
        "daily_conversation": "Hey there! Welcome to our daily conversation practice. Feel free to talk about anything — your hobbies, weekend plans, or daily life. So, how's your day going?",
    },
    "B2": {
        "job_interview": "Good morning and welcome to your professional interview practice. I'll be conducting your interview today. To kick things off, could you walk me through your background and what motivated you to pursue this path?",
        "academic_discussion": "Welcome to our academic discussion! Today we can explore complex concepts, debate perspectives, or analyze current trends. What particular academic field or issue would you like to focus on?",
        "daily_conversation": "Hey, great to connect with you! I'm ready to dive into some spontaneous English conversation today. What's been on your mind lately, or what exciting projects have you been working on?",
    },
    "C1": {
        "job_interview": "Good day, and thank you for taking the time to meet with me. Let's delve right into our discussion — could you provide a comprehensive overview of your professional trajectory and the core competencies you bring to the table?",
        "academic_discussion": "Welcome to today's scholarly exchange. I look forward to an analytical discourse with you. Which theoretical framework, research inquiry, or critical discourse would you like to examine?",
        "daily_conversation": "Delighted to speak with you today! Let's engage in an open, nuanced conversation. What fascinating ideas, cultural insights, or current affairs have captured your curiosity recently?",
    },
}

LEVEL_ADAPTED_GREETINGS_ID = {
    "B1": {
        "job_interview": "Selamat pagi! Terima kasih sudah datang hari ini. Selamat datang di sesi latihan wawancara kerjamu. Saya akan menjadi pewawancaramu. Mari kita mulai — bisakah kamu menceritakan sedikit tentang dirimu?",
        "academic_discussion": "Selamat datang di diskusi akademik kita! Saya sangat antusias untuk berdiskusi ilmiah denganmu. Hari ini kita bisa membahas topik akademis apa pun yang menarik minatmu. Subjek apa yang ingin kamu jelajahi?",
        "daily_conversation": "Halo! Selamat datang di sesi latihan percakapan sehari-hari. Jangan ragu mengobrol tentang apa saja — hobimu, rencana akhir pekan, atau kehidupan sehari-hari. Jadi, bagaimana harimu hari ini?",
    },
    "B2": {
        "job_interview": "Selamat pagi dan selamat datang di latihan wawancara profesionalmu. Saya akan memandu wawancaramu hari ini. Sebagai pembuka, bisakah kamu menjabarkan latar belakangmu dan apa yang memotivasimu mengejar jalur karier ini?",
        "academic_discussion": "Selamat datang di diskusi akademik kita! Hari ini kita bisa menjelajahi konsep-konsep mendalam, memperdebatkan berbagai sudut pandang, atau menganalisis tren terkini. Bidang akademis atau isu spesifik apa yang ingin kamu fokuskan?",
        "daily_conversation": "Hai, senang bisa terhubung denganmu! Saya siap berdiskusi secara santai dan spontan hari ini. Hal apa yang sedang menarik perhatianmu belakangan ini, atau proyek seru apa yang sedang kamu kerjakan?",
    },
}

TOPIC_GOALS = {
    "job_interview": "Practice professional English for job interviews. Focus on formal language, clear self-presentation, and confident responses.",
    "academic_discussion": "Practice academic English for discussions, presentations, and debates. Focus on expressing complex ideas clearly.",
    "daily_conversation": "Practice everyday English for social situations. Focus on natural, fluent conversation and common expressions.",
}


# ─── Start Session ────────────────────────────────────────────────────────────

@router.post(
    "/session/start",
    response_model=SessionStartResponse,
    summary="Start a new practice session",
    status_code=status.HTTP_201_CREATED,
)
async def start_session(
    request: SessionStartRequest,
    db: AsyncSession = Depends(get_db),
) -> SessionStartResponse:
    """
    Create a new practice session with selected topic, daily goal, and CEFR level.
    Returns MILO's greeting message adapted to the user's level and chosen topic.
    """
    topic = request.topic
    if topic not in TOPIC_GREETINGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid topic '{topic}'. Must be one of: {', '.join(TOPIC_GREETINGS.keys())}",
        )

    conv = ConversationService(db)
    goal_base = TOPIC_GOALS.get(topic, "")
    daily_goal_str = request.daily_goal or "15_min"
    daily_goal_label = "15 min/day" if daily_goal_str == "15_min" else "5 min/day" if daily_goal_str == "5_min" else "30 min/day"
    learning_goal = f"{goal_base} Target: {daily_goal_label}. Level: {request.cefr_level}."

    session = await conv.create_session(
        user_id=request.user_id,
        learning_goal=learning_goal,
        topic=topic,
        cefr_level=request.cefr_level,
    )

    level_dict = LEVEL_ADAPTED_GREETINGS.get(request.cefr_level, LEVEL_ADAPTED_GREETINGS["B1"])
    greeting = level_dict.get(topic, TOPIC_GREETINGS[topic])

    level_dict_id = LEVEL_ADAPTED_GREETINGS_ID.get(request.cefr_level, LEVEL_ADAPTED_GREETINGS_ID["B1"])
    greeting_translation = level_dict_id.get(topic, "Selamat datang di sesi latihan MILO!")

    # Save the greeting as the first assistant message
    await conv.add_message(
        session_id=str(session.id),
        role="assistant",
        content=greeting,
        input_type="text",
    )

    # Generate TTS for the greeting
    audio_base64 = None
    try:
        audio_base64 = await synthesize_speech(greeting)
    except Exception as e:
        logger.warning(f"TTS failed for greeting: {e}")

    return SessionStartResponse(
        session_id=str(session.id),
        cefr_level=request.cefr_level,
        topic=topic,
        topic_label=TOPIC_LABELS.get(topic, topic),
        daily_goal=daily_goal_str,
        greeting=greeting,
        greeting_translation=greeting_translation,
        audio_base64=audio_base64,
    )


# ─── End Session ──────────────────────────────────────────────────────────────

@router.post(
    "/session/end",
    response_model=SessionEndResponse,
    summary="End session and get scores",
)
async def end_session(
    request: SessionEndRequest,
    db: AsyncSession = Depends(get_db),
) -> SessionEndResponse:
    """
    End a practice session:
    1. Compute average scores (Grammar, Vocabulary, Fluency)
    2. Map overall score → CEFR level
    3. Generate AI session summary referencing actual speech performance
    4. Return comprehensive results and transcript documentation
    """
    conv = ConversationService(db)

    session = await conv.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{request.session_id}' not found.",
        )

    session = await conv.end_session(request.session_id)
    summary_data = await conv.get_session_feedback_summary(request.session_id)
    all_corrections = summary_data.get("all_corrections", [])

    duration_minutes = _calc_duration_minutes(session.created_at, session.ended_at)
    daily_goal_key, target_duration = _extract_goal_info(session.learning_goal)

    history = await conv.get_history(request.session_id, max_turns=60)
    session_summary = await _generate_session_summary(
        history=history,
        all_corrections=all_corrections,
        avg_grammar=session.avg_grammar_score or 0.0,
        avg_vocab=session.avg_vocabulary_score or 0.0,
        avg_fluency=session.avg_fluency_score or 0.0,
        overall_score=session.overall_score or 0.0,
        cefr_target=session.cefr_level or "B1",
        cefr_result=session.cefr_result or "A1",
        topic=session.topic or "",
        duration_minutes=duration_minutes,
    )

    from sqlalchemy import update as sa_update
    from app.db.models import Session as DBSession
    import uuid
    await db.execute(
        sa_update(DBSession)
        .where(DBSession.id == uuid.UUID(request.session_id))
        .values(session_summary=session_summary)
    )

    top_mistakes, improvement_areas = _build_session_diagnostics(
        all_corrections=all_corrections,
        grammar_score=session.avg_grammar_score or 0.0,
        vocab_score=session.avg_vocabulary_score or 0.0,
        fluency_score=session.avg_fluency_score or 0.0,
    )

    topic = session.topic or "daily_conversation"
    transcript_messages = await conv.get_session_messages(request.session_id)

    return SessionEndResponse(
        session_id=request.session_id,
        total_turns=summary_data["total_turns"],
        avg_grammar_score=session.avg_grammar_score or 0.0,
        avg_vocabulary_score=session.avg_vocabulary_score or 0.0,
        avg_fluency_score=session.avg_fluency_score or 0.0,
        overall_score=session.overall_score or 0.0,
        cefr_target=session.cefr_level or "B1",
        cefr_result=session.cefr_result or "A1",
        cefr_achieved=(session.cefr_result or "A1") >= (session.cefr_level or "B1"),
        session_summary=session_summary,
        all_corrections=[
            GrammarCorrection(
                original=c.get("original", ""),
                corrected=c.get("corrected", ""),
                explanation=c.get("explanation", ""),
                error_type=c.get("error_type", "grammar"),
            )
            for c in all_corrections
        ],
        top_mistakes=top_mistakes,
        improvement_areas=improvement_areas,
        topic=topic,
        topic_label=TOPIC_LABELS.get(topic, topic),
        duration_minutes=duration_minutes,
        daily_goal=daily_goal_key,
        target_duration_minutes=target_duration,
        transcript_history=transcript_messages,
    )


# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get dashboard data",
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    """Get recent sessions and aggregate statistics for the dashboard."""
    conv = ConversationService(db)
    recent = await conv.get_recent_sessions(limit=10)

    sessions_items = []
    total_score = 0.0
    score_count = 0
    grammar_sum = 0.0
    vocab_sum = 0.0
    fluency_sum = 0.0

    for s in recent:
        topic = s.topic or "daily_conversation"
        duration = _calc_duration_minutes(s.created_at, s.ended_at)

        sessions_items.append(DashboardSessionItem(
            session_id=str(s.id),
            topic=topic,
            topic_label=TOPIC_LABELS.get(topic, topic),
            cefr_level=s.cefr_level or "B1",
            cefr_result=s.cefr_result,
            overall_score=s.overall_score,
            created_at=s.created_at,
            ended_at=s.ended_at,
            duration_minutes=duration,
        ))

        if s.overall_score:
            total_score += s.overall_score
            score_count += 1
        if s.avg_grammar_score:
            grammar_sum += s.avg_grammar_score
        if s.avg_vocabulary_score:
            vocab_sum += s.avg_vocabulary_score
        if s.avg_fluency_score:
            fluency_sum += s.avg_fluency_score

    avg_score = round(total_score / max(score_count, 1), 1)

    return DashboardResponse(
        total_sessions=len(recent),
        avg_overall_score=avg_score,
        recent_sessions=sessions_items,
        skill_averages={
            "grammar": round(grammar_sum / max(score_count, 1), 1),
            "vocabulary": round(vocab_sum / max(score_count, 1), 1),
            "fluency": round(fluency_sum / max(score_count, 1), 1),
        },
    )


# ─── Legacy Endpoints ─────────────────────────────────────────────────────────

@router.post(
    "/session",
    response_model=SessionInfo,
    summary="Create a new conversation session",
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    request: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> SessionInfo:
    """Pre-create a session before starting a conversation."""
    conv = ConversationService(db)
    session = await conv.create_session(
        user_id=request.user_id,
        learning_goal=request.learning_goal,
        topic=request.topic,
        cefr_level=request.cefr_level,
    )
    count = await conv.get_message_count(str(session.id))
    return SessionInfo(
        session_id=str(session.id),
        created_at=session.created_at,
        learning_goal=session.learning_goal,
        cefr_level=session.cefr_level,
        message_count=count,
    )


@router.get(
    "/session/{session_id}",
    response_model=SessionInfo,
    summary="Get session information",
)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> SessionInfo:
    """Retrieve metadata about an existing session."""
    conv = ConversationService(db)
    session = await conv.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    count = await conv.get_message_count(session_id)
    return SessionInfo(
        session_id=str(session.id),
        created_at=session.created_at,
        learning_goal=session.learning_goal,
        cefr_level=session.cefr_level,
        message_count=count,
    )


@router.get(
    "/session/{session_id}/feedback",
    response_model=SessionFeedbackResponse,
    summary="Get full feedback summary for a session",
)
async def get_session_feedback(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> SessionFeedbackResponse:
    """Compute and return a comprehensive feedback summary for a completed session."""
    conv = ConversationService(db)
    session = await conv.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    summary_data = await conv.get_session_feedback_summary(session_id)
    all_corrections = summary_data.get("all_corrections", [])

    duration_minutes = _calc_duration_minutes(
        session.created_at, session.ended_at or datetime.now(timezone.utc)
    )
    daily_goal_key, target_duration = _extract_goal_info(session.learning_goal)

    history = await conv.get_history(session_id, max_turns=60)
    session_summary = session.session_summary
    if not session_summary:
        session_summary = await _generate_session_summary(
            history=history,
            all_corrections=all_corrections,
            avg_grammar=session.avg_grammar_score or summary_data["avg_grammar_score"],
            avg_vocab=session.avg_vocabulary_score or summary_data["avg_vocabulary_score"],
            avg_fluency=session.avg_fluency_score or summary_data["avg_fluency_score"],
            overall_score=session.overall_score or 0.0,
            cefr_target=session.cefr_level or "B1",
            cefr_result=session.cefr_result or "A1",
            topic=session.topic or "",
            duration_minutes=duration_minutes,
        )

    top_mistakes, improvement_areas = _build_session_diagnostics(
        all_corrections=all_corrections,
        grammar_score=session.avg_grammar_score or summary_data["avg_grammar_score"],
        vocab_score=session.avg_vocabulary_score or summary_data["avg_vocabulary_score"],
        fluency_score=session.avg_fluency_score or summary_data["avg_fluency_score"],
    )

    topic = session.topic or "daily_conversation"
    transcript_messages = await conv.get_session_messages(session_id)

    return SessionFeedbackResponse(
        session_id=session_id,
        total_turns=summary_data["total_turns"],
        avg_grammar_score=session.avg_grammar_score or summary_data["avg_grammar_score"],
        avg_vocabulary_score=session.avg_vocabulary_score or summary_data["avg_vocabulary_score"],
        avg_fluency_score=session.avg_fluency_score or summary_data["avg_fluency_score"],
        overall_score=session.overall_score or 0.0,
        cefr_target=session.cefr_level or "B1",
        cefr_result=session.cefr_result or "A1",
        cefr_achieved=(session.cefr_result or "A1") >= (session.cefr_level or "B1"),
        session_summary=session_summary,
        all_corrections=[
            GrammarCorrection(
                original=c.get("original", ""),
                corrected=c.get("corrected", ""),
                explanation=c.get("explanation", ""),
                error_type=c.get("error_type", "grammar"),
            )
            for c in all_corrections
        ],
        top_mistakes=top_mistakes,
        improvement_areas=improvement_areas,
        topic=topic,
        topic_label=TOPIC_LABELS.get(topic, topic),
        duration_minutes=duration_minutes,
        daily_goal=daily_goal_key,
        target_duration_minutes=target_duration,
        created_at=session.created_at,
        ended_at=session.ended_at,
        transcript_history=transcript_messages,
    )


# ─── Helper ───────────────────────────────────────────────────────────────────

async def _generate_session_summary(
    history: list[dict],
    all_corrections: list[dict],
    avg_grammar: float,
    avg_vocab: float,
    avg_fluency: float,
    overall_score: float,
    cefr_target: str,
    cefr_result: str,
    topic: str,
    duration_minutes: float,
) -> str:
    """Generate an evidence-grounded AI evaluation report referencing actual user performance."""
    if not history:
        return "Belum ada rekaman percakapan yang tersedia untuk sesi ini."

    topic_label = TOPIC_LABELS.get(topic, topic or "General practice")
    user_turns = [h for h in history if h.get("role") == "user"]
    total_turns = len(user_turns)

    user_samples = [
        f"- Student said: \"{t.get('content', '')[:140]}\""
        for t in user_turns[-8:]
    ]
    sample_text = "\n".join(user_samples) if user_samples else "(No utterances recorded)"

    corr_samples = [
        f"- \"{c.get('original', '')}\" → \"{c.get('corrected', '')}\" ({c.get('explanation', '')})"
        for c in all_corrections[:6]
    ]
    corr_text = "\n".join(corr_samples) if corr_samples else "None (all recorded utterances were accurate)"

    summary_prompt = f"""\
You are an expert CEFR English evaluator and speaking coach.
Write an objective, encouraging, and well-structured evaluation report for this student's completed speaking session.
Your evaluation MUST refer directly to what the student actually spoke about and their actual performance.

Session Data:
- Topic: {topic_label}
- Target CEFR: {cefr_target} | Achieved CEFR: {cefr_result}
- Duration: {duration_minutes:.1f} minutes ({total_turns} spoken turns)
- Grammar Accuracy: {avg_grammar:.0f}/100
- Vocabulary Score: {avg_vocab:.0f}/100
- Fluency Score: {avg_fluency:.0f}/100
- Composite Score: {overall_score:.0f}/100

Representative User Utterances From This Session:
{sample_text}

Specific Errors & Corrections From This Session:
{corr_text}

Output Format Guidelines (STRICT):
- Do NOT output document titles with '#' or composite score headers (the UI already has a score gauge and title).
- Structure your response cleanly using these exact sections:

## Ringkasan Performa
<1-2 paragraphs of supportive, evidence-based narrative about what the student actually discussed in {topic_label} and how effectively they communicated.>

## Kelebihan Teramati
- **<Aspect, e.g. Kosakata / Kelancaran / Pemahaman>**: <specific strength with concrete example from their speech>
- **<Aspect>**: <another specific strength>

## Catatan Kaidah & Kosakata
<If errors occurred, list 1-2 points formatted like:
- **"original phrase"** → gunakan **"corrected phrase"** (brief explanation).
If no errors occurred, explain why their sentence structures were precise.>

## Rekomendasi Latihan Selanjutnya
<1 actionable, motivating recommendation for their next speaking session.>

Write in natural, encouraging Indonesian with English terms in quotes or bold where helpful."""

    try:
        result = await generate_response(
            user_message=summary_prompt,
            history=[],
            learning_goal="",
            cefr_level=cefr_result or cefr_target or "B1",
        )
        return result.content
    except Exception:
        return (
            f"Anda telah menyelesaikan sesi latihan {cefr_target} pada topik {topic_label} selama {duration_minutes:.1f} menit ({total_turns} putaran bicara). "
            f"Performa Anda menghasilkan skor tata bahasa {avg_grammar:.0f}/100, kosakata {avg_vocab:.0f}/100, dan kelancaran {avg_fluency:.0f}/100 dengan capaian level {cefr_result}. "
            "Terus pertahankan konsistensi latihan untuk memperkaya spontanitas dan ketepatan berbicara Anda!"
        )


# ─── Obsidian Markdown Export ────────────────────────────────────────────────

@router.get(
    "/session/{session_id}/export/obsidian",
    summary="Export session learning log as Obsidian Markdown",
    description="Generates an Obsidian-compatible Markdown note with frontmatter, callouts, and wikilinks.",
)
async def export_session_obsidian(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import Response

    conv = ConversationService(db)
    session = await conv.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    summary_data = await conv.get_session_feedback_summary(session_id)
    history = await conv.get_history(session_id, max_turns=100)

    topic_label = TOPIC_LABELS.get(session.topic or "", session.topic or "English Practice")
    created_str = session.created_at.strftime("%Y-%m-%d %H:%M") if session.created_at else "Unknown"
    date_iso = session.created_at.strftime("%Y-%m-%d") if session.created_at else "2026-10-27"

    # Frontmatter
    md = [
        "---",
        f"title: MILO Practice - {topic_label}",
        f"date: {date_iso}",
        "tags:",
        "  - milo/session",
        f"  - cefr/{session.cefr_level or 'B1'}",
        f"  - topic/{session.topic or 'general'}",
        f"grammar_score: {session.avg_grammar_score or 0:.1f}",
        f"vocabulary_score: {session.avg_vocabulary_score or 0:.1f}",
        f"fluency_score: {session.avg_fluency_score or 0:.1f}",
        f"overall_score: {session.overall_score or 0:.1f}",
        f"cefr_level: {session.cefr_result or session.cefr_level or 'B1'}",
        "---",
        "",
        f"# 🎙️ MILO Practice Session: {topic_label}",
        f"**Date**: {created_str} | **Level**: `{session.cefr_level or 'B1'}` | **Goal**: *{session.learning_goal or 'Speaking practice'}*",
        "",
        "## 📊 Assessment Scores",
        "| Metric | Score | Rating |",
        "| :--- | :--- | :--- |",
        f"| **Grammar Accuracy** | `{session.avg_grammar_score or 0:.1f}/100` | {'🟢 Solid' if (session.avg_grammar_score or 0) >= 80 else '🟡 Needs practice'} |",
        f"| **Vocabulary Richness** | `{session.avg_vocabulary_score or 0:.1f}/100` | {'🟢 Diverse' if (session.avg_vocabulary_score or 0) >= 80 else '🟡 Basic'} |",
        f"| **Fluency & Confidence** | `{session.avg_fluency_score or 0:.1f}/100` | {'🟢 Fluent' if (session.avg_fluency_score or 0) >= 80 else '🟡 Developing'} |",
        f"| **Overall CEFR Result** | **`{session.cefr_result or session.cefr_level or 'B1'}`** | `{session.overall_score or 0:.1f}/100` |",
        "",
        "> [!NOTE] Tutor Summary",
        f"> {session.session_summary or 'Great effort during this speaking practice session!'}",
        "",
        "## 🛠️ Key Corrections & Upgrades",
    ]

    all_corrections = summary_data.get("all_corrections", [])
    if all_corrections:
        for idx, c in enumerate(all_corrections[:15], 1):
            orig = c.get("original", "").strip()
            corr = c.get("corrected", "").strip()
            expl = c.get("explanation", "").strip()
            etype = c.get("error_type", "grammar")
            md.append(f"{idx}. **[{etype.upper()}]** ~~{orig}~~ ➔ **`{corr}`**")
            if expl:
                md.append(f"   - *Note*: {expl}")
    else:
        md.append("- *No major errors recorded. Outstanding accuracy!*")

    md.extend([
        "",
        "## 💬 Conversation Transcript",
        "",
    ])

    for turn in history:
        role = turn.get("role", "user")
        content = turn.get("content", "").strip()
        if role == "user":
            md.append(f"- 👤 **Learner**: {content}")
        else:
            md.append(f"- 🤖 **MILO**: {content}")

    md.extend([
        "",
        "---",
        "*Exported from AI-MILO Companion — Connected with [[00_Home_MOC|CEFR Knowledge Base]]*",
    ])

    content_str = "\n".join(md)
    filename = f"milo_session_{session_id[:8]}.md"

    return Response(
        content=content_str,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

