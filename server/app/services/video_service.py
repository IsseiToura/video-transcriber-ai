"""
Video processing service.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import boto3
from app.core.config import get_settings
from app.repositories.video_repository import VideoRepository
from app.schemas.video import Video
from app.clients.cache_client import cache_client

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()

class VideoService:
    """Video processing service class."""
    
    def __init__(self):
        self.videos_dir = Path(settings.UPLOAD_DIR) / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self._audio_processor = None  # Lazy load to avoid importing whisper unnecessarily
        self._text_compressor = None  # Lazy load to avoid importing numpy, torch, etc.
        self._summary_generator = None  # Lazy load to avoid unnecessary imports
        self.s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
        self.s3_bucket = settings.S3_BUCKET
        # DynamoDB repository
        self.video_repo = VideoRepository()
    
    @property
    def audio_processor(self):
        """Lazy load AudioProcessor only when needed (to avoid importing whisper)."""
        if self._audio_processor is None:
            from .audio_processor import AudioProcessor
            self._audio_processor = AudioProcessor()
        return self._audio_processor
    
    @property
    def text_compressor(self):
        """Lazy load TextCompressor only when needed (to avoid importing numpy, torch, etc.)."""
        if self._text_compressor is None:
            from .text_compressor import TextCompressor
            self._text_compressor = TextCompressor()
        return self._text_compressor
    
    @property
    def summary_generator(self):
        """Lazy load SummaryGenerator only when needed."""
        if self._summary_generator is None:
            from .summary_generator import SummaryGenerator
            self._summary_generator = SummaryGenerator()
        return self._summary_generator
    
    def save_video_metadata(self, file_id: str, filename: str, s3_key: str, owner_username: str) -> str:
        """Save video metadata after S3 upload."""
        # Determine file type
        file_extension = filename.split(".")[-1].lower()
        is_audio = file_extension in ["mp3", "wav", "aac", "ogg", "flac", "m4a", "wma"]
        
        # Save metadata to DynamoDB
        self.video_repo.save_metadata(
            video_id=file_id,
            filename=filename,
            s3_key=s3_key,
            s3_bucket=self.s3_bucket,
            file_type="audio" if is_audio else "video",
            owner_username=owner_username,
            status="uploaded",
        )
        
        # Invalidate cache for this video
        self._invalidate_cache(file_id, owner_username, "new video")
        
        return file_id
    
    def get_video_info(self, video_id: str, owner_username: str) -> Optional[Video]:
        """Get video or audio file information with caching."""
        # Try to get from cache first
        if cache_client.is_available():
            cache_key = cache_client.get_video_info_key(video_id, owner_username)
            cached_data = cache_client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for video {video_id}")
                # Handle cached data format (Python dict string representation with function calls)
                if isinstance(cached_data, bytes):
                    try:
                        # Try pickle decode first (for data with function calls like Decimal)
                        import pickle
                        cached_data = pickle.loads(cached_data)
                    except (pickle.PickleError, UnicodeDecodeError):
                        try:
                            # Fallback to eval for Python dict string representation
                            data_str = cached_data.decode('utf-8')
                            # Use eval with restricted globals and Decimal support
                            from decimal import Decimal
                            safe_globals = {"__builtins__": {}, "Decimal": Decimal}
                            cached_data = eval(data_str, safe_globals, {})
                        except Exception as e:
                            logger.warning(f"Failed to decode cached data for video {video_id}: {e}")
                            cached_data = None
                elif isinstance(cached_data, str):
                    try:
                        # Use eval with restricted globals and Decimal support
                        from decimal import Decimal
                        safe_globals = {"__builtins__": {}, "Decimal": Decimal}
                        cached_data = eval(cached_data, safe_globals, {})
                    except Exception as e:
                        logger.warning(f"Failed to decode cached string data for video {video_id}: {e}")
                        cached_data = None
                # Convert cached dict to Video domain model
                if cached_data and isinstance(cached_data, dict):
                    return Video.from_dict(cached_data)
                return None
        
        # If not in cache, get from database (already returns Video)
        video = self.video_repo.get(video_id, owner_username)
        
        # Cache the result if available (store as dict for cache compatibility)
        if video and cache_client.is_available():
            cache_key = cache_client.get_video_info_key(video_id, owner_username)
            cache_client.set(cache_key, video.model_dump())
            logger.debug(f"Cached video info for {video_id}")
        
        return video
    
    def get_all_videos(self, owner_username: str) -> List[Video]:
        """Get all videos for a specific owner."""
        resp = self.video_repo.list_by_owner(owner_username)
        return resp.get("items", [])
    
    def delete_video(self, video_id: str, owner_username: str) -> bool:
        """Delete files whose paths are stored in metadata, then remove metadata entry.
        
        Returns True if the video existed and was removed, else False.
        """
        video = self.video_repo.get(video_id, owner_username)
        if not video:
            return False
        if video.owner_username != owner_username:
            # Do not allow deleting others' videos
            return False
        
        # Delete S3 file if it exists
        if video.s3_key:
            try:
                self.s3_client.delete_object(Bucket=self.s3_bucket, Key=video.s3_key)
            except Exception:
                # Keep deletion best-effort; do not raise
                pass
        
        # Delete transcript artifacts from S3 if present
        for tk in [
            video.transcript_s3_key,
            video.transcript_text_s3_key,
            video.transcript_metadata_s3_key,
        ]:
            if not tk:
                continue
            try:
                self.s3_client.delete_object(Bucket=self.s3_bucket, Key=tk)
            except Exception:
                pass
        
        self.video_repo.delete(video_id, owner_username)
        
        # Invalidate cache when video is deleted
        self._invalidate_cache(video_id, owner_username, "deleted")
        
        return True
    
    def process_video(self, video_id: str, owner_username: str) -> Dict:
        """Process video or audio: extract audio, transcribe, summarize."""
        logger.info(f"Starting video processing for ID: {video_id}")
        
        video = self.video_repo.get(video_id, owner_username)
        if not video:
            raise ValueError("File not found")
        if not self._assert_ownership(video_id, owner_username):
            raise ValueError("Not allowed")
        
        # Download file from S3
        if not video.s3_key:
            raise ValueError("S3 key not found for this file")
        file_path = self.videos_dir / f"{video_id}_{video.filename}"
        try:
            self.s3_client.download_file(self.s3_bucket, video.s3_key, str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to download file from S3: {str(e)}")
        
        # Update status to processing
        self.video_repo.update_fields(video_id, {"status": "processing"}, owner_username)
        
        # Invalidate cache when status changes
        self._invalidate_cache(video_id, owner_username, "status changed to processing")
        
        try:
            # For audio files, use directly; for video files, extract audio
            if video.file_type == "audio":
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
            self.video_repo.update_fields(video_id, {"status": "error"}, owner_username)
            
            # Invalidate cache when status changes to error
            self._invalidate_cache(video_id, owner_username, "status changed to error")
            
            logger.error(f"Error processing video {video_id}: {e}")
            raise
        
        # Update metadata
        # Save transcript data to the same video record
        self.video_repo.save_transcript_data(
            video_id=video_id,
            transcript_text=compressed_transcript,
            summary=summary,
            segments_count=transcript_data.get("segments_count", 0),
            total_characters=transcript_data.get("total_characters", 0),
            total_words=transcript_data.get("total_words", 0),
            owner_username=owner_username,
            transcript_s3_key=transcript_data.get("transcript_s3_key"),
            transcript_text_s3_key=transcript_data.get("text_s3_key"),
            transcript_metadata_s3_key=transcript_data.get("metadata_s3_key"),
        )
        # Mark processing as completed upon successful transcript save
        self.video_repo.update_fields(video_id, {"status": "completed"}, owner_username)
        
        # Invalidate cache when processing completes
        self._invalidate_cache(video_id, owner_username, "status changed to completed")
        
        # Clean up temporary files downloaded from S3
        if video.s3_key:
            try:
                if file_path.exists():
                    file_path.unlink()
                if audio_path.exists() and audio_path != file_path:
                    audio_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to clean up temporary files: {e}")
        
        logger.info(f"Video processing completed for ID: {video_id}")
        
        return {
            "summary": summary
        }
    
    def get_transcript(self, video_id: str, owner_username: str) -> Optional[str]:
        """Get transcript.txt content for the given video."""
        video = self.get_video_info(video_id, owner_username)
        if not video or video.status != "completed":
            return None
        if video.owner_username != owner_username:
            return None
            
        try:
            if not video.transcript_text_s3_key:
                return None
            obj = self.s3_client.get_object(Bucket=self.s3_bucket, Key=video.transcript_text_s3_key)
            return obj["Body"].read().decode("utf-8")
        except Exception:
            return None
    
    def get_summary(self, video_id: str, owner_username: str) -> Optional[str]:
        """Get video summary."""
        video = self.get_video_info(video_id, owner_username)
        if video and video.status == "completed":
            if video.owner_username == owner_username:
                return video.summary
        return None
    
    # === Private methods ===
    
    def _invalidate_cache(self, video_id: str, owner_username: str, reason: str = "") -> None:
        """Invalidate cache for video."""
        if not cache_client.is_available():
            return
        
        cache_client.invalidate_video_info(video_id, owner_username)
        if reason:
            logger.debug(f"Invalidated cache for video {video_id}: {reason}")
        else:
            logger.debug(f"Invalidated cache for video {video_id}")
    
    def _assert_ownership(self, video_id: str, owner_username: str) -> bool:
        """Return True if the given user owns the video_id."""
        video = self.video_repo.get(video_id, owner_username)
        if not video:
            return False
        return video.owner_username == owner_username
    
    def _save_transcript(self, video_id: str, segments) -> Dict:
        """Save transcript data to S3 (JSON, TXT, and metadata)."""
        # Extract full text
        full_text = self._extract_full_transcript(segments)

        # Prepare S3 keys
        base_prefix = f"transcripts/{video_id}"
        transcript_s3_key = f"{base_prefix}/transcript.json"
        text_s3_key = f"{base_prefix}/transcript.txt"
        metadata_s3_key = f"{base_prefix}/metadata.json"

        # Build payloads
        transcript_json_bytes = json.dumps(segments, ensure_ascii=False, indent=2).encode("utf-8")
        text_bytes = full_text.encode("utf-8")
        transcript_metadata = {
            "video_id": video_id,
            "created_at": datetime.now().isoformat(),
            "segments_count": len(segments) if isinstance(segments, list) else 0,
            "total_characters": len(full_text),
            "total_words": len(full_text.split()),
            "transcript_s3_key": transcript_s3_key,
            "text_s3_key": text_s3_key,
        }
        metadata_json_bytes = json.dumps(transcript_metadata, ensure_ascii=False, indent=2).encode("utf-8")

        # Upload to S3
        self.s3_client.put_object(Bucket=self.s3_bucket, Key=transcript_s3_key, Body=transcript_json_bytes, ContentType="application/json; charset=utf-8")
        self.s3_client.put_object(Bucket=self.s3_bucket, Key=text_s3_key, Body=text_bytes, ContentType="text/plain; charset=utf-8")
        self.s3_client.put_object(Bucket=self.s3_bucket, Key=metadata_s3_key, Body=metadata_json_bytes, ContentType="application/json; charset=utf-8")

        # Return keys and stats for further saving
        return {
            "transcript_s3_key": transcript_s3_key,
            "text_s3_key": text_s3_key,
            "metadata_s3_key": metadata_s3_key,
            "segments_count": transcript_metadata["segments_count"],
            "total_characters": transcript_metadata["total_characters"],
            "total_words": transcript_metadata["total_words"],
            "full_text": full_text,
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