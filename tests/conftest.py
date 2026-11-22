import pytest
from app.db.database import engine


@pytest.fixture(autouse=True)
async def cleanup_db_engine():
    """Ensure connection pool is cleanly disposed between test event loops on Windows."""
    yield
    try:
        await engine.dispose()
    except Exception:
        pass
