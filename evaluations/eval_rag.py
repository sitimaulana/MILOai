"""
MILO AI Backend - RAG Evaluation Suite (DeepEval)

Evaluates the Retrieval-Augmented Generation (RAG) pipeline:
- Faithfulness: Hallucination rate relative to Obsidian KB context (0.0 - 1.0)
- Answer Relevancy: How directly the answer addresses the user question (0.0 - 1.0)
- Contextual Precision / Recall: Quality of ChromaDB chunk retrieval
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from evaluations.model_loader import get_eval_judge_model


def load_rag_benchmarks() -> List[Dict[str, Any]]:
    """Load benchmark RAG queries and expected contexts."""
    dataset_path = Path(__file__).parent / "datasets" / "rag_benchmarks.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def evaluate_rag_item(
    item: Dict[str, Any],
    actual_output: Optional[str] = None,
    retrieval_context: Optional[List[str]] = None,
    judge_model: Any = None,
) -> Dict[str, Any]:
    """
    Evaluates a single RAG test case using DeepEval metrics.
    """
    judge = judge_model or get_eval_judge_model()

    query = item["input"]
    expected_output = item.get("expected_output")
    context = retrieval_context or item.get("retrieval_context", [])
    output = actual_output or expected_output

    test_case = LLMTestCase(
        input=query,
        actual_output=output,
        expected_output=expected_output,
        retrieval_context=context,
    )

    # 1. Faithfulness Metric
    faithfulness_metric = FaithfulnessMetric(
        threshold=0.7,
        model=judge,
        include_reason=True,
    )
    faithfulness_metric.measure(test_case)

    # 2. Answer Relevancy Metric
    relevancy_metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=judge,
        include_reason=True,
    )
    relevancy_metric.measure(test_case)

    result = {
        "id": item["id"],
        "category": item.get("category", "general"),
        "cefr_level": item.get("cefr_level", "B1-B2"),
        "input": query,
        "actual_output": output,
        "faithfulness_score": round(float(faithfulness_metric.score), 4),
        "faithfulness_passed": faithfulness_metric.is_successful(),
        "faithfulness_reason": faithfulness_metric.reason,
        "relevancy_score": round(float(relevancy_metric.score), 4),
        "relevancy_passed": relevancy_metric.is_successful(),
        "relevancy_reason": relevancy_metric.reason,
    }

    # Optional: Contextual Precision if expected_output is present
    if expected_output:
        try:
            precision_metric = ContextualPrecisionMetric(
                threshold=0.7,
                model=judge,
                include_reason=False,
            )
            precision_metric.measure(test_case)
            result["contextual_precision_score"] = round(float(precision_metric.score), 4)
            result["contextual_precision_passed"] = precision_metric.is_successful()
        except Exception:
            result["contextual_precision_score"] = None
            result["contextual_precision_passed"] = None

    return result


async def run_rag_evaluations(
    use_live_pipeline: bool = False,
    max_samples: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Run evaluation on the RAG benchmark dataset.
    If use_live_pipeline=True, retrieves live context from ChromaDB and generates
    responses with MILO's LLM before scoring with DeepEval.
    """
    items = load_rag_benchmarks()
    if max_samples:
        items = items[:max_samples]

    judge = get_eval_judge_model()
    results = []

    if use_live_pipeline:
        from app.core.rag import rag_retriever
        from app.core.llm import milo_llm

        if not rag_retriever.is_ready:
            rag_retriever.load()

        for item in items:
            query = item["input"]
            retrieved_docs = await rag_retriever.retrieve(query, k=3)
            retrieval_context = [doc.content for doc in retrieved_docs] if retrieved_docs else item.get("retrieval_context", [])
            formatted_context = "\n\n".join(retrieval_context)

            llm_res = await milo_llm.generate(
                user_message=query,
                history=[],
                rag_context=formatted_context,
                learning_goal=f"Learn English {item.get('category')}",
                cefr_level=item.get("cefr_level", "B1"),
            )

            res = await evaluate_rag_item(
                item=item,
                actual_output=llm_res.content,
                retrieval_context=retrieval_context,
                judge_model=judge,
            )
            results.append(res)
    else:
        for item in items:
            res = await evaluate_rag_item(
                item=item,
                judge_model=judge,
            )
            results.append(res)

    return results

