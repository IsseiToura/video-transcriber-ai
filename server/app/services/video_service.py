"""
Video processing service.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from .audio_processor import AudioProcessor
from app.core.config import get_settings
from .text_compressor import TextCompressor

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
    
    def save_video(self, file_content: bytes, filename: str) -> str:
        """Save uploaded video or audio file."""
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
            "processed": False
        }
        self._save_metadata()
        
        return file_id
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get video or audio file information."""
        return self.metadata.get(video_id)
    
    def process_video(self, video_id: str) -> Dict:
        """Process video or audio: extract audio, transcribe, summarize."""
        logger.info(f"Starting video processing for ID: {video_id}")
        
        if video_id not in self.metadata:
            raise ValueError("File not found")
        
        file_info = self.metadata[video_id]
        file_path = Path(file_info["file_path"])
        
        if not file_path.exists():
            raise ValueError("File not found")
        
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
        
        # Generate summary (simple approach for now)
        summary = self._generate_summary(compressed_transcript)
        
        # Update metadata
        self.metadata[video_id].update({
            "processed": True,
            "transcript": compressed_transcript,
            "transcript_path": transcript_data["transcript_path"],
            "transcript_metadata_path": transcript_data["metadata_path"],
            "summary": summary,
            "audio_path": str(audio_path)
        })
        self._save_metadata()
        
        logger.info(f"Video processing completed for ID: {video_id}")
        
        return {
            "transcript": compressed_transcript,
            "summary": summary
        }
    
    def _save_transcript(self, video_id: str, segments) -> Dict:
        """Save transcript data to files."""
        # Extract full text
        full_text = self._extract_full_transcript(segments)
        
        # Save segments with metadata
        transcript_path = self.transcript_dir / f"{video_id}_transcript.json"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        # Save plain text
        text_path = self.transcript_dir / f"{video_id}_transcript.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Save metadata
        metadata_path = self.transcript_dir / f"{video_id}_metadata.json"
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
    
    def _generate_summary(self, transcript: str) -> str:
        """Generate summary from transcript."""
        # Simple summary for demo purposes
        words = transcript.split()
        if len(words) > 50:
            return " ".join(words[:50]) + "... (summary truncated)"
        return transcript
    
    def get_transcript(self, video_id: str, format: str = "full") -> Optional[str]:
        """Get video transcript in specified format."""
        video_info = self.get_video_info(video_id)
        if not video_info or not video_info.get("processed"):
            return None
        
        transcript_path = video_info.get("transcript_path")
        if not transcript_path:
            return None
        
        try:
            if format == "segments":
                # Return segments JSON
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif format == "text":
                # Return plain text
                text_path = Path(transcript_path).parent / f"{video_id}_transcript.txt"
                if text_path.exists():
                    with open(text_path, 'r', encoding='utf-8') as f:
                        return f.read()
            else:
                # Return full text (default)
                return self._extract_full_transcript_from_file(transcript_path)
        except Exception as e:
            print(f"Error reading transcript: {e}")
            return None
    
    def _extract_full_transcript_from_file(self, transcript_path: str) -> str:
        """Extract full transcript text from saved file."""
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                segments = json.load(f)
            return self._extract_full_transcript(segments)
        except Exception as e:
            print(f"Error extracting transcript from file: {e}")
            return ""
    
    def get_summary(self, video_id: str) -> Optional[str]:
        """Get video summary."""
        video_info = self.get_video_info(video_id)
        if video_info and video_info.get("processed"):
            return video_info.get("summary")
        return None
    
    def chat_with_video(self, video_id: str, question: str) -> str:
        """Simple RAG-based chat with video content."""
        transcript = self.get_transcript(video_id)
        if not transcript:
            return "Video has not been processed yet. Please process the video first."
        
        # Simple keyword-based response for demo
        question_lower = question.lower()
        transcript_lower = transcript.lower()
        
        if "what" in question_lower and "about" in question_lower:
            return f"Based on the video content: {transcript[:200]}..."
        elif "when" in question_lower:
            return "The video content doesn't specify exact timing information."
        elif "who" in question_lower:
            return "The video content doesn't specify specific people."
        else:
            return f"Based on the video transcript: {transcript[:150]}... This is a simplified response. In a full implementation, this would use proper RAG with vector embeddings and semantic search."
