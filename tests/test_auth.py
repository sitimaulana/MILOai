import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_register_and_login_flow():
    """Verify registration, duplicate handling, login, and profile retrieval."""
    unique_suffix = uuid.uuid4().hex[:8]
    test_username = f"user_{unique_suffix}"
    test_email = f"{test_username}@example.com"
    test_password = "SecretPassword123"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register new user
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_username,
                "email": test_email,
                "password": test_password,
                "full_name": "Test Learner",
                "cefr_level": "B2",
            },
        )
        assert reg_resp.status_code == 201
        reg_data = reg_resp.json()
        assert "access_token" in reg_data
        assert reg_data["user"]["username"] == test_username
        assert reg_data["user"]["cefr_level"] == "B2"

        # Prevent duplicate username registration
        dup_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_username,
                "email": f"other_{unique_suffix}@example.com",
                "password": test_password,
            },
        )
        assert dup_resp.status_code == 400

        # Login with valid credentials
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_username,
                "password": test_password,
            },
        )
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        token = login_data["access_token"]
        assert token is not None

        # Login with email instead of username
        login_email_resp = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_email,
                "password": test_password,
            },
        )
        assert login_email_resp.status_code == 200

        # Login with wrong password
        bad_pw_resp = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_username,
                "password": "WrongPassword!",
            },
        )
        assert bad_pw_resp.status_code == 401

        # Access protected endpoint with valid token
        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == test_username

        # Access protected endpoint without token
        unauth_resp = await client.get("/api/v1/auth/me")
        assert unauth_resp.status_code == 401

        # Update profile
        update_resp = await client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"full_name": "Updated Name", "cefr_level": "B1"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["full_name"] == "Updated Name"
        assert update_resp.json()["cefr_level"] == "B1"


@pytest.mark.asyncio
async def test_register_validation():
    """Verify input validation rules for username and password."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Username too short
        resp_short_user = await client.post(
            "/api/v1/auth/register",
            json={"username": "ab", "password": "ValidPassword123"},
        )
        assert resp_short_user.status_code in (400, 422)

        # Password too short
        resp_short_pw = await client.post(
            "/api/v1/auth/register",
            json={"username": f"valid_{uuid.uuid4().hex[:6]}", "password": "123"},
        )
        assert resp_short_pw.status_code in (400, 422)
