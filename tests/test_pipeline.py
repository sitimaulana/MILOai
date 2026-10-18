"""
MILO AI Backend - Integration Test: Full Pipeline

Tests the complete text → response pipeline using mocked AI components.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def mock_pipeline_dependencies():
    """Patch all AI components to avoid actual API calls."""
    with (
        patch("app.core.asr.whisper_asr.is_loaded", return_value=True),
        patch("app.core.rag.rag_retriever.retrieve", new_callable=AsyncMock, return_value=[]),
        patch("app.core.rag.rag_retriever.format_context_for_prompt", return_value=""),
        patch(
            "app.core.llm.milo_llm.generate",
            new_callable=AsyncMock,
            return_value=MagicMock(
                content="Great question! The present perfect is used for actions that have a connection to the present.",
                prompt_tokens=100,
                completion_tokens=30,
                model="gpt-4o-mini",
            ),
        ),
        patch(
            "app.core.feedback.feedback_engine.analyze",
            new_callable=AsyncMock,
            return_value=MagicMock(
                grammar_score=90.0,
                vocabulary_score=85.0,
                fluency_score=88.0,
                corrections=[],
                positive_note="Excellent question!",
                tip="Try using 'however' to connect ideas.",
                overall_score=88.1,
            ),
        ),
        patch(
            "app.core.tts.tts_synthesizer.synthesize",
            new_callable=AsyncMock,
            return_value="ZmFrZWF1ZGlv",  # base64 "fakeaudio"
        ),
        patch("app.db.database.init_db", new_callable=AsyncMock),
        patch("app.core.asr.whisper_asr.load"),
        patch("app.core.rag.rag_retriever.load"),
    ):
        yield


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test that the health endpoint returns 200."""
    with (
        patch("app.db.database.init_db", new_callable=AsyncMock),
        patch("app.core.asr.whisper_asr.load"),
        patch("app.core.rag.rag_retriever.load"),
    ):
        from app.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint."""
    with (
        patch("app.db.database.init_db", new_callable=AsyncMock),
        patch("app.core.asr.whisper_asr.load"),
        patch("app.core.rag.rag_retriever.load"),
    ):
        from app.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/")

        assert response.status_code == 200
        assert "MILO" in response.json()["message"]
