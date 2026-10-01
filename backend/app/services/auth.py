"""Authentication business logic."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User, UserRole
from app.repositories import users as users_repo
from app.schemas import TokenResponse, UserCreate, UserLogin, UserRead


def register_user(db: Session, payload: UserCreate) -> User:
    existing = users_repo.get_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este correo ya está registrado",
        )

    # Public registration defaults to VIEWER. Elevated roles only for first-user bootstrap.
    role = UserRole.VIEWER
    if payload.role in {UserRole.ADMIN, UserRole.TECHNICIAN}:
        any_user = db.scalar(select(User.id).limit(1))
        if any_user is None:
            role = payload.role

    return users_repo.create_user(
        db,
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
        role=role,
    )


def authenticate_user(db: Session, payload: UserLogin) -> TokenResponse:
    user = users_repo.get_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    token = create_access_token(subject=str(user.id), role=user.role)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


def user_to_read(user: User) -> UserRead:
    return UserRead.model_validate(user)
