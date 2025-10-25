"""
Timeout management for video processing jobs.
"""

import logging
import threading
import time
from typing import Dict

from .config import DEFAULT_TIMEOUT, MAX_TIMEOUT, TIMEOUT_CHECK_INTERVAL, TIMEOUT_BUFFER

logger = logging.getLogger(__name__)


class TimeoutManager:
    """Manages visibility timeout for long-running video processing jobs."""
    
    def __init__(self, sqs_client):
        self.sqs_client = sqs_client
    
    def process_with_timeout_management(self, video_service, video_id: str, owner_username: str, 
                                      message: Dict, start_time: float):
        """Process video with periodic visibility timeout extension."""
        
        # Start a thread to monitor and extend visibility timeout
        timeout_monitor = threading.Thread(
            target=self._monitor_and_extend_timeout,
            args=(message, start_time),
            daemon=True
        )
        timeout_monitor.start()
        
        try:
            # Process the video
            result = video_service.process_video(video_id, owner_username)
            return result
        finally:
            # The timeout monitor thread will stop when the main thread completes
            pass
    
    def _monitor_and_extend_timeout(self, message: Dict, start_time: float):
        """Monitor processing time and extend visibility timeout if needed."""
        while True:
            time.sleep(TIMEOUT_CHECK_INTERVAL)
            
            elapsed_time = time.time() - start_time
            
            # Calculate new timeout (elapsed time + buffer)
            new_timeout = int(elapsed_time + TIMEOUT_BUFFER)
            
            # Don't exceed maximum timeout
            if new_timeout > MAX_TIMEOUT:
                new_timeout = MAX_TIMEOUT
            
            # Don't extend if we're within default timeout
            if new_timeout <= DEFAULT_TIMEOUT:
                continue
            
            try:
                # Extend visibility timeout
                success = self.sqs_client.change_message_visibility(message, new_timeout)
                if success:
                    logger.info(f"Extended visibility timeout to {new_timeout} seconds (elapsed: {elapsed_time:.2f}s)")
                else:
                    logger.warning(f"Failed to extend visibility timeout to {new_timeout} seconds")
            except Exception as e:
                logger.error(f"Error extending visibility timeout: {e}")
            
            # If we've reached maximum timeout, stop monitoring
            if new_timeout >= MAX_TIMEOUT:
                logger.warning(f"Reached maximum timeout of {MAX_TIMEOUT} seconds")
                break
