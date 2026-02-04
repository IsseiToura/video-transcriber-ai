"""
DLQ job processing logic for failed video jobs.
"""

import logging
from typing import Dict

from app.services.video_service import VideoService

logger = logging.getLogger(__name__)


class DLQJobProcessor:
    """Handles DLQ video job processing - marking failed jobs."""
    
    def __init__(self):
        self.video_service = VideoService()
    
    # === Public methods ===
    
    def process_failed_video_job(
        self, 
        message: Dict, 
        message_handler
    ) -> bool:
        """
        Process a failed video processing job from DLQ.
        
        Args:
            message: Raw SQS message from DLQ
            message_handler: Message parser instance
            
        Returns:
            True if message should be deleted, False to retry
        """
        # Parse and validate message
        job_data = message_handler.parse_message(message)
        if not job_data or not message_handler.is_valid_job_data(job_data):
            logger.warning("Invalid job data in DLQ message, marking for deletion")
            return True  # Delete invalid messages
        
        # Extract job data
        video_id = job_data['video_id']
        owner_username = job_data['owner_username']
        
        logger.warning(
            f"Processing failed video job from DLQ: {video_id} "
            f"for user: {owner_username}"
        )
        
        try:
            # Execute business logic
            self._mark_video_as_failed(video_id, owner_username)
            
            # Log permanent failure
            logger.error(
                f"Video processing permanently failed - "
                f"video_id: {video_id}, user: {owner_username}"
            )
            
            return True  # Delete message after successful processing
            
        except Exception as e:
            logger.error(
                f"Failed to process DLQ job for video {video_id}: {e}"
            )
            return False  # Don't delete - will retry later
    
    # === Private methods ===
    
    def _mark_video_as_failed(self, video_id: str, owner_username: str):
        """Update video status to 'failed' in database."""
        self.video_service.video_repo.update_fields(
            video_id, 
            {"status": "failed"}, 
            owner_username
        )
        
        logger.info(f"Marked video {video_id} as permanently failed")
