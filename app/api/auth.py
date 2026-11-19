import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.db.models import User, UserGamification
from app.models.schemas import (
    AuthTokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
    UserUpdateRequest,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{3,30}$")
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
VALID_CEFR_LEVELS = {"A1", "A2", "B1", "B2", "C1"}


def _serialize_user(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        cefr_level=user.cefr_level,
        created_at=user.created_at,
        last_login=user.last_login,
        is_active=user.is_active,
    )


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthTokenResponse:
    username_clean = request.username.strip().lower()
    if not USERNAME_REGEX.match(username_clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username harus 3-30 karakter dan hanya boleh berisi huruf, angka, garis bawah, titik, atau tanda hubung.",
        )

    email_clean: Optional[str] = None
    if request.email and request.email.strip():
        email_clean = request.email.strip().lower()
        if not EMAIL_REGEX.match(email_clean):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format email tidak valid.",
            )

    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password minimal 6 karakter.",
        )

    # Check for existing username or email collisions
    existing_check = await db.execute(
        select(User).where(
            or_(
                func.lower(User.username) == username_clean,
                func.lower(User.email) == email_clean if email_clean else False,
            )
        )
    )
    existing_user = existing_check.scalar_one_or_none()
    if existing_user:
        if existing_user.username.lower() == username_clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username sudah terdaftar. Silakan gunakan username lain.",
            )
        if email_clean and existing_user.email and existing_user.email.lower() == email_clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah terdaftar. Silakan gunakan email lain atau masuk.",
            )

    cefr = (request.cefr_level or "B1").upper().strip()
    if cefr not in VALID_CEFR_LEVELS:
        cefr = "B1"

    new_user = User(
        username=username_clean,
        email=email_clean,
        hashed_password=hash_password(request.password),
        full_name=request.full_name.strip() if request.full_name else None,
        cefr_level=cefr,
        is_active=True,
    )
    db.add(new_user)
    await db.flush()

    # Pre-seed gamification row so stats resolve safely on first load
    user_gamification = UserGamification(user_id=new_user.id)
    db.add(user_gamification)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token({
        "sub": str(new_user.id),
        "username": new_user.username,
        "cefr_level": new_user.cefr_level,
    })

    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=_serialize_user(new_user),
    )


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Login to user account",
)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthTokenResponse:
    identifier = request.username.strip().lower()

    result = await db.execute(
        select(User).where(
            or_(
                func.lower(User.username) == identifier,
                func.lower(User.email) == identifier,
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username/email atau password salah.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun ini telah dinonaktifkan. Hubungi admin untuk bantuan.",
        )

    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({
        "sub": str(user.id),
        "username": user.username,
        "cefr_level": user.cefr_level,
    })

    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=_serialize_user(user),
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get currently authenticated user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    return _serialize_user(current_user)


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update profile details for the authenticated user",
)
async def update_me(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    if request.full_name is not None:
        current_user.full_name = request.full_name.strip() or None

    if request.email is not None and request.email.strip():
        email_clean = request.email.strip().lower()
        if not EMAIL_REGEX.match(email_clean):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format email tidak valid.",
            )

        # Check collision with other users
        dup_check = await db.execute(
            select(User).where(
                func.lower(User.email) == email_clean,
                User.id != current_user.id,
            )
        )
        if dup_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah digunakan akun lain.",
            )
        current_user.email = email_clean

    if request.cefr_level:
        cefr = request.cefr_level.upper().strip()
        if cefr in VALID_CEFR_LEVELS:
            current_user.cefr_level = cefr

    await db.commit()
    await db.refresh(current_user)
    return _serialize_user(current_user)
