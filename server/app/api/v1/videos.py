"""
Video endpoints.
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends, Header
from fastapi.responses import PlainTextResponse
from app.schemas.video import (
    VideoUploadResponse, VideoInfo, ProcessResponse
)
from typing import List
from app.services.video_service import VideoService
from app.core.security import verify_token

router = APIRouter()
video_service = VideoService()

def get_current_user(authorization: str = Header(None)):
    """Get current user from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload video or audio file."""
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_extension = file.filename.split(".")[-1].lower()
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
    
    # Read file content
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Save video
    try:
        video_id = video_service.save_video(content, file.filename, current_user["username"])
        return VideoUploadResponse(
            video_id=video_id,
            filename=file.filename,
            message="Video uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving video: {str(e)}"
        )

@router.get("/", response_model=List[VideoInfo])
async def get_videos(
    current_user: dict = Depends(get_current_user)
):
    """Get all videos for the current user."""
    try:
        videos = video_service.get_all_videos(current_user["username"])
        return videos
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
    video_info = video_service.get_video_info(video_id)
    if not video_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    if video_info.get("owner_username") != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    return VideoInfo(
        video_id=video_id,
        filename=video_info["filename"],
        summary=video_info.get("summary"),
        transcript=video_info.get("transcript"),
        created_at=video_info["created_at"],
        status=video_info.get("status", "uploaded")
    )

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

@router.post("/{video_id}/process", response_model=ProcessResponse)
async def process_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Process video: extract audio, transcribe, summarize."""
    try:
        result = video_service.process_video(video_id, current_user["username"])
        return ProcessResponse(
            message="Video processed successfully",
            video_id=video_id,
            status="completed",
            summary=result["summary"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing video: {str(e)}"
        )

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