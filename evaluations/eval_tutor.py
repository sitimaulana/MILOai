"""
MILO AI Backend - Tutor Persona & CEFR Adaptation Evaluation Suite (DeepEval)

Evaluates the MILO conversational speaking tutor:
- CEFR Adaptation: Complexity, sentence length, and vocabulary match target level
- One Question Rule: Concludes with exactly ONE natural open-ended question
- Conversational Warmth & Naturalness: Active listening without robotic clichés
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from evaluations.model_loader import get_eval_judge_model


def load_tutor_benchmarks() -> List[Dict[str, Any]]:
    """Load benchmark multi-level conversation test cases."""
    dataset_path = Path(__file__).parent / "datasets" / "tutor_benchmarks.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_tutor_metrics(judge_model: Any) -> Dict[str, GEval]:
    """Build G-Eval custom rubric metrics for speaking companion."""
    cefr_adaptation_metric = GEval(
        name="CEFR Level Adaptation",
        criteria=(
            "Assess whether the tutor's response matches the target CEFR level guidelines:\n"
            "- A1/A2: Short, gentle sentences, basic vocabulary, very accessible.\n"
            "- B1/B2: Natural conversational sentences, connectors, idiomatic richness.\n"
            "The language should neither be overly complex for beginners nor infantilizing for higher levels."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge_model,
        threshold=0.7,
    )

    one_question_rule_metric = GEval(
        name="One Question Rule",
        criteria=(
            "Assess whether the tutor ends its response with exactly ONE engaging, open-ended "
            "question to keep the dialogue flowing smoothly. It should NOT ask multiple questions, "
            "interrogate the learner, or forget to ask a question."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge_model,
        threshold=0.7,
    )

    conversational_warmth_metric = GEval(
        name="Conversational Warmth & Active Listening",
        criteria=(
            "Assess whether the tutor responds like a supportive speaking partner: reacts genuinely "
            "to what the learner said (active listening), avoids robotic filler ('Awesome!', 'That's great!'), "
            "and maintains a warm, encouraging tone."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge_model,
        threshold=0.7,
    )

    return {
        "cefr_adaptation": cefr_adaptation_metric,
        "one_question": one_question_rule_metric,
        "warmth": conversational_warmth_metric,
    }


async def evaluate_tutor_item(
    item: Dict[str, Any],
    tutor_reply: str,
    judge_model: Any = None,
) -> Dict[str, Any]:
    """
    Evaluates a single tutor turn against G-Eval persona rubrics.
    """
    judge = judge_model or get_eval_judge_model()
    metrics = build_tutor_metrics(judge)

    test_case = LLMTestCase(
        input=(
            f"Learner CEFR Level: {item['cefr_level']}\n"
            f"Learning Goal: {item['learning_goal']}\n"
            f"Learner Message: '{item['user_message']}'"
        ),
        actual_output=tutor_reply,
    )

    metrics["cefr_adaptation"].measure(test_case)
    metrics["one_question"].measure(test_case)
    metrics["warmth"].measure(test_case)

    return {
        "id": item["id"],
        "cefr_level": item["cefr_level"],
        "user_message": item["user_message"],
        "tutor_reply": tutor_reply,
        "cefr_adaptation_score": round(float(metrics["cefr_adaptation"].score), 4),
        "cefr_adaptation_passed": metrics["cefr_adaptation"].is_successful(),
        "one_question_score": round(float(metrics["one_question"].score), 4),
        "one_question_passed": metrics["one_question"].is_successful(),
        "warmth_score": round(float(metrics["warmth"].score), 4),
        "warmth_passed": metrics["warmth"].is_successful(),
    }


async def run_tutor_evaluations(
    max_samples: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Runs evaluation against live MILO Conversation LLM.
    """
    from app.core.llm import milo_llm

    items = load_tutor_benchmarks()
    if max_samples:
        items = items[:max_samples]

    judge = get_eval_judge_model()
    results = []

    for item in items:
        llm_res = await milo_llm.generate(
            user_message=item["user_message"],
            history=[],
            rag_context="",
            learning_goal=item["learning_goal"],
            cefr_level=item["cefr_level"],
        )

        eval_res = await evaluate_tutor_item(
            item=item,
            tutor_reply=llm_res.content,
            judge_model=judge,
        )
        results.append(eval_res)

    return results

