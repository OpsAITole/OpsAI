from fastapi import APIRouter

from app.api.v1 import auth, incidents, status

api_router = APIRouter()
api_router.include_router(status.router, tags=["status"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
