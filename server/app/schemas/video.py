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
    s3_key: Optional[str] = None
    s3_bucket: Optional[str] = None
class VideoInfo(BaseModel):
    """Video information schema."""
    video_id: str
    filename: str
    summary: Optional[str] = None
    transcript: Optional[str] = None
    created_at: datetime
    status: Literal["uploading", "uploaded", "processing", "completed", "error"] = "uploaded"
    file_type: Optional[str] = None 
    s3_key: Optional[str] = None 
    s3_bucket: Optional[str] = None 
    
class ProcessResponse(BaseModel):
    """Video processing response schema."""
    message: str
    video_id: str
    status: str
    summary: str

class PresignedUrlResponse(BaseModel):
    """Presigned URL response schema."""
    uploadUrl: str
    fileId: str
    s3Key: str

class VideoMetadataRequest(BaseModel):
    """Video metadata request schema."""
    fileId: str
    filename: str
    s3Key: str

class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None
