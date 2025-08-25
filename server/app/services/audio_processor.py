"""
Audio processing service for video transcription.
"""

import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import shutil
import glob
import os
import whisper
from .text_compressor import TextCompressor

# Configure logging
logger = logging.getLogger(__name__)


def _transcribe_chunk_worker(chunk_path: str) -> Dict:
    """Worker function to transcribe a single audio chunk with Whisper.

    Note: This runs in a separate process; it loads the model inside the worker
    to avoid non-picklable state.
    """
    model = whisper.load_model("base")
    result = model.transcribe(chunk_path, word_timestamps=True)
    return result


class AudioProcessor:
    """Audio processing class for transcription and audio extraction."""
    
    def __init__(self):
        self.text_compressor = TextCompressor()
    
    def extract_audio(self, video_path: Path, audio_path: Path):
        """Extract audio from video using ffmpeg."""
        try:
            cmd = [
                "ffmpeg", "-i", str(video_path),
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                str(audio_path), "-y"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Audio extraction completed successfully. Video: {video_path}, Audio: {audio_path}")
        except subprocess.CalledProcessError:
            # Fallback: create empty audio file for demo
            audio_path.touch()
            logger.warning(f"Audio extraction failed, created empty audio file. Video: {video_path}, Audio: {audio_path}")
    
    def _get_audio_duration_seconds(self, audio_path: Path) -> float:
        """Return audio duration in seconds using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def _split_audio_into_chunks(self, audio_path: Path, chunk_seconds: int = 600) -> Tuple[Path, List[Path]]:
        """Split audio into N-minute chunks using ffmpeg segmenter. Returns (chunks_dir, chunk_paths)."""
        chunks_dir = audio_path.parent / f"{audio_path.stem}_chunks"
        if chunks_dir.exists():
            shutil.rmtree(chunks_dir)
        chunks_dir.mkdir(parents=True, exist_ok=True)

        chunk_pattern = str(chunks_dir / "chunk_%03d.wav")

        cmd = [
            "ffmpeg",
            "-i",
            str(audio_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-f",
            "segment",
            "-segment_time",
            str(chunk_seconds),
            chunk_pattern,
            "-y",
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        chunk_paths = sorted(Path(p) for p in glob.glob(str(chunks_dir / "chunk_*.wav")))
        return chunks_dir, chunk_paths

    def transcribe_audio(self, audio_path: Path) -> List[Dict]:
        """Transcribe audio by splitting into 10-minute chunks and processing in parallel (max_workers=2)."""
        try:
            # Split audio into 10-minute (600s) chunks
            chunk_seconds = 600
            chunks_dir, chunk_paths = self._split_audio_into_chunks(audio_path, chunk_seconds=chunk_seconds)

            if not chunk_paths:
                logger.warning(f"No chunks generated for audio: {audio_path}. Falling back to single-pass transcription.")
                single_result = _transcribe_chunk_worker(str(audio_path))
                segments = single_result.get("segments", [])
                logger.info(f"Audio transcription completed successfully. Audio: {audio_path}, Segments: {len(segments)}")
                return segments

            # Transcribe chunks in parallel with max_workers=2
            futures = {}
            with ProcessPoolExecutor(max_workers=2) as executor:
                for idx, chunk_path in enumerate(chunk_paths):
                    futures[executor.submit(_transcribe_chunk_worker, str(chunk_path))] = (idx, chunk_path)

                # Collect results
                indexed_results: List[Tuple[int, Dict]] = []
                for future in as_completed(futures):
                    idx, _ = futures[future]
                    res = future.result()
                    indexed_results.append((idx, res))

            # Sort by original order
            indexed_results.sort(key=lambda x: x[0])

            # Merge segments and adjust timestamps by chunk offset
            merged_segments: List[Dict] = []
            for idx, res in indexed_results:
                offset = idx * chunk_seconds
                for seg in res.get("segments", []):
                    seg_copy = dict(seg)
                    if "start" in seg_copy:
                        seg_copy["start"] = seg_copy["start"] + offset
                    if "end" in seg_copy:
                        seg_copy["end"] = seg_copy["end"] + offset
                    if "words" in seg_copy and isinstance(seg_copy["words"], list):
                        adjusted_words = []
                        for w in seg_copy["words"]:
                            w_copy = dict(w)
                            if "start" in w_copy:
                                w_copy["start"] = w_copy["start"] + offset
                            if "end" in w_copy:
                                w_copy["end"] = w_copy["end"] + offset
                            adjusted_words.append(w_copy)
                        seg_copy["words"] = adjusted_words
                    merged_segments.append(seg_copy)

            logger.info(
                f"Audio transcription completed successfully. Audio: {audio_path}, Segments: {len(merged_segments)}"
            )

            # Cleanup chunk directory
            try:
                shutil.rmtree(chunks_dir)
            except Exception:
                pass

            return merged_segments
            
        except Exception as e:
            logger.error(f"Error in transcription: {e}, Audio: {audio_path}")
            print(f"Error in transcription: {e}")
            # Fallback: return empty segments list
            return []
