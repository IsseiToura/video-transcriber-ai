"""
Video endpoints.
"""

import os
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends, Header
from fastapi.responses import FileResponse
from app.schemas.video import (
    VideoUploadResponse, VideoInfo, ChatRequest, 
    ChatResponse, ProcessResponse
)
from app.services.video_service import VideoService
from app.core.security import verify_token
from typing import Optional

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
        video_id = video_service.save_video(content, file.filename)
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
    
    return VideoInfo(
        video_id=video_id,
        filename=video_info["filename"],
        summary=video_info.get("summary"),
        transcript=video_info.get("transcript"),
        created_at=video_info["created_at"],
        processed=video_info.get("processed", False)
    )

@router.post("/{video_id}/process", response_model=ProcessResponse)
async def process_video(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Process video: extract audio, transcribe, summarize."""
    try:
        result = video_service.process_video(video_id)
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

@router.get("/{video_id}/transcript")
async def get_transcript(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get video transcript."""
    transcript = video_service.get_transcript(video_id)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found. Please process the video first."
        )
    
    return {"transcript": transcript}

@router.get("/{video_id}/summary")
async def get_summary(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get video summary."""
    summary = video_service.get_summary(video_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found. Please process the video first."
        )
    
    return {"summary": summary}

@router.post("/{video_id}/chat", response_model=ChatResponse)
async def chat_with_video(
    video_id: str,
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Chat with video content using RAG."""
    try:
        answer = video_service.chat_with_video(video_id, chat_request.question)
        return ChatResponse(
            answer=answer,
            sources=None  # In a full implementation, this would include source references
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )
