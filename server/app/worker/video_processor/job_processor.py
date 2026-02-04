"""
Video job processing logic.
"""

import logging
import time
from typing import Dict

from app.services.video_service import VideoService
from .timeout_manager import TimeoutManager

logger = logging.getLogger(__name__)


class JobProcessor:
    """Handles individual video processing jobs."""
    
    def __init__(self, sqs_client):
        self.video_service = VideoService()
        self.timeout_manager = TimeoutManager(sqs_client)
    
    # === Public methods ===
    
    def process_video_job(self, message: Dict, message_handler) -> bool:
        """
        Process video transcription job.
        
        Args:
            message: Raw SQS message
            message_handler: Message parser instance
            
        Returns:
            True if message should be deleted, False to retry
        """
        # Parse and validate message
        job_data = message_handler.parse_message(message)
        if not job_data or not message_handler.is_valid_job_data(job_data):
            logger.warning("Invalid job data, marking for deletion")
            return True  # Delete invalid messages
        
        # Extract job data
        video_id = job_data['video_id']
        
        try:
            success = self._process_single_job(job_data, message)
            
            if success:
                logger.info(f"Job completed successfully for video {video_id}")
                return True  # Delete message
            else:
                # Validation error (video not found, etc.)
                logger.warning(
                    f"Job failed validation for video {video_id}, "
                    f"deleted from queue"
                )
                return True  # Delete message (won't succeed on retry)
        
        except Exception as e:
            # Processing error - let SQS handle retries
            logger.error(
                f"Job failed for video {video_id}, will be retried by SQS: {e}"
            )
            return False  # Don't delete - retry later
    
    # === Private methods ===
    
    def _process_single_job(self, job_data: Dict, message: Dict) -> bool:
        """Process a single video job with visibility timeout management."""
        video_id = job_data['video_id']
        owner_username = job_data['owner_username']
        
        logger.info(f"Processing video job: {video_id} for user: {owner_username}")
        
        # Start timing the job
        start_time = time.time()
        
        try:
            # Process the video with timeout management
            result = self.timeout_manager.process_with_timeout_management(
                self.video_service, video_id, owner_username, message, start_time
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully processed video {video_id} in {processing_time:.2f} seconds: {result.get('summary', 'No summary')}")
            return True
            
        except ValueError as e:
            # Video not found or permission denied
            logger.error(f"Validation error processing video {video_id}: {e}")
            return False
        except Exception as e:
            # Processing error - this will trigger retry mechanism
            logger.error(f"Processing error for video {video_id}: {e}")
            raise
