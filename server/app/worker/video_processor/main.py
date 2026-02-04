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
    
    # === Public methods ===
    
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
    
    # === Private methods ===
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _process_message(self, message: dict) -> bool:
        """
        Process a single SQS message.
        
        Orchestrates message processing by delegating all business logic
        to JobProcessor and handling SQS message cleanup.
        """
        try:
            should_delete = self.job_processor.process_video_job(
                message, 
                self.message_handler
            )
            
            # Handle SQS cleanup based on processing result
            if should_delete:
                self.sqs_client.delete_message(message)
            
            return should_delete
            
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return False


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
