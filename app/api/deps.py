from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Permission, RolePermission, User, UserRole
from app.models import Session as UserSession


bearer_scheme = HTTPBearer()


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )
        
    return credentials.credentials


def get_current_user(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db),
) -> User:
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
        
    user = db.execute(
        select(User).where(
            User.id == session.user_id,
            User.status == "active",
        )
    ).scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated",
        )
    
    return user


def require_permission(resource: str, action: str):
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> None:
        user_role_ids = db.execute(
            select(UserRole.role_id).where(UserRole.user_id == current_user.id)
        ).scalars().all()

        if not user_role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
            
        permission = db.execute(
            select(Permission).where(
                Permission.resource == resource,
                Permission.action == action,
            )
        ).scalar_one_or_none()
        
        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission is not configured",
            )

        role_permission = db.execute(
            select(RolePermission).where(
                RolePermission.role_id.in_(user_role_ids),
                RolePermission.permission_id == permission.id,
            )
        ).scalars().first()
        
        if role_permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
            
    return permission_checker
