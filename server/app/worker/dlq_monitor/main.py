"""
DLQ Monitor service for handling failed video processing jobs.
"""

import logging
import signal
import sys
import time

from app.services.sqs_client import SQSClient
from app.core.config import get_settings
from .config import MAX_MESSAGES_PER_POLL, LONG_POLL_WAIT_TIME, ERROR_RETRY_DELAY, NO_MESSAGE_SLEEP
from .message_handler import DLQMessageHandler
from .job_processor import DLQJobProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


class DLQMonitor:
    """Monitor for Dead Letter Queue messages."""
    
    def __init__(self):
        self.sqs_client = SQSClient()
        self.message_handler = DLQMessageHandler()
        self.job_processor = DLQJobProcessor()
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _process_dlq_message(self, message: dict) -> bool:
        """Process a single DLQ message."""
        # Parse the message
        job_data = self.message_handler.parse_message(message)
        if not job_data or not self.message_handler.is_valid_job_data(job_data):
            # Invalid message, delete it
            self.sqs_client.delete_message_from_dlq(message)
            return False
        
        video_id = job_data['video_id']
        owner_username = job_data['owner_username']
        
        logger.warning(f"Processing failed job from DLQ: {video_id} for user: {owner_username}")
        
        try:
            # Mark video status as failed in database
            self.job_processor.mark_video_as_failed(video_id, owner_username)
            
            # Log the failure for monitoring
            logger.error(f"Video processing permanently failed - video_id: {video_id}, user: {owner_username}")
            
            # Delete the message from DLQ after processing
            self.sqs_client.delete_message_from_dlq(message)
            return True
            
        except Exception as e:
            logger.error(f"Failed to process DLQ message for video {video_id}: {e}")
            # Don't delete message if we can't process it - will retry later
            return False
    
    def run(self):
        """Main DLQ monitoring loop."""
        logger.info("Starting DLQ monitor...")
        logger.info("Monitoring Dead Letter Queue for failed video processing jobs...")
        
        while self.running:
            try:
                # Receive messages from DLQ
                messages = self.sqs_client.receive_messages_from_dlq(
                    max_messages=MAX_MESSAGES_PER_POLL, 
                    wait_time_seconds=LONG_POLL_WAIT_TIME
                )
                
                for message in messages:
                    if not self.running:
                        break
                    
                    self._process_dlq_message(message)
                
                # If no messages received, sleep briefly to avoid excessive polling
                if not messages:
                    time.sleep(NO_MESSAGE_SLEEP)
                    
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in DLQ monitor loop: {e}")
                time.sleep(ERROR_RETRY_DELAY)  # Wait before retrying
        
        logger.info("DLQ monitor stopped")


def main():
    """Main entry point for the DLQ monitor service."""
    try:
        monitor = DLQMonitor()
        monitor.run()
    except Exception as e:
        logger.error(f"DLQ monitor failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
