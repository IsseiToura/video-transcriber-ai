"""
API router for v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1 import auth, videos, admin

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
