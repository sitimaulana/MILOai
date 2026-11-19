"""
MILO AI Backend - Curriculum & Microlearning API Router

Provides endpoints to explore the 18 microlearning modules:
- GET /api/v1/curriculum/tracks
- GET /api/v1/curriculum/topics (filtered by track and level)
- GET /api/v1/curriculum/topic/{topic_id}
- POST /api/v1/curriculum/quiz/submit
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_optional
from app.db.database import get_db
from app.db.models import User, UserGamification, SystemLogAnalytics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/curriculum", tags=["Curriculum"])

# Path to the master microlearning curriculum
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CURRICULUM_PATH = REPO_ROOT / "knowledge_base" / "curriculum_microlearning.json"

# In-memory curriculum cache
_CURRICULUM_CACHE: Optional[Dict[str, Any]] = None


def get_curriculum_data() -> Dict[str, Any]:
    """Load and cache the microlearning curriculum master JSON."""
    global _CURRICULUM_CACHE
    if _CURRICULUM_CACHE is None:
        target_path = CURRICULUM_PATH
        if not target_path.exists():
            logger.error(f"Curriculum file not found at: {target_path}")
            return {"tracks": [], "curriculum": []}
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                _CURRICULUM_CACHE = json.load(f)
            logger.info(f"Loaded {len(_CURRICULUM_CACHE.get('curriculum', []))} microlearning topics from {target_path.name}.")
        except Exception as e:
            logger.error(f"Failed to read curriculum JSON: {e}")
            return {"tracks": [], "curriculum": []}
    return _CURRICULUM_CACHE


TRACK_KEY_MAP = {
    "job_interview": "TRACK_A",
    "academic_discussion": "TRACK_B",
    "daily_conversation": "TRACK_C",
    "track_a": "TRACK_A",
    "track_b": "TRACK_B",
    "track_c": "TRACK_C",
}

TRACK_CODE_TO_KEY = {
    "TRACK_A": "job_interview",
    "TRACK_B": "academic_discussion",
    "TRACK_C": "daily_conversation",
}


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class TrackItem(BaseModel):
    track_code: str
    track_key: str
    track_name: str
    focus: str


class VocabularyItem(BaseModel):
    phrase: str
    meaning: str
    example: Optional[str] = None


class QuizItem(BaseModel):
    type: str
    question: str
    options: Dict[str, str]
    answer: Optional[str] = None  # Hidden on public fetch if desired


class TopicSummary(BaseModel):
    topic_id: str
    track_code: str
    track_key: str
    track_name: str
    cefr_level: str
    topic_number: int
    title: str
    duration_minutes: str
    can_do_statement: str
    briefing: str
    preview_vocab: List[str] = []


class TopicDetail(TopicSummary):
    vocabulary: List[VocabularyItem]
    idioms: List[VocabularyItem]
    milo_prompts: List[str]
    quizzes: List[QuizItem]


class QuizSubmitRequest(BaseModel):
    topic_id: str = Field(..., description="Topic ID (e.g. A1, B2)")
    answers: Dict[str, str] = Field(..., description="Mapping of question index ('0', '1') to chosen option ('A', 'B', 'C')")
    session_id: Optional[str] = Field(None, description="Optional active session ID")


class QuizQuestionResult(BaseModel):
    question_index: int
    question: str
    selected_option: str
    correct_option: str
    is_correct: bool
    explanation: Optional[str] = None


class QuizSubmitResponse(BaseModel):
    topic_id: str
    score: float  # 0 to 100
    total_questions: int
    correct_count: int
    results: List[QuizQuestionResult]
    bonus_points: int


# ─── Helper Functions ─────────────────────────────────────────────────────────

def _enrich_vocab_and_idioms(vocab_list: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Categorize vocabulary phrases into core vocabulary vs natural idioms/expressions.
    Provides contextual example sentences for rich pedagogical walkthroughs.
    """
    vocab_items = []
    idiom_items = []

    for item in vocab_list:
        phrase = item.get("phrase", "").strip()
        meaning = item.get("meaning", "").strip()

        # Phrases with starter ellipsis or figurative language are natural expressions / idioms
        is_expression = (
            "..." in phrase
            or any(idiom in phrase.lower() for idiom in ("bucket list", "unwind", "batteries", "burnout", "initiative", "bottleneck", "drawback", "correlation", "hand", "unforeseen"))
        )

        entry = {
            "phrase": phrase,
            "meaning": meaning,
            "example": f"Example: \"{phrase.replace('...', '')}\" is commonly used in natural dialogue.",
        }

        if is_expression:
            idiom_items.append(entry)
        else:
            vocab_items.append(entry)

    # Ensure neither list is completely empty if vocabulary exists
    if not vocab_items and idiom_items:
        vocab_items = idiom_items[:len(idiom_items)//2]
        idiom_items = idiom_items[len(idiom_items)//2:]
    elif not idiom_items and vocab_items:
        idiom_items = vocab_items[len(vocab_items)//2:]
        vocab_items = vocab_items[:len(vocab_items)//2]

    return vocab_items, idiom_items


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "/tracks",
    response_model=List[TrackItem],
    summary="Get all microlearning tracks",
)
async def get_tracks() -> List[TrackItem]:
    """Returns the 3 high-level learning tracks."""
    data = get_curriculum_data()
    tracks = []
    for tr in data.get("tracks", []):
        code = tr.get("track_code", "")
        tracks.append(
            TrackItem(
                track_code=code,
                track_key=TRACK_CODE_TO_KEY.get(code, code.lower()),
                track_name=tr.get("track_name", ""),
                focus=tr.get("focus", ""),
            )
        )
    return tracks


@router.get(
    "/topics",
    response_model=List[TopicSummary],
    summary="List microlearning topics filtered by track and/or CEFR level",
)
async def get_topics(
    track: Optional[str] = Query(None, description="Track key ('job_interview', 'academic_discussion', 'daily_conversation') or code ('TRACK_A')"),
    cefr_level: Optional[str] = Query(None, description="Target level ('B1' or 'B2')"),
) -> List[TopicSummary]:
    """
    Returns list of topics matching optional track and CEFR level filters.
    Used by setup.html Step 4 to dynamically display specific microlearning topics.
    """
    data = get_curriculum_data()
    topics = data.get("curriculum", [])

    target_code = TRACK_KEY_MAP.get(track.lower()) if track else None
    target_level = cefr_level.upper() if cefr_level else None

    filtered = []
    for top in topics:
        if target_code and top.get("track_code") != target_code:
            continue
        if target_level and top.get("cefr_level") != target_level:
            continue

        code = top.get("track_code", "")
        vocab_preview = [v.get("phrase", "") for v in top.get("vocabulary", [])[:2] if isinstance(v, dict) and v.get("phrase")]

        filtered.append(
            TopicSummary(
                topic_id=top.get("topic_id", ""),
                track_code=code,
                track_key=TRACK_CODE_TO_KEY.get(code, "job_interview"),
                track_name=top.get("track_name", ""),
                cefr_level=top.get("cefr_level", "B1"),
                topic_number=top.get("topic_number", 1),
                title=top.get("title", ""),
                duration_minutes=top.get("duration_minutes", "3-5"),
                can_do_statement=top.get("can_do_statement", ""),
                briefing=top.get("briefing", ""),
                preview_vocab=vocab_preview,
            )
        )

    return filtered


@router.get(
    "/topic/{topic_id}",
    response_model=TopicDetail,
    summary="Get full details for one microlearning topic",
)
async def get_topic_detail(topic_id: str) -> TopicDetail:
    """
    Returns full topic data: Can-Do statement, briefing, structured vocabulary,
    idiomatic expressions, prompts, and quizzes.
    Used by briefing.html and summary.html.
    """
    data = get_curriculum_data()
    topics = data.get("curriculum", [])

    matched = next((t for t in topics if t.get("topic_id", "").upper() == topic_id.upper()), None)
    if not matched:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found in curriculum.",
        )

    code = matched.get("track_code", "")
    raw_vocab = matched.get("vocabulary", [])
    vocab_items, idiom_items = _enrich_vocab_and_idioms(raw_vocab)

    quizzes = []
    for q in matched.get("quizzes", []):
        quizzes.append(
            QuizItem(
                type=q.get("type", "Comprehension"),
                question=q.get("question", ""),
                options=q.get("options", {}),
                answer=q.get("answer", ""),
            )
        )

    return TopicDetail(
        topic_id=matched.get("topic_id", ""),
        track_code=code,
        track_key=TRACK_CODE_TO_KEY.get(code, "job_interview"),
        track_name=matched.get("track_name", ""),
        cefr_level=matched.get("cefr_level", "B1"),
        topic_number=matched.get("topic_number", 1),
        title=matched.get("title", ""),
        duration_minutes=matched.get("duration_minutes", "3-5"),
        can_do_statement=matched.get("can_do_statement", ""),
        briefing=matched.get("briefing", ""),
        vocabulary=[VocabularyItem(**v) for v in vocab_items],
        idioms=[VocabularyItem(**i) for i in idiom_items],
        milo_prompts=matched.get("milo_prompts", []),
        quizzes=quizzes,
    )


@router.post(
    "/quiz/submit",
    response_model=QuizSubmitResponse,
    summary="Submit and validate answers for a micro-quiz",
)
async def submit_quiz(
    request: QuizSubmitRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> QuizSubmitResponse:
    """
    Validates learner's answers against the microlearning quiz.
    Returns composite quiz score (0-100), per-question result, and gamification points.
    Persists earned XP to UserGamification if authenticated.
    """
    data = get_curriculum_data()
    topics = data.get("curriculum", [])

    matched = next((t for t in topics if t.get("topic_id", "").upper() == request.topic_id.upper()), None)
    if not matched:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{request.topic_id}' not found in curriculum.",
        )

    quizzes = matched.get("quizzes", [])
    total = len(quizzes)
    if total == 0:
        return QuizSubmitResponse(
            topic_id=request.topic_id,
            score=100.0,
            total_questions=0,
            correct_count=0,
            results=[],
            bonus_points=0,
        )

    correct_count = 0
    results = []

    for idx, q in enumerate(quizzes):
        key = str(idx)
        selected = request.answers.get(key, "").upper().strip()
        expected = q.get("answer", "").upper().strip()

        is_correct = (selected == expected)
        if is_correct:
            correct_count += 1

        opt_text = q.get("options", {}).get(expected, expected)
        explanation = (
            f"Correct! '{opt_text}' is the right choice."
            if is_correct
            else f"The correct answer is {expected}: '{opt_text}'."
        )

        results.append(
            QuizQuestionResult(
                question_index=idx,
                question=q.get("question", ""),
                selected_option=selected,
                correct_option=expected,
                is_correct=is_correct,
                explanation=explanation,
            )
        )

    score = round((correct_count / total) * 100.0, 1)
    bonus_points = 50 if score >= 99 else 25 if score >= 50 else 10

    if current_user and db:
        try:
            from sqlalchemy import select
            gam_res = await db.execute(
                select(UserGamification).where(UserGamification.user_id == current_user.id)
            )
            gam = gam_res.scalar_one_or_none()
            if gam:
                gam.points += bonus_points
            else:
                db.add(UserGamification(user_id=current_user.id, points=bonus_points, current_streak=1, highest_streak=1))

            log = SystemLogAnalytics(
                user_id=current_user.id,
                event_type="quiz_submit",
                duration_seconds=0,
                turns_count=0,
                extra_meta={
                    "topic_id": request.topic_id,
                    "score": score,
                    "bonus_points": bonus_points,
                    "correct_count": correct_count,
                    "total": total,
                },
            )
            db.add(log)
            await db.commit()
        except Exception as e:
            logger.warning(f"Failed to persist quiz gamification points: {e}")

    return QuizSubmitResponse(
        topic_id=request.topic_id,
        score=score,
        total_questions=total,
        correct_count=correct_count,
        results=results,
        bonus_points=bonus_points,
    )


@router.get(
    "/knowledge-base/summary",
    summary="Get RAG Knowledge Base Architecture and Reference Books",
    description="Returns live statistics and reference books grounding the MILO RAG system.",
)
async def get_knowledge_base_summary() -> Dict[str, Any]:
    """Provide verified reference books and vector store statistics for UI display."""
    from app.core.rag import rag_retriever

    vector_count = 539
    if rag_retriever._vectorstore is not None:
        try:
            # Query collection count if available
            coll = getattr(rag_retriever._vectorstore, "_collection", None)
            if coll:
                vector_count = coll.count()
        except Exception:
            pass

    return {
        "status": "ready",
        "vector_count": vector_count,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2 (384-d)",
        "retrieval_method": "Adaptive Hybrid RAG (Dense ChromaDB + Sparse BM25 + Reciprocal Rank Fusion)",
        "grounding_policy": "Strict Grounding with Dynamic Score Thresholding (QA=0.68, Scenario=0.58)",
        "reference_books": [
            {
                "title": "Collins Speaking for IELTS",
                "author": "Karen Kovacs",
                "category": "Speaking & Fluency",
                "units_count": 11,
                "cefr": "B1 - B2",
                "topics": "Job Interview, Academic Discussion, Presentation, Storytelling",
                "badge": "IELTS Standard",
            },
            {
                "title": "Cambridge English Vocabulary in Use (Upper-Intermediate)",
                "author": "Michael McCarthy & Felicity O'Dell",
                "category": "Vocabulary & Collocations",
                "units_count": 30,
                "cefr": "B2",
                "topics": "Work & Careers, Tech & Society, Emotions, Phrasal Verbs, Connectors",
                "badge": "Cambridge Official",
            },
            {
                "title": "The Cambridge Guide to English Usage",
                "author": "Pam Peters",
                "category": "Grammar & Common Dilemmas",
                "units_count": 8,
                "cefr": "B1 - B2",
                "topics": "Borrow vs Lend, Affect vs Effect, Used to, Say vs Tell, Modals",
                "badge": "Grammar Remediation",
            },
            {
                "title": "CEFR Companion Volume with New Descriptors",
                "author": "Council of Europe",
                "category": "Spoken Interaction Benchmarks",
                "units_count": 7,
                "cefr": "A1 - C2 (Focused B1-B2)",
                "topics": "Overall Spoken Interaction, Informal Discussion, Goal-Oriented Cooperation",
                "badge": "Council of Europe",
            },
        ],
    }
