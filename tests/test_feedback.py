"""
MILO AI Backend - Test Suite: Feedback Engine

Tests for the language feedback analyzer.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_openai_client():
    """Mock the OpenAI client for feedback tests."""
    client = AsyncMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = json.dumps({
        "grammar_score": 75.0,
        "vocabulary_score": 80.0,
        "fluency_score": 70.0,
        "corrections": [
            {
                "original": "I go to the store",
                "corrected": "I went to the store",
                "explanation": "Use past tense 'went' for completed actions.",
                "error_type": "grammar"
            }
        ],
        "positive_note": "Great effort using complex sentences!",
        "tip": "Practice past tense verbs for B2 level."
    })
    client.chat.completions.create = AsyncMock(return_value=mock_completion)
    return client


@pytest.mark.asyncio
async def test_analyze_returns_feedback_result(mock_openai_client):
    """Test that analyze() returns a properly structured FeedbackResult."""
    from app.core.feedback import FeedbackEngine, FeedbackResult

    engine = FeedbackEngine()
    engine._client = mock_openai_client

    result = await engine.analyze("Yesterday I go to the store.", cefr_level="B1")

    assert isinstance(result, FeedbackResult)
    assert result.grammar_score == 75.0
    assert result.vocabulary_score == 80.0
    assert result.fluency_score == 70.0
    assert len(result.corrections) == 1
    assert result.corrections[0].error_type == "grammar"
    assert result.positive_note != ""
    assert result.tip != ""


@pytest.mark.asyncio
async def test_analyze_empty_text_returns_zero_scores():
    """Test that empty input returns zero scores."""
    from app.core.feedback import FeedbackEngine

    engine = FeedbackEngine()
    result = await engine.analyze("")

    assert result.grammar_score == 0.0
    assert result.vocabulary_score == 0.0
    assert result.fluency_score == 0.0


def test_overall_score_calculation():
    """Test weighted overall score: grammar 40%, vocab 30%, fluency 30%."""
    from app.core.feedback import FeedbackResult

    result = FeedbackResult(
        grammar_score=100.0,
        vocabulary_score=100.0,
        fluency_score=100.0,
        positive_note="",
        tip="",
    )
    assert result.overall_score == 100.0

    result2 = FeedbackResult(
        grammar_score=80.0,
        vocabulary_score=70.0,
        fluency_score=60.0,
        positive_note="",
        tip="",
    )
    expected = 80.0 * 0.4 + 70.0 * 0.3 + 60.0 * 0.3
    assert abs(result2.overall_score - expected) < 0.001


@pytest.mark.asyncio
async def test_fallback_on_json_parse_error(mock_openai_client):
    """Test that malformed JSON response returns fallback result."""
    from app.core.feedback import FeedbackEngine

    mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "NOT JSON"

    engine = FeedbackEngine()
    engine._client = mock_openai_client

    result = await engine.analyze("Some text", cefr_level="B1")
    # Fallback returns 75.0 for all scores
    assert result.grammar_score == 75.0
