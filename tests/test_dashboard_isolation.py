import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_dashboard_and_session_user_isolation():
    """Verify that dashboard metrics and session details are strictly isolated per user."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Unauthenticated access to /dashboard must be rejected with 401
        unauth_dash = await client.get("/api/v1/dashboard")
        assert unauth_dash.status_code == 401

        # 2. Register User A
        suffix_a = uuid.uuid4().hex[:8]
        user_a_name = f"user_a_{suffix_a}"
        resp_a = await client.post(
            "/api/v1/auth/register",
            json={
                "username": user_a_name,
                "password": "Password123!",
                "full_name": "User Alpha",
                "cefr_level": "B1",
            },
        )
        assert resp_a.status_code == 201
        token_a = resp_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 3. User A starts a session
        start_a = await client.post(
            "/api/v1/session/start",
            headers=headers_a,
            json={
                "topic": "job_interview",
                "cefr_level": "B1",
                "daily_goal": "5_min",
            },
        )
        assert start_a.status_code == 201
        session_id_a = start_a.json()["session_id"]

        # 4. End User A's session so it counts as completed
        end_a = await client.post(
            "/api/v1/session/end",
            headers=headers_a,
            json={"session_id": session_id_a},
        )
        assert end_a.status_code == 200

        # 5. Check User A's dashboard: should see their completed session
        dash_a = await client.get("/api/v1/dashboard", headers=headers_a)
        assert dash_a.status_code == 200
        dash_a_data = dash_a.json()
        assert dash_a_data["total_sessions"] == 1
        assert len(dash_a_data["recent_sessions"]) == 1
        assert dash_a_data["recent_sessions"][0]["session_id"] == session_id_a

        # 6. Register User B (fresh new user, 0 sessions)
        suffix_b = uuid.uuid4().hex[:8]
        user_b_name = f"user_b_{suffix_b}"
        resp_b = await client.post(
            "/api/v1/auth/register",
            json={
                "username": user_b_name,
                "password": "Password123!",
                "full_name": "User Beta",
                "cefr_level": "B2",
            },
        )
        assert resp_b.status_code == 201
        token_b = resp_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 7. Check User B's dashboard: MUST NOT see User A's sessions
        dash_b = await client.get("/api/v1/dashboard", headers=headers_b)
        assert dash_b.status_code == 200
        dash_b_data = dash_b.json()
        assert dash_b_data["total_sessions"] == 0
        assert len(dash_b_data["recent_sessions"]) == 0
        assert dash_b_data["avg_overall_score"] == 0.0

        # 8. User B attempts to access User A's session feedback: MUST be 403 Forbidden
        fb_b = await client.get(
            f"/api/v1/session/{session_id_a}/feedback",
            headers=headers_b,
        )
        assert fb_b.status_code == 403

        # 9. (Removed: /export/obsidian endpoint not yet implemented)
