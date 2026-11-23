"""
MILO AI Backend - Unit & Integration Test for Session Closing Mechanism

Tests that:
1. is_closing=True appends CLOSING_DIRECTIVE to LLM prompt.
2. process_text with is_closing=True produces is_session_closed=True.
3. Chat endpoint returns is_session_closed=True on time limit closing turn.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.core.llm import CLOSING_DIRECTIVE, generate_response, milo_llm, sanitize_llm_response
from app.models.schemas import ChatRequest, ChatResponse


@pytest.mark.asyncio
async def test_sanitize_llm_response():
    """Verify that leaked rule commentary is stripped from LLM output."""
    raw = "That sounds exciting! What do you like most about it?\n\n*One question rule applies.*"
    assert sanitize_llm_response(raw) == "That sounds exciting! What do you like most about it?"

    raw2 = "Great job! How was your weekend? *(One question rule applies)*"
    assert sanitize_llm_response(raw2) == "Great job! How was your weekend?"

    raw3 = "I like reading books. What genre do you prefer? (One question rule applies.)"
    assert sanitize_llm_response(raw3) == "I like reading books. What genre do you prefer?"

    raw4 = "Hello there! *Rule 2 applied*"
    assert sanitize_llm_response(raw4) == "Hello there!"

    raw5 = "Nice to meet you! [One question rule applies]"
    assert sanitize_llm_response(raw5) == "Nice to meet you!"


@pytest.mark.asyncio
async def test_llm_closing_directive_appended():
    """Verify that is_closing=True appends the closing directive."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="That wraps up our practice today! You did great speaking with confidence. See you next time!"
                    )
                )
            ],
            usage=MagicMock(prompt_tokens=50, completion_tokens=25),
            model="gpt-4o-mini",
        )
    )

    with patch.object(milo_llm, "_get_client_and_model", return_value=(mock_client, "gpt-4o-mini", "openai")):
        resp = await generate_response(
            user_message="Time is up for today's practice session.",
            history=[],
            rag_context="",
            learning_goal="General practice",
            cefr_level="B1",
            is_closing=True,
        )

        assert resp.content is not None
        assert "?" not in resp.content

        # Inspect the messages argument passed to chat.completions.create
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        messages = call_kwargs["messages"]
        system_msg = next(m["content"] for m in messages if m["role"] == "system")
        assert "SESSION TIME LIMIT REACHED" in system_msg
        assert "DO NOT ask any questions" in system_msg


@pytest.mark.asyncio
async def test_pipeline_process_text_closing():
    """Verify pipeline process_text sets is_session_closed=True when is_closing=True."""
    from app.services.pipeline import MILOPipeline

    mock_db = AsyncMock()
    pipeline = MILOPipeline(mock_db)

    # Mock session
    mock_session = MagicMock()
    mock_session.id = "11111111-1111-1111-1111-111111111111"
    mock_session.learning_goal = "Interview"
    mock_session.cefr_level = "B1"
    mock_session.topic = "job_interview"
    pipeline._ensure_session = AsyncMock(return_value=mock_session)
    pipeline._conv.get_history = AsyncMock(return_value=[])
    pipeline._conv.add_message = AsyncMock(return_value=MagicMock(id="msg-123"))

    with (
        patch("app.services.pipeline.retrieve_adaptive", new_callable=AsyncMock, return_value=[]),
        patch(
            "app.services.pipeline.generate_response",
            new_callable=AsyncMock,
            return_value=MagicMock(content="Thank you for your practice today! Goodbye!"),
        ) as mock_gen,
        patch("app.services.pipeline.synthesize_speech", new_callable=AsyncMock, return_value="fake_b64_audio"),
    ):
        result = await pipeline.process_text(
            session_id=str(mock_session.id),
            user_message="Time is up for today's practice session.",
            learning_goal="Interview",
            cefr_level="B1",
            return_audio=True,
            is_closing=True,
            trigger="time_limit_reached",
        )

        assert result.is_session_closed is True
        assert result.avatar_emotion == "happy"
        assert result.response_text == "Thank you for your practice today! Goodbye!"
        mock_gen.assert_called_once()
        assert mock_gen.call_args.kwargs["is_closing"] is True


@pytest.mark.asyncio
async def test_chat_endpoint_closing_response():
    """Verify /api/v1/chat returns is_session_closed=True when is_closing=True."""
    from app.db.models import User as DBUser
    import uuid

    mock_user = MagicMock(spec=DBUser)
    mock_user.id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    mock_user.username = "testuser"
    mock_user.full_name = "Test User"
    mock_user.cefr_level = "B1"

    with (
        patch("app.db.database.init_db", new_callable=AsyncMock),
        patch("app.core.asr.whisper_asr.load"),
        patch("app.core.rag.rag_retriever.load"),
        patch(
            "app.services.pipeline.MILOPipeline.process_text",
            new_callable=AsyncMock,
            return_value=MagicMock(
                session_id="test-session",
                message_id="msg-1",
                response_text="Practice completed! Great job!",
                translation="Latihan selesai! Kerja bagus!",
                audio_base64="fake_audio",
                feedback=None,
                rag_sources=[],
                rag_details=[],
                avatar_emotion="happy",
                is_session_closed=True,
            ),
        ),
    ):
        from app.main import app
        from app.api.chat import get_current_user
        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post(
                    "/api/v1/chat",
                    json={
                        "session_id": "test-session",
                        "message": "Time is up for today's practice session.",
                        "is_closing": True,
                        "trigger": "time_limit_reached",
                        "cefr_level": "B1",
                        "return_audio": True,
                    },
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["is_session_closed"] is True
        assert data["response_text"] == "Practice completed! Great job!"
