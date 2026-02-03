"""
Video endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import PlainTextResponse
from app.schemas.video import (
    VideoUploadResponse, VideoInfo, PresignedUrlResponse, VideoMetadataRequest
)
from typing import List
from app.services.video_service import VideoService
from app.clients.s3_client import create_presigned_url
from app.core.dependencies import get_current_user

router = APIRouter()
video_service = VideoService()

@router.get("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
    filename: str = Query(...),
    content_type: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate presigned URL for S3 upload."""
    # Validate file type
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_extension = filename.split(".")[-1].lower()
    # Support both video and audio formats
    supported_formats = [
        # Video formats
        "mp4", "avi", "mov", "wmv", "flv", "webm",
        # Audio formats
        "mp3", "wav", "aac", "ogg", "flac", "m4a", "wma"
    ]
    if file_extension not in supported_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Supported formats: video (mp4, avi, mov, wmv, flv, webm) and audio (mp3, wav, aac, ogg, flac, m4a, wma)"
        )
    
    try:
        result = create_presigned_url(filename, content_type)
        return PresignedUrlResponse(
            uploadUrl=result["uploadUrl"],
            fileId=result["fileId"],
            s3Key=result["s3Key"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating presigned URL: {str(e)}"
        )

@router.post("/metadata", response_model=VideoUploadResponse)
async def save_video_metadata(
    metadata: VideoMetadataRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save video metadata after S3 upload."""
    try:
        video_id = video_service.save_video_metadata(
            metadata.fileId,
            metadata.filename,
            metadata.s3Key,
            current_user["username"]
        )
        return VideoUploadResponse(
            video_id=video_id,
            filename=metadata.filename,
            message="Video metadata saved successfully",
            s3_key=metadata.s3Key,
            s3_bucket=video_service.s3_bucket
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving video metadata: {str(e)}"
        )

@router.get("/", response_model=List[VideoInfo])
async def get_videos(
    current_user: dict = Depends(get_current_user)
):
    """Get all videos for the current user."""
    try:
        videos = video_service.get_all_videos(current_user["username"])
        return [VideoInfo.from_domain(video) for video in videos]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching videos: {str(e)}"
        )

@router.get("/{video_id}", response_model=VideoInfo)
async def get_video_info(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get video information."""
    video = video_service.get_video_info(video_id, current_user["username"])
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    if video.owner_username != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    return VideoInfo.from_domain(video)

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a video and its associated artifacts."""
    deleted = video_service.delete_video(video_id, current_user["username"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    # 204 No Content
    return None


@router.get("/{video_id}/transcript", response_class=PlainTextResponse)
async def get_transcript_text(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get video transcript as plain text (transcript.txt content)."""
    transcript = video_service.get_transcript(video_id, current_user["username"])
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found. Please process the video first."
        )
    return transcript

@router.get("/{video_id}/summary")
async def get_summary(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get video summary."""
    summary = video_service.get_summary(video_id, current_user["username"])
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found. Please process the video first."
        )
    
    return {"summary": summary}