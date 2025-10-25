"""
DLQ job processing logic for failed video jobs.
"""

import logging

from app.services.video_service import VideoService

logger = logging.getLogger(__name__)


class DLQJobProcessor:
    """Handles DLQ video job processing - marking failed jobs."""
    
    def __init__(self):
        self.video_service = VideoService()
    
    def mark_video_as_failed(self, video_id: str, owner_username: str):
        """Mark video as permanently failed (called from DLQ monitor)."""
        try:
            # Update video status to 'failed' in database
            self.video_service.video_repo.update_fields(
                video_id, 
                {"status": "failed"}, 
                owner_username
            )
            
            logger.info(f"Marked video {video_id} as permanently failed")
            
        except Exception as e:
            logger.error(f"Failed to mark video {video_id} as failed: {e}")
            raise
