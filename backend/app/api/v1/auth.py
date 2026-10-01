"""Auth routes — register, login, logout, me, and OAuth stubs."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import CurrentUser
from app.schemas import MessageResponse, OAuthProviderStub, TokenResponse, UserCreate, UserLogin, UserRead
from app.services import auth as auth_service

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserRead:
    user = auth_service.register_user(db, payload)
    return auth_service.user_to_read(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    return auth_service.authenticate_user(db, payload)


@router.post("/logout", response_model=MessageResponse)
def logout(_user: CurrentUser) -> MessageResponse:
    """Client should discard the JWT. Stateless logout acknowledges the session end."""
    return MessageResponse(message="Sesión cerrada")


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> UserRead:
    return auth_service.user_to_read(user)


# --- OAuth stubs (no implementation in Phase 2) ---


@router.get("/oauth/{provider}", response_model=OAuthProviderStub, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def oauth_start(provider: str) -> OAuthProviderStub:
    return OAuthProviderStub(
        provider=provider,
        detail=f"El proveedor OAuth '{provider}' aún no está implementado",
    )


@router.get(
    "/oauth/{provider}/callback",
    response_model=OAuthProviderStub,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
def oauth_callback(provider: str) -> OAuthProviderStub:
    return OAuthProviderStub(
        provider=provider,
        detail=f"El callback OAuth de '{provider}' aún no está implementado",
    )
