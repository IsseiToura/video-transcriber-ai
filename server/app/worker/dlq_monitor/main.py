"""
DLQ Monitor service for handling failed video processing jobs.
"""

import logging
import signal
import sys
import time

from app.clients.sqs_client import SQSClient
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
    
    # === Public methods ===
    
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
                    
                    self._handle_failed_job_message(message)
                
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
    
    # === Private methods ===
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _handle_failed_job_message(self, message: dict) -> bool:
        """
        Handle a single failed job message from DLQ.
        
        Orchestrates message processing by delegating all business logic
        to JobProcessor and handling SQS message cleanup.
        
        Args:
            message: Raw SQS message from DLQ
            
        Returns:
            True if message was processed successfully, False otherwise
        """
        try:
            # Delegate all business logic to JobProcessor
            should_delete = self.job_processor.process_failed_video_job(
                message, 
                self.message_handler
            )
            
            # Handle SQS cleanup based on processing result
            if should_delete:
                self.sqs_client.delete_message_from_dlq(message)
            
            return should_delete
            
        except Exception as e:
            logger.error(f"Failed to handle DLQ message: {e}")
            return False


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
