"""User data-access helpers."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserRole


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_by_id(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def create_user(
    db: Session,
    *,
    email: str,
    password_hash: str,
    name: str,
    role: UserRole = UserRole.VIEWER,
) -> User:
    user = User(
        email=email.lower(),
        password_hash=password_hash,
        name=name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
