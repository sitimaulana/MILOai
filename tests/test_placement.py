"""
MILO AI Backend - Tests for Placement & Diagnostic Router (CEFR B1 vs B2)
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_get_placement_questions():
    """Verify that placement endpoint returns 20 questions without leaking answers."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.get("/api/v1/curriculum/placement/questions")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_questions"] == 20
    assert len(data["questions"]) == 20
    assert len(data["domains"]) == 4

    # Ensure answers and explanations are stripped from client response
    for q in data["questions"]:
        assert "answer" not in q
        assert "explanation" not in q
        assert "options" in q
        assert len(q["options"]) == 4
        assert q["domain"] in {"grammar", "vocabulary", "discourse", "pragmatics"}


@pytest.mark.asyncio
async def test_submit_placement_all_correct():
    """Verify submitting 100% correct answers produces B2 recommendation with full domain scores."""
    # Build all-correct answers based on master keys
    # Questions 1-5: B, A, B, A, A
    # Questions 6-10: B, B, A, A, B
    # Questions 11-15: B, B, A, A, A
    # Questions 16-20: B, B, B, B, B
    correct_answers = {
        "1": "B", "2": "A", "3": "B", "4": "A", "5": "A",
        "6": "B", "7": "B", "8": "A", "9": "A", "10": "B",
        "11": "B", "12": "B", "13": "A", "14": "A", "15": "A",
        "16": "B", "17": "B", "18": "B", "19": "B", "20": "B",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.post(
            "/api/v1/curriculum/placement/submit",
            json={"answers": correct_answers},
        )

    assert resp.status_code == 200
    res = resp.json()
    assert res["total_questions"] == 20
    assert res["correct_count"] == 20
    assert res["score_percentage"] == 100.0
    assert res["recommended_level"] == "B2"
    assert "Level B2" in res["level_title"]
    assert len(res["domain_breakdown"]) == 4
    for d in res["domain_breakdown"]:
        assert d["score_percentage"] == 100.0


@pytest.mark.asyncio
async def test_submit_placement_low_score_recommends_b1():
    """Verify that low score (< 50%) recommends Level B1."""
    # Submit all 'C' answers (none of them is 'C' in our key)
    wrong_answers = {str(i): "C" for i in range(1, 21)}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.post(
            "/api/v1/curriculum/placement/submit",
            json={"answers": wrong_answers},
        )

    assert resp.status_code == 200
    res = resp.json()
    assert res["correct_count"] == 0
    assert res["score_percentage"] == 0.0
    assert res["recommended_level"] == "B1"
    assert "Level B1" in res["level_title"]
    assert len(res["growth_areas"]) > 0


@pytest.mark.asyncio
async def test_submit_placement_intermediate_score_recommends_b1():
    """Verify that score around 55% recommends B1 with bridge guidance."""
    # 11 correct answers (55%)
    mixed_answers = {
        "1": "B", "2": "A", "3": "B", "4": "A", "5": "A",
        "6": "B", "7": "B", "8": "A", "9": "A", "10": "B",
        "11": "B",
        "12": "C", "13": "C", "14": "C", "15": "C",
        "16": "C", "17": "C", "18": "C", "19": "C", "20": "C",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.post(
            "/api/v1/curriculum/placement/submit",
            json={"answers": mixed_answers},
        )

    assert resp.status_code == 200
    res = resp.json()
    assert res["correct_count"] == 11
    assert res["score_percentage"] == 55.0
    assert res["recommended_level"] == "B1"
