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
    
    def process_single_job(self, job_data: Dict, message: Dict) -> bool:
        """Process a single video job with visibility timeout management."""
        video_id = job_data['video_id']
        owner_username = job_data['owner_username']
        
        logger.info(f"Processing video job: {video_id} for user: {owner_username}")
        
        # Start timing the job
        start_time = time.time()
        
        try:
            # Process the video using the existing VideoService with timeout management
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
