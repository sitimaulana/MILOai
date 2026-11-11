"""
MILO AI Backend - Language Feedback Engine Evaluation Suite (DeepEval)

Evaluates the CEFR Feedback Analyzer:
- Grammar Correction Accuracy: True error detection without hallucinated rules
- False Positive Resistance: Ensuring correct sentences are not wrongly penalized
- Pedagogical Constructiveness: Clear, encouraging, and level-appropriate advice
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from evaluations.model_loader import get_eval_judge_model


def load_feedback_benchmarks() -> List[Dict[str, Any]]:
    """Load benchmark student utterances for feedback evaluation."""
    dataset_path = Path(__file__).parent / "datasets" / "feedback_benchmarks.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_feedback_metrics(judge_model: Any) -> Dict[str, GEval]:
    """Build G-Eval custom rubric metrics for feedback engine evaluation."""
    correction_accuracy_metric = GEval(
        name="Correction Accuracy",
        criteria=(
            "Assess whether the feedback accurately identifies genuine language errors "
            "(grammar, vocabulary, preposition) and provides a correct, natural correction "
            "with a valid explanation. The evaluator should not penalize valid alternative phrases."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge_model,
        threshold=0.7,
    )

    false_positive_metric = GEval(
        name="False Positive Resistance",
        criteria=(
            "Assess whether the feedback avoids creating imaginary errors (hallucinated mistakes). "
            "If the input utterance is grammatically correct and natural, the output should "
            "NOT mark it as an error or penalize the student's score."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge_model,
        threshold=0.7,
    )

    pedagogical_metric = GEval(
        name="Pedagogical Tone & Clarity",
        criteria=(
            "Assess whether the feedback is encouraging, supportive, and pedagogical. "
            "Explanations should be concise (1-2 sentences), easy to grasp, and motivating for the student."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge_model,
        threshold=0.7,
    )

    return {
        "accuracy": correction_accuracy_metric,
        "false_positive": false_positive_metric,
        "pedagogical": pedagogical_metric,
    }


async def evaluate_feedback_item(
    item: Dict[str, Any],
    feedback_output_json: str,
    judge_model: Any = None,
) -> Dict[str, Any]:
    """
    Evaluates feedback generated for a single learner utterance.
    """
    judge = judge_model or get_eval_judge_model()
    metrics = build_feedback_metrics(judge)

    user_text = item["user_text"]
    test_case = LLMTestCase(
        input=f"Student Utterance: '{user_text}' (Target CEFR: {item.get('cefr_level', 'B1')})",
        actual_output=feedback_output_json,
    )

    # Measure Accuracy
    metrics["accuracy"].measure(test_case)

    # Measure False Positive Resistance
    metrics["false_positive"].measure(test_case)

    # Measure Pedagogical Tone
    metrics["pedagogical"].measure(test_case)

    return {
        "id": item["id"],
        "type": item["type"],
        "user_text": user_text,
        "cefr_level": item.get("cefr_level", "B1"),
        "has_error": item["has_error"],
        "accuracy_score": round(float(metrics["accuracy"].score), 4),
        "accuracy_passed": metrics["accuracy"].is_successful(),
        "accuracy_reason": metrics["accuracy"].reason,
        "false_positive_score": round(float(metrics["false_positive"].score), 4),
        "false_positive_passed": metrics["false_positive"].is_successful(),
        "pedagogical_score": round(float(metrics["pedagogical"].score), 4),
        "pedagogical_passed": metrics["pedagogical"].is_successful(),
    }


async def run_feedback_evaluations(
    max_samples: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Runs evaluation against the actual MILO feedback engine.
    """
    from app.core.feedback import feedback_engine

    items = load_feedback_benchmarks()
    if max_samples:
        items = items[:max_samples]

    judge = get_eval_judge_model()
    results = []

    for item in items:
        # Run real feedback engine
        result = await feedback_engine.analyze(
            user_text=item["user_text"],
            cefr_level=item.get("cefr_level", "B1"),
        )

        # Serialize feedback to JSON string for evaluator
        feedback_summary = json.dumps({
            "grammar_score": result.grammar_score,
            "vocabulary_score": result.vocabulary_score,
            "fluency_score": result.fluency_score,
            "overall_score": result.overall_score,
            "corrections": [
                {
                    "original": c.original,
                    "corrected": c.corrected,
                    "explanation": c.explanation,
                    "error_type": c.error_type,
                }
                for c in result.corrections
            ],
            "positive_note": result.positive_note,
            "tip": result.tip,
        }, indent=2)

        eval_res = await evaluate_feedback_item(
            item=item,
            feedback_output_json=feedback_summary,
            judge_model=judge,
        )
        results.append(eval_res)

    return results

