from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.models import Permission, Role, RolePermission, User, UserRole
from app.schemas.permission import AssignPermissionRequest, PermissionResponse
from app.schemas.role import AssignRoleRequest, RoleResponse


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/roles", response_model=list[RoleResponse])
def get_roles(
    _: None = Depends(require_permission("roles", "manage")),
    db: Session = Depends(get_db),
) -> Sequence[Role]:
    roles = db.execute(select(Role)).scalars().all()
    return roles


@router.get("/permissions", response_model=list[PermissionResponse])
def get_permissions(
    _: None = Depends(require_permission("permissions", "manage")),
    db: Session = Depends(get_db),
) -> Sequence[Permission]:
    permissions = db.execute(select(Permission)).scalars().all()
    return permissions


@router.post("/users/{user_id}/roles")
def assign_role_to_user(
    user_id: int,
    data: AssignRoleRequest,
    _: None = Depends(require_permission("roles", "manage")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    user = db.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    role = db.execute(
        select(Role).where(Role.id == data.role_id)
    ).scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    existing_user_role = db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
    ).scalar_one_or_none()

    if existing_user_role is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already assigned to user",
        )

    db.add(
        UserRole(
            user_id=user.id,
            role_id=role.id,
        )
    )
    db.commit()

    return {"message": "Role assigned successfully"}


@router.post("/roles/{role_id}/permissions")
def assign_permission_to_role(
    role_id: int,
    data: AssignPermissionRequest,
    _: None = Depends(require_permission("permissions", "manage")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    role = db.execute(
        select(Role).where(Role.id == role_id)
    ).scalar_one_or_none()
    
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    permission = db.execute(
        select(Permission).where(Permission.id == data.permission_id)
    ).scalar_one_or_none()
    
    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    existing_role_permission = db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
    ).scalar_one_or_none()
    
    if existing_role_permission is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already assigned to role",
        )

    db.add(
        RolePermission(
            role_id=role.id,
            permission_id=permission.id,
        )
    )
    db.commit()

    return {"message": "Permission assigned successfully"}
