from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Permission, Role, RolePermission, User, UserRole


def seed_roles(db: Session) -> None:
    roles = [
        {"name": "admin", "description": "System administrator"},
        {"name": "user", "description": "Regular user"},
    ]
    
    for role_data in roles:
        existing_role = db.execute(
            select(Role).where(Role.name == role_data["name"])
        ).scalar_one_or_none()
        
        if existing_role is None:
            db.add(Role(**role_data))


def seed_permissions(db: Session) -> None:
    permissions = [
        {
            "resource": "users",
            "action": "read",
            "description": "Read users",
        },
        {
            "resource": "users",
            "action": "update",
            "description": "Update users",
        },
        {
            "resource": "documents",
            "action": "read",
            "description": "Read documents",
        },
        {
            "resource": "reports",
            "action": "read",
            "description": "Read reports",
        },
        {
            "resource": "roles",
            "action": "manage",
            "description": "Manage roles",
        },
        {
            "resource": "permissions",
            "action": "manage",
            "description": "Manage permissions",
        },
    ]

    for permission_data in permissions:
        existing_permission = db.execute(
            select(Permission).where(
                Permission.resource == permission_data["resource"],
                Permission.action == permission_data["action"],
            )
        ).scalar_one_or_none()
        
        if existing_permission is None:
            db.add(Permission(**permission_data))


def seed_role_permissions(db: Session) -> None:
    roles = {
        role.name: role
        for role in db.execute(select(Role)).scalars().all()
    }

    permissions = {
        (permission.resource, permission.action): permission
        for permission in db.execute(select(Permission)).scalars().all()
    }
    
    role_permission_map = {
        "admin": [
            ("users", "read"),
            ("users", "update"),
            ("documents", "read"),
            ("reports", "read"),
            ("roles", "manage"),
            ("permissions", "manage"),
        ],
        "user": [
            ("users", "update"),
            ("documents", "read"),
        ],
    }
    
    for role_name, permission_keys in role_permission_map.items():
        role = roles.get(role_name)
        if role is None:
            continue
        
        for resource, action in permission_keys:
            permission = permissions.get((resource, action))
            if permission is None:
                continue
            
            existing_role_permission = db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            ).scalar_one_or_none()
            
            if existing_role_permission is None:
                db.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission.id,
                    )
                )


def seed_users(db: Session) -> None:
    users = [
        {
            "email": "admin@example.com",
            "password": "admin123",
            "last_name": "Admin",
            "first_name": "System",
            "middle_name": None,
            "status": "active",
        },
        {
            "email": "user@example.com",
            "password": "user123",
            "last_name": "User",
            "first_name": "Regular",
            "middle_name": None,
            "status": "active",
        },
    ]
    
    for user_data in users:
        existing_user = db.execute(
            select(User).where(User.email == user_data["email"])
        ).scalar_one_or_none()
        
        if existing_user is None:
            db.add(
                User(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    last_name=user_data["last_name"],
                    first_name=user_data["first_name"],
                    middle_name=user_data["middle_name"],
                    status=user_data["status"],
                )
            )


def seed_user_roles(db: Session) -> None:
    users = {
        user.email: user
        for user in db.execute(select(User)).scalars().all()
    }
    
    roles = {
        role.name: role
        for role in db.execute(select(Role)).scalars().all()
    }
    
    user_role_map = {
        "admin@example.com": "admin",
        "user@example.com": "user",
    }
    
    for user_email, role_name in user_role_map.items():
        user = users.get(user_email)
        role = roles.get(role_name)
        
        if user is None or role is None:
            continue
        
        existing_user_role = db.execute(
            select(UserRole).where(
                UserRole.user_id == user.id,
                UserRole.role_id == role.id,
            )
        ).scalar_one_or_none()
        
        if existing_user_role is None:
            db.add(
                UserRole(
                    user_id=user.id,
                    role_id=role.id,
                )
            )


def seed_database() -> None:
    db = SessionLocal()
    try:
        seed_roles(db)
        db.flush()
        seed_permissions(db)
        db.flush()
        seed_role_permissions(db)
        seed_users(db)
        db.flush()
        seed_user_roles(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



if __name__ == "__main__":
    seed_database()
