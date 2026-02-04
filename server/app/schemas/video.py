"""
Video schemas.
"""

from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from datetime import datetime


# =============================================================================
# Domain Model (Core model used across the application)
# =============================================================================

class Video(BaseModel):
    """
    Video domain model - Core type used across the application.
    Used in Repository and Service layers.
    """
    video_id: str
    filename: str
    s3_key: str
    s3_bucket: str
    file_type: str
    owner_username: str
    created_at: str
    status: Literal["uploading", "uploaded", "processing", "completed", "error", "failed"] = "uploaded"
    
    # Fields added after processing
    transcript: Optional[str] = None
    summary: Optional[str] = None
    segments_count: Optional[int] = None
    total_characters: Optional[int] = None
    total_words: Optional[int] = None
    transcript_s3_key: Optional[str] = None
    transcript_text_s3_key: Optional[str] = None
    transcript_metadata_s3_key: Optional[str] = None
    audio_path: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Video":
        """Convert DynamoDB Item (dict) to domain model"""
        return cls(
            video_id=data["video_id"],
            filename=data["filename"],
            s3_key=data.get("s3_key", ""),
            s3_bucket=data.get("s3_bucket", ""),
            file_type=data.get("file_type", ""),
            owner_username=data.get("owner_username", ""),
            created_at=data.get("created_at", ""),
            status=data.get("status", "uploaded"),
            transcript=data.get("transcript"),
            summary=data.get("summary"),
            segments_count=data.get("segments_count"),
            total_characters=data.get("total_characters"),
            total_words=data.get("total_words"),
            transcript_s3_key=data.get("transcript_s3_key"),
            transcript_text_s3_key=data.get("transcript_text_s3_key"),
            transcript_metadata_s3_key=data.get("transcript_metadata_s3_key"),
            audio_path=data.get("audio_path"),
        )


# =============================================================================
# API Schemas (for request/response)
# =============================================================================

class VideoUploadResponse(BaseModel):
    """Video upload response schema."""
    video_id: str
    filename: str
    message: str
    s3_key: Optional[str] = None
    s3_bucket: Optional[str] = None
class VideoInfo(BaseModel):
    """Video information schema - for API response"""
    video_id: str
    filename: str
    summary: Optional[str] = None
    transcript: Optional[str] = None
    created_at: datetime
    status: Literal["uploading", "uploaded", "processing", "completed", "error", "failed"] = "uploaded"
    file_type: Optional[str] = None 
    s3_key: Optional[str] = None 
    s3_bucket: Optional[str] = None 
    
    @classmethod
    def from_domain(cls, video: "Video") -> "VideoInfo":
        """Convert domain model to API response"""
        return cls(
            video_id=video.video_id,
            filename=video.filename,
            summary=video.summary,
            transcript=video.transcript,
            created_at=datetime.fromisoformat(video.created_at),
            status=video.status,
            file_type=video.file_type,
            s3_key=video.s3_key,
            s3_bucket=video.s3_bucket,
        )
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
