"""
Configuration and constants for the video processing worker.
"""

# Timeout configuration
DEFAULT_TIMEOUT = 600          # 10 minutes
MAX_TIMEOUT = 1800            # 30 minutes maximum
TIMEOUT_CHECK_INTERVAL = 300  # Check every 5 minutes
TIMEOUT_BUFFER = 300          # 5-minute buffer when extending

# SQS polling configuration
MAX_MESSAGES_PER_POLL = 1
LONG_POLL_WAIT_TIME = 20      # seconds

# Error handling
ERROR_RETRY_DELAY = 5         # seconds
NO_MESSAGE_SLEEP = 1          # seconds
