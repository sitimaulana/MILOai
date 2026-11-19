import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    security_bearer = HTTPBearer(auto_error=False)
except ImportError:
    def Depends(dep=None):
        return dep
    HTTPException = Exception
    status = None
    security_bearer = None
    HTTPAuthorizationCredentials = Any

try:
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.database import get_db
    from app.db.models import User
except ImportError:
    select = None
    AsyncSession = None
    get_db = None
    User = None

try:
    from app.config import settings
    JWT_SECRET_KEY = settings.jwt_secret_key
    JWT_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes
except Exception:
    JWT_SECRET_KEY = "milo-secret-key-change-in-production-2026"
    JWT_EXPIRE_MINUTES = 60 * 24 * 7

PBKDF2_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """Hash password with PBKDF2-HMAC-SHA256 and a 16-byte random salt."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored hash using constant-time comparison."""
    if not hashed_password or not plain_password:
        return False

    parts = hashed_password.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False

    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
    except (ValueError, TypeError):
        return False

    computed_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(computed_hash, expected_hash)


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64_decode(data: str) -> bytes:
    padding = (4 - len(data) % 4) % 4
    return base64.urlsafe_b64decode((data + "=" * padding).encode("ascii"))


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate HS256-signed JWT token using standard library primitives."""
    now = int(time.time())
    if expires_delta:
        expire_time = now + int(expires_delta.total_seconds())
    else:
        expire_time = now + (JWT_EXPIRE_MINUTES * 60)

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {**data, "iat": now, "exp": expire_time}

    header_segment = _b64_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")

    signature = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_segment = _b64_encode(signature)

    return f"{header_segment}.{payload_segment}.{signature_segment}"


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and verify JWT token signature and expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_segment, payload_segment, signature_segment = parts
        signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
        expected_sig = hmac.new(
            JWT_SECRET_KEY.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()

        provided_sig = _b64_decode(signature_segment)
        if not hmac.compare_digest(expected_sig, provided_sig):
            return None

        payload = json.loads(_b64_decode(payload_segment).decode("utf-8"))
        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload
    except Exception:
        return None


async def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Retrieve user if bearer token is present and valid; returns None otherwise."""
    if not creds or not creds.credentials:
        return None

    payload = decode_access_token(creds.credentials)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)  # noqa: E712
    )
    return result.scalar_one_or_none()


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """Enforce authentication on protected endpoints."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentikasi diperlukan. Silakan login terlebih dahulu.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
