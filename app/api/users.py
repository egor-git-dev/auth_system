from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Role, Session as UserSession, User, UserRole
from app.schemas.user import CurrentUserResponse, UpdateUserRequest, UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=CurrentUserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUserResponse:
    role_ids = db.execute(
        select(UserRole.role_id).where(UserRole.user_id == current_user.id)
    ).scalars().all()
    
    roles = db.execute(
        select(Role).where(Role.id.in_(role_ids))
    ).scalars().all()
    
    role_names = [role.name for role in roles]
    
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        last_name=current_user.last_name,
        first_name=current_user.first_name,
        middle_name=current_user.middle_name,
        status=current_user.status,
        roles=role_names,
    )


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
