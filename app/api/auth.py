from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_bearer_token
from app.core.config import settings
from app.core.database import get_db
from app.core.security import generate_session_token, hash_password, verify_password
from app.models import Session as UserSession
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
) -> User:
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    existing_user = db.execute(select(User).where(User.email == data.email)
    ).scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        last_name=data.last_name,
        first_name=data.first_name,
        middle_name=data.middle_name,
        status="active",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.execute(
        select(User).where(User.email == data.email)
    ).scalar_one_or_none()
    
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    token = generate_session_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.session_expire_minutes
    )

    session = UserSession(
        user_id=user.id,
        token=token,
        is_active=True,
        expires_at=expires_at,
    )

    db.add(session)
    db.commit()
    
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    session = db.execute(
        select(UserSession).where(
            UserSession.token == token,
            UserSession.is_active.is_(True),
        )
    ).scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive session",
        )

    session.is_active = False
    db.commit()

    return {"message": "Logged out successfully"}
