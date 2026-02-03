"""
Worker service for processing video transcription jobs from SQS.
"""

import logging
import signal
import sys
import time

from app.clients.sqs_client import SQSClient
from app.core.config import get_settings
from .config import MAX_MESSAGES_PER_POLL, LONG_POLL_WAIT_TIME, ERROR_RETRY_DELAY, NO_MESSAGE_SLEEP
from .message_handler import MessageHandler
from .job_processor import JobProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


class VideoProcessingWorker:
    """Worker class for processing video jobs from SQS."""
    
    def __init__(self):
        self.sqs_client = SQSClient()
        self.message_handler = MessageHandler()
        self.job_processor = JobProcessor(self.sqs_client)
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _process_message(self, message: dict) -> bool:
        """Process a single SQS message."""
        # Parse the message
        job_data = self.message_handler.parse_message(message)
        if not job_data or not self.message_handler.is_valid_job_data(job_data):
            # Invalid message, delete it
            self.sqs_client.delete_message(message)
            return False
        
        video_id = job_data['video_id']
        owner_username = job_data['owner_username']
        
        try:
            # Process the job
            success = self.job_processor.process_single_job(job_data, message)
            
            if success:
                # Delete message from queue after successful processing
                self.sqs_client.delete_message(message)
                logger.info(f"Job completed successfully for video {video_id}")
                return True
            else:
                # Processing failed due to validation error (video not found, etc.)
                # Delete message to prevent infinite retries
                self.sqs_client.delete_message(message)
                logger.warning(f"Job failed validation for video {video_id}, deleted from queue")
                return False
        
        except Exception as e:
            # Processing error - let SQS handle retries
            video_id = job_data['video_id']
            logger.error(f"Job failed for video {video_id}, will be retried by SQS: {e}")
            # Don't delete message - let SQS retry mechanism handle it
            return False
    
    def run(self):
        """Main worker loop - poll SQS and process jobs."""
        logger.info("Starting video processing worker...")
        logger.info(f"Polling SQS queue for video processing jobs...")
        
        while self.running:
            try:
                # Receive messages from SQS
                messages = self.sqs_client.receive_messages(
                    max_messages=MAX_MESSAGES_PER_POLL, 
                    wait_time_seconds=LONG_POLL_WAIT_TIME
                )
                
                for message in messages:
                    if not self.running:
                        break
                    
                    self._process_message(message)
                
                # If no messages received, sleep briefly to avoid excessive polling
                if not messages:
                    time.sleep(NO_MESSAGE_SLEEP)
                    
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {e}")
                time.sleep(ERROR_RETRY_DELAY)  # Wait before retrying
        
        logger.info("Video processing worker stopped")


def main():
    """Main entry point for the worker service."""
    try:
        worker = VideoProcessingWorker()
        worker.run()
    except Exception as e:
        logger.error(f"Worker failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
