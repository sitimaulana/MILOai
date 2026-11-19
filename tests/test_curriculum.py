"""
MILO AI Backend - Tests for Curriculum & Microlearning Router
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.mark.asyncio
async def test_get_tracks():
    """Verify that curriculum tracks endpoint returns 3 tracks."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.get("/api/v1/curriculum/tracks")

    assert resp.status_code == 200
    tracks = resp.json()
    assert len(tracks) == 3
    codes = [t["track_code"] for t in tracks]
    assert "TRACK_A" in codes
    assert "TRACK_B" in codes
    assert "TRACK_C" in codes


@pytest.mark.asyncio
async def test_get_topics_filtered():
    """Verify filtering topics by track and CEFR level."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.get("/api/v1/curriculum/topics?track=job_interview&cefr_level=B1")

    assert resp.status_code == 200
    topics = resp.json()
    assert len(topics) == 3  # A1, A2, A3
    assert all(t["track_code"] == "TRACK_A" for t in topics)
    assert all(t["cefr_level"] == "B1" for t in topics)
    assert topics[0]["topic_id"] == "A1"
    assert "can_do_statement" in topics[0]


@pytest.mark.asyncio
async def test_get_topic_detail_and_quizzes():
    """Verify full topic detail and structured vocabulary / idioms."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.get("/api/v1/curriculum/topic/A1")

    assert resp.status_code == 200
    data = resp.json()
    assert data["topic_id"] == "A1"
    assert data["title"] == "Self-Introduction & Background"
    assert len(data["vocabulary"]) > 0
    assert len(data["idioms"]) > 0
    assert len(data["quizzes"]) == 2
    assert len(data["milo_prompts"]) > 0


@pytest.mark.asyncio
async def test_submit_quiz():
    """Verify submitting quiz answers and calculating score."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        payload = {
            "topic_id": "A1",
            "answers": {
                "0": "A",
                "1": "C",
            },
        }
        resp = await client.post("/api/v1/curriculum/quiz/submit", json=payload)

    assert resp.status_code == 200
    res = resp.json()
    assert res["topic_id"] == "A1"
    assert res["score"] == 100.0
    assert res["correct_count"] == 2
    assert res["bonus_points"] == 50
