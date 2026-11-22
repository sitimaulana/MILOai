"""
MILO AI Backend - CEFR Placement & Diagnostic API Router

Provides standardized 20-question CEFR placement testing:
- GET  /api/v1/curriculum/placement/questions  : Get questions (answers stripped)
- POST /api/v1/curriculum/placement/submit     : Evaluate answers, compute smart recommendation, save to DB
- GET  /api/v1/curriculum/placement/history    : Retrieve user's placement test history
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_optional, get_current_user
from app.db.database import get_db
from app.db.models import User, PlacementTestResult, SystemLogAnalytics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/curriculum/placement", tags=["Placement Test"])

# Path to master placement questions JSON
QUESTIONS_PATH = Path(__file__).resolve().parent.parent.parent / "knowledge_base" / "placement_questions.json"
_QUESTIONS_CACHE: Optional[Dict[str, Any]] = None


def get_placement_data() -> Dict[str, Any]:
    """Load and cache the placement questions JSON."""
    global _QUESTIONS_CACHE
    if _QUESTIONS_CACHE is None:
        if not QUESTIONS_PATH.exists():
            logger.error(f"Placement questions file not found at: {QUESTIONS_PATH}")
            return {"title": "CEFR Placement Test", "total_questions": 0, "domains": [], "questions": []}
        try:
            with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
                _QUESTIONS_CACHE = json.load(f)
            logger.info(f"Loaded {len(_QUESTIONS_CACHE.get('questions', []))} placement questions.")
        except Exception as e:
            logger.error(f"Failed to read placement questions JSON: {e}")
            return {"title": "CEFR Placement Test", "total_questions": 0, "domains": [], "questions": []}
    return _QUESTIONS_CACHE


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class DomainInfo(BaseModel):
    key: str
    name: str
    question_count: int
    reference: str


class PublicPlacementQuestion(BaseModel):
    id: int
    domain: str
    domain_name: str
    cefr_target: str
    question: str
    options: Dict[str, str]
    reference_source: str


class PlacementQuestionsResponse(BaseModel):
    title: str
    total_questions: int
    domains: List[DomainInfo]
    questions: List[PublicPlacementQuestion]


class PlacementSubmitRequest(BaseModel):
    answers: Dict[str, str] = Field(..., description="Mapping of question ID ('1', '2') to chosen option ('A', 'B', 'C', 'D')")
    selected_level: Optional[str] = Field(None, description="Optional user final choice override ('B1' or 'B2')")


class QuestionResultDetail(BaseModel):
    id: int
    domain: str
    domain_name: str
    question: str
    selected_option: str
    correct_option: str
    is_correct: bool
    explanation: str
    reference_source: str


class DomainScore(BaseModel):
    domain_key: str
    domain_name: str
    correct_count: int
    total_count: int
    score_percentage: float


class PlacementSubmitResponse(BaseModel):
    score_percentage: float
    total_questions: int
    correct_count: int
    recommended_level: str  # "B1" or "B2"
    selected_level: str     # level applied
    level_title: str
    recommendation_summary: str
    strengths: List[str]
    growth_areas: List[str]
    domain_breakdown: List[DomainScore]
    question_results: List[QuestionResultDetail]
    saved_to_profile: bool


class PlacementHistoryItem(BaseModel):
    id: int
    created_at: datetime
    total_questions: int
    correct_count: int
    score_percentage: float
    grammar_score: float
    vocabulary_score: float
    discourse_score: float
    pragmatics_score: float
    recommended_level: str
    selected_level: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get(
    "/questions",
    response_model=PlacementQuestionsResponse,
    summary="Get 20 placement questions (answers hidden)",
)
async def get_placement_questions() -> PlacementQuestionsResponse:
    """Returns the 20 CEFR placement questions without exposing the answers."""
    data = get_placement_data()
    raw_questions = data.get("questions", [])

    public_questions: List[PublicPlacementQuestion] = []
    for q in raw_questions:
        public_questions.append(
            PublicPlacementQuestion(
                id=q["id"],
                domain=q["domain"],
                domain_name=q["domain_name"],
                cefr_target=q.get("cefr_target", "B1-B2"),
                question=q["question"],
                options=q["options"],
                reference_source=q.get("reference_source", ""),
            )
        )

    domains: List[DomainInfo] = [
        DomainInfo(**d) for d in data.get("domains", [])
    ]

    return PlacementQuestionsResponse(
        title=data.get("title", "MILO CEFR B1 vs B2 Placement Diagnostic Test"),
        total_questions=len(public_questions),
        domains=domains,
        questions=public_questions,
    )


@router.post(
    "/submit",
    response_model=PlacementSubmitResponse,
    summary="Submit placement answers and calculate smart recommendation",
)
async def submit_placement_test(
    payload: PlacementSubmitRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> PlacementSubmitResponse:
    """Grade placement test answers, produce smart recommendation, and store in DB."""
    data = get_placement_data()
    master_questions = {q["id"]: q for q in data.get("questions", [])}
    total_questions = len(master_questions)

    if total_questions == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bank soal placement belum dimuat dengan benar.",
        )

    # Evaluate answers
    correct_count = 0
    domain_stats: Dict[str, Dict[str, Any]] = {
        "grammar": {"name": "Grammar & Complex Syntax", "correct": 0, "total": 0},
        "vocabulary": {"name": "Vocabulary & Collocations", "correct": 0, "total": 0},
        "discourse": {"name": "Discourse Cohesion & Linking Markers", "correct": 0, "total": 0},
        "pragmatics": {"name": "Situational Pragmatics, Tone & Register", "correct": 0, "total": 0},
    }

    question_results: List[QuestionResultDetail] = []

    for q_id, q_data in master_questions.items():
        domain_key = q_data.get("domain", "grammar")
        if domain_key in domain_stats:
            domain_stats[domain_key]["total"] += 1

        user_answer = payload.answers.get(str(q_id), "").strip().upper()
        correct_answer = q_data.get("answer", "").strip().upper()
        is_correct = (user_answer == correct_answer)

        if is_correct:
            correct_count += 1
            if domain_key in domain_stats:
                domain_stats[domain_key]["correct"] += 1

        question_results.append(
            QuestionResultDetail(
                id=q_id,
                domain=domain_key,
                domain_name=q_data.get("domain_name", domain_key.title()),
                question=q_data["question"],
                selected_option=user_answer,
                correct_option=correct_answer,
                is_correct=is_correct,
                explanation=q_data.get("explanation", ""),
                reference_source=q_data.get("reference_source", ""),
            )
        )

    # Calculate scores
    score_percentage = round((correct_count / total_questions) * 100.0, 1)

    domain_breakdown: List[DomainScore] = []
    strengths: List[str] = []
    growth_areas: List[str] = []

    for d_key, d_val in domain_stats.items():
        c = d_val["correct"]
        t = d_val["total"]
        pct = round((c / t) * 100.0, 1) if t > 0 else 0.0
        domain_breakdown.append(
            DomainScore(
                domain_key=d_key,
                domain_name=d_val["name"],
                correct_count=c,
                total_count=t,
                score_percentage=pct,
            )
        )
        if pct >= 80.0:
            strengths.append(f"{d_val['name']} ({pct}%): Sangat baik dalam memahami konsep dan kaidah bahasa.")
        elif pct < 60.0:
            growth_areas.append(f"{d_val['name']} ({pct}%): Perlu pembiasaan lebih lanjut saat latihan berbicara bersama Milo.")

    # Smart Recommendation Logic
    if score_percentage >= 75.0:
        recommended_level = "B2"
        level_title = "Level B2 (Upper-Intermediate Ready)"
        recommendation_summary = (
            f"Luar biasa! Skor Anda {score_percentage}%. Anda menunjukkan penguasaan wacana terstruktur, "
            "kolokasi profesional, dan ragam bahasa diplomatis yang sangat solid. Anda sangat siap "
            "untuk skenario mendalam di Level B2 (STAR method, evaluasi kritis, dan diskusi akademis)."
        )
    elif score_percentage >= 50.0:
        recommended_level = "B1"
        level_title = "Level B1 (Intermediate Solid)"
        recommendation_summary = (
            f"Bagus! Skor Anda {score_percentage}%. Fondasi tata bahasa dan kosa kata umum Anda sudah kuat. "
            "Level B1 adalah tempat terbaik untuk membangun kelancaran berbicara (fluency) secara spontan "
            "sebelum beralih ke argumen kompleks. Anda juga dapat memilih Level B2 jika menyukai tantangan lebih tinggi."
        )
    else:
        recommended_level = "B1"
        level_title = "Level B1 (Intermediate Foundation)"
        recommendation_summary = (
            f"Skor Anda {score_percentage}%. Kami merekomendasikan memulai latihan dari Level B1 (Intermediate) "
            "agar Anda merasa nyaman dan percaya diri melatih pembentukan kalimat, pengucapan, dan percakapan santai "
            "tanpa tekanan berlebih."
        )

    # Determine final level applied
    final_selected_level = (payload.selected_level or recommended_level).strip().upper()
    if final_selected_level not in {"B1", "B2"}:
        final_selected_level = recommended_level

    saved_to_profile = False

    # Persist in DB if user is authenticated
    if current_user:
        try:
            placement_row = PlacementTestResult(
                user_id=str(current_user.id),
                total_questions=total_questions,
                correct_count=correct_count,
                score_percentage=score_percentage,
                grammar_score=domain_stats["grammar"]["correct"] / max(domain_stats["grammar"]["total"], 1) * 100.0,
                vocabulary_score=domain_stats["vocabulary"]["correct"] / max(domain_stats["vocabulary"]["total"], 1) * 100.0,
                discourse_score=domain_stats["discourse"]["correct"] / max(domain_stats["discourse"]["total"], 1) * 100.0,
                pragmatics_score=domain_stats["pragmatics"]["correct"] / max(domain_stats["pragmatics"]["total"], 1) * 100.0,
                recommended_level=recommended_level,
                selected_level=final_selected_level,
                answers_detail={
                    "answers": payload.answers,
                    "score": score_percentage,
                    "date": datetime.now(timezone.utc).isoformat(),
                },
            )
            db.add(placement_row)

            # Update user profile with placement score and chosen level
            current_user.placement_score = score_percentage
            current_user.cefr_level = final_selected_level

            # Research logging for Thesis Chapter 4
            analytics_log = SystemLogAnalytics(
                user_id=current_user.id,
                session_id=None,
                event_type="placement_test_completed",
                duration_seconds=0,
                turns_count=total_questions,
                extra_meta={
                    "score_percentage": score_percentage,
                    "correct_count": correct_count,
                    "recommended_level": recommended_level,
                    "selected_level": final_selected_level,
                },
            )
            db.add(analytics_log)

            await db.commit()
            saved_to_profile = True
            logger.info(f"Saved placement result for user {current_user.username}: score={score_percentage}%, level={final_selected_level}")
        except Exception as e:
            logger.error(f"Failed to persist placement result: {e}")
            await db.rollback()

    return PlacementSubmitResponse(
        score_percentage=score_percentage,
        total_questions=total_questions,
        correct_count=correct_count,
        recommended_level=recommended_level,
        selected_level=final_selected_level,
        level_title=level_title,
        recommendation_summary=recommendation_summary,
        strengths=strengths if strengths else ["Pemahaman umum materi sudah cukup baik."],
        growth_areas=growth_areas if growth_areas else ["Pertahankan performa ini saat sesi interaktif bersama Milo!"],
        domain_breakdown=domain_breakdown,
        question_results=question_results,
        saved_to_profile=saved_to_profile,
    )


@router.get(
    "/history",
    response_model=List[PlacementHistoryItem],
    summary="Get user placement test history",
)
async def get_placement_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[PlacementHistoryItem]:
    """Retrieve historical placement attempts for the authenticated user."""
    stmt = (
        select(PlacementTestResult)
        .where(PlacementTestResult.user_id == str(current_user.id))
        .order_by(PlacementTestResult.created_at.desc())
    )
    res = await db.execute(stmt)
    records = res.scalars().all()

    return [
        PlacementHistoryItem(
            id=r.id,
            created_at=r.created_at,
            total_questions=r.total_questions,
            correct_count=r.correct_count,
            score_percentage=r.score_percentage,
            grammar_score=r.grammar_score,
            vocabulary_score=r.vocabulary_score,
            discourse_score=r.discourse_score,
            pragmatics_score=r.pragmatics_score,
            recommended_level=r.recommended_level,
            selected_level=r.selected_level,
        )
        for r in records
    ]
