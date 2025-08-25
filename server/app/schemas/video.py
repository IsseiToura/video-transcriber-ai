"""
Video schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoUploadResponse(BaseModel):
    """Video upload response schema."""
    video_id: str
    filename: str
    message: str


class VideoInfo(BaseModel):
    """Video information schema."""
    video_id: str
    filename: str
    summary: Optional[str] = None
    transcript: Optional[str] = None
    created_at: datetime
    processed: bool = False


class ChatRequest(BaseModel):
    """Chat request schema."""
    question: str


class ChatResponse(BaseModel):
    """Chat response schema."""
    answer: str
    sources: Optional[list] = None


class ProcessResponse(BaseModel):
    """Video processing response schema."""
    message: str
    video_id: str
    status: str
    summary: str
