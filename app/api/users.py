from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Session as UserSession
from app.models import User
from app.schemas.user import UpdateUserRequest, UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if data.email is not None and data.email != current_user.email:
        existing_user = db.execute(
            select(User).where(User.email == data.email)
        ).scalar_one_or_none()

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        current_user.email = data.email

    if data.last_name is not None:
        current_user.last_name = data.last_name

    if data.first_name is not None:
        current_user.first_name = data.first_name

    if data.middle_name is not None:
        current_user.middle_name = data.middle_name

    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete("/me")
def delete_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    current_user.status = "deleted"
    current_user.deleted_at = datetime.now(timezone.utc)

    sessions = db.execute(
        select(UserSession).where(
            UserSession.user_id == current_user.id,
            UserSession.is_active.is_(True),
        )
    ).scalars().all()

    for session in sessions:
        session.is_active = False

    db.commit()

    return {"message": "User deleted successfully"}
