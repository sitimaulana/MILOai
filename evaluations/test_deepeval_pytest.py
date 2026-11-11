"""
MILO AI Backend - DeepEval Pytest Integration

Allows running benchmark assertions via pytest:
    uv run pytest evaluations/test_deepeval_pytest.py
"""

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from evaluations.model_loader import get_eval_judge_model


@pytest.fixture(scope="module")
def judge_model():
    """Shared judge model fixture."""
    return get_eval_judge_model()


def test_rag_present_perfect_faithfulness(judge_model):
    """Test faithfulness for Present Perfect explanation."""
    test_case = LLMTestCase(
        input="Can you explain when I should use Present Perfect tense?",
        actual_output=(
            "Use the Present Perfect for actions connected to the present, "
            "unfinished periods of time, or life experiences without a specified time."
        ),
        retrieval_context=[
            "Present Perfect tense connects the past with the present. "
            "It is used for life experiences (without specific time), ongoing states starting in the past, "
            "or past actions with a present result."
        ],
    )
    metric = FaithfulnessMetric(threshold=0.7, model=judge_model)
    assert_test(test_case, [metric])


def test_rag_answer_relevancy(judge_model):
    """Test relevancy of response to user question."""
    test_case = LLMTestCase(
        input="When should I use 'since' and when should I use 'for'?",
        actual_output=(
            "Use 'since' with a specific starting point in time (like since 2020), "
            "and 'for' with a duration or period (like for two years)."
        ),
    )
    metric = AnswerRelevancyMetric(threshold=0.7, model=judge_model)
    assert_test(test_case, [metric])

