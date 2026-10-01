"""OpsAI FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import check_db_connection


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    title="OpsAI API",
    description="Intelligent IT operations assistant (assistance-only MVP).",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Liveness probe — process is up."""
    return {"status": "ok", "service": "opsai-backend"}


@app.get("/readiness", tags=["system"])
def readiness() -> dict[str, str]:
    """Readiness probe — database is reachable."""
    try:
        check_db_connection()
    except Exception as exc:  # noqa: BLE001 — surface connectivity failures as 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"database unavailable: {exc}",
        ) from exc
    return {"status": "ready", "database": "ok"}
