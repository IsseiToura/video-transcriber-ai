"""
Video schemas.
"""

from pydantic import BaseModel
from typing import Optional, Literal
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
    status: Literal["uploading", "uploaded", "processing", "completed", "error"] = "uploaded"
    
class ProcessResponse(BaseModel):
    """Video processing response schema."""
    message: str
    video_id: str
    status: str
    summary: str
