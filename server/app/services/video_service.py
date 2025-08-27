"""
Video processing service.
"""

import json
import shutil
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import os
from .audio_processor import AudioProcessor
from app.core.config import get_settings
from .text_compressor import TextCompressor
from .summary_generator import SummaryGenerator

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()

class VideoService:
    """Video processing service class."""
    
    def __init__(self):
        self.videos_dir = Path(settings.UPLOAD_DIR) / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.transcript_dir = Path(settings.UPLOAD_DIR) / "transcripts"
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.videos_dir / "metadata.json"
        self.audio_processor = AudioProcessor()
        self.text_compressor = TextCompressor()
        self.summary_generator = SummaryGenerator()
        self._load_metadata()
    
    def _load_metadata(self):
        """Load video metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
            self._save_metadata()
    
    def _save_metadata(self):
        """Save video metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def save_video(self, file_content: bytes, filename: str, owner_username: str) -> str:
        """Save uploaded video or audio file and record owner."""
        file_id = str(uuid.uuid4())
        file_path = self.videos_dir / f"{file_id}_{filename}"
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Determine file type
        file_extension = filename.split(".")[-1].lower()
        is_audio = file_extension in ["mp3", "wav", "aac", "ogg", "flac", "m4a", "wma"]
        
        # Save metadata
        self.metadata[file_id] = {
            "filename": filename,
            "file_path": str(file_path),
            "file_type": "audio" if is_audio else "video",
            "created_at": datetime.now().isoformat(),
            "status": "uploading",
            "owner_username": owner_username,
        }
        self._save_metadata()
        
        # Update status to uploaded after successful save
        self.metadata[file_id]["status"] = "uploaded"
        self._save_metadata()
        
        return file_id
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get video or audio file information."""
        return self.metadata.get(video_id)
    
    def get_all_videos(self, owner_username: str) -> List[Dict]:
        """Get all videos for a specific owner."""
        videos = []
        for video_id, video_info in self.metadata.items():
            if video_info.get("owner_username") != owner_username:
                continue
            videos.append({
                "video_id": video_id,
                "filename": video_info["filename"],
                "summary": video_info.get("summary"),
                "transcript": video_info.get("transcript"),
                "created_at": video_info["created_at"],
                "status": video_info.get("status", "uploaded")
            })
        return videos

    def _assert_ownership(self, video_id: str, owner_username: str) -> bool:
        """Return True if the given user owns the video_id."""
        info = self.metadata.get(video_id)
        if not info:
            return False
        return info.get("owner_username") == owner_username
    
    def delete_video(self, video_id: str, owner_username: str) -> bool:
        """Delete files whose paths are stored in metadata, then remove metadata entry.
        
        Returns True if the video existed and was removed, else False.
        """
        info = self.metadata.get(video_id)
        if not info:
            return False
        if info.get("owner_username") != owner_username:
            # Do not allow deleting others' videos
            return False
        
        for key in ["file_path", "audio_path", "transcript_path", "transcript_metadata_path"]:
            path_str = info.get(key)
            if not path_str:
                continue
            path = Path(path_str)
            try:
                if path.exists() and path.is_file():
                    path.unlink()
            except Exception:
                # Keep deletion best-effort; do not raise
                pass

        # Also attempt to remove the per-video transcript directory if present (new structure only)
        tp = info.get("transcript_path")
        if tp:
            try:
                transcript_dir = Path(tp).parent
                # Only remove if this is exactly .../transcripts/{video_id}
                if (
                    transcript_dir.exists()
                    and transcript_dir.is_dir()
                    and transcript_dir.parent == self.transcript_dir
                    and transcript_dir.name == video_id
                ):
                    shutil.rmtree(transcript_dir)
            except Exception:
                pass
        
        self.metadata.pop(video_id, None)
        self._save_metadata()
        return True
    
    def process_video(self, video_id: str, owner_username: str) -> Dict:
        """Process video or audio: extract audio, transcribe, summarize."""
        logger.info(f"Starting video processing for ID: {video_id}")
        
        if video_id not in self.metadata:
            raise ValueError("File not found")
        if not self._assert_ownership(video_id, owner_username):
            raise ValueError("Not allowed")
        
        file_info = self.metadata[video_id]
        file_path = Path(file_info["file_path"])
        
        if not file_path.exists():
            raise ValueError("File not found")
        
        # Update status to processing
        self.metadata[video_id]["status"] = "processing"
        self._save_metadata()
        
        try:
            # For audio files, use directly; for video files, extract audio
            if file_info["file_type"] == "audio":
                audio_path = file_path
            else:
                # Extract audio from video
                audio_path = self.videos_dir / f"{video_id}_audio.wav"
                self.audio_processor.extract_audio(file_path, audio_path)
            
            # Transcribe audio and save transcript
            segments = self.audio_processor.transcribe_audio(audio_path)
            transcript_data = self._save_transcript(video_id, segments)

            # Compress transcript
            compressed_transcript = self.text_compressor.compress_segments(segments)
            
            # Generate summary
            summary = self.summary_generator.generate_summary(compressed_transcript)
        except Exception as e:
            # Update status to error on failure
            self.metadata[video_id]["status"] = "error"
            self._save_metadata()
            logger.error(f"Error processing video {video_id}: {e}")
            raise
        
        # Update metadata
        self.metadata[video_id].update({
            "status": "completed",
            "transcript": compressed_transcript,
            "transcript_path": transcript_data["transcript_path"],
            "transcript_metadata_path": transcript_data["metadata_path"],
            "summary": summary,
            "audio_path": str(audio_path)
        })
        self._save_metadata()
        
        logger.info(f"Video processing completed for ID: {video_id}")
        
        return {
            "summary": summary
        }
    
    def _save_transcript(self, video_id: str, segments) -> Dict:
        """Save transcript data to files."""
        # Extract full text
        full_text = self._extract_full_transcript(segments)
        
        # Create per-video transcript directory
        video_transcript_dir = self.transcript_dir / video_id
        video_transcript_dir.mkdir(parents=True, exist_ok=True)

        # Save segments with metadata
        transcript_path = video_transcript_dir / "transcript.json"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        # Save plain text
        text_path = video_transcript_dir / "transcript.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Save metadata
        metadata_path = video_transcript_dir / "metadata.json"
        transcript_metadata = {
            "video_id": video_id,
            "created_at": datetime.now().isoformat(),
            "segments_count": len(segments) if isinstance(segments, list) else 0,
            "total_characters": len(full_text),
            "total_words": len(full_text.split()),
            "transcript_file": str(transcript_path),
            "text_file": str(text_path)
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_metadata, f, ensure_ascii=False, indent=2)
        
        return {
            "transcript_path": str(transcript_path),
            "text_path": str(text_path),
            "metadata_path": str(metadata_path),
            "full_text": full_text
        }
    
    def _extract_full_transcript(self, segments) -> str:
        """Extract full transcript text from segments."""
        if isinstance(segments, str):
            return segments
        
        if not segments or not isinstance(segments, list):
            return ""
        
        # Extract text from each segment and join
        transcript_parts = []
        for segment in segments:
            if isinstance(segment, dict) and "text" in segment:
                text = segment["text"].strip()
                if text:
                    transcript_parts.append(text)
        
        return " ".join(transcript_parts)
    
    def get_transcript(self, video_id: str, owner_username: str) -> Optional[str]:
        """Get transcript.txt content for the given video."""
        video_info = self.get_video_info(video_id)
        if not video_info or video_info.get("status") != "completed":
            return None
        if video_info.get("owner_username") != owner_username:
            return None
        
        transcript_path = video_info.get("transcript_path")
        if not transcript_path:
            return None
        
        try:
            # Always return the plain text transcript stored as transcript.txt
            parent_dir = Path(transcript_path).parent
            text_path = parent_dir / "transcript.txt"
            if text_path.exists():
                with open(text_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading transcript: {e}")
            return None
    
    def get_summary(self, video_id: str, owner_username: str) -> Optional[str]:
        """Get video summary."""
        video_info = self.get_video_info(video_id)
        if video_info and video_info.get("status") == "completed":
            if video_info.get("owner_username") == owner_username:
                return video_info.get("summary")
        return None
    
