"""Auth route stubs — future contracts (Phase 2+)."""

from fastapi import APIRouter, HTTPException, status

from app.schemas import TokenResponse, UserCreate, UserRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def register(_payload: UserCreate) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth not implemented in Phase 1")


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def login(_payload: UserCreate) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth not implemented in Phase 1")


@router.get("/me", response_model=UserRead, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def me() -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth not implemented in Phase 1")
