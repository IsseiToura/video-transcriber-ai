"""
Configuration and constants for the DLQ monitor.
"""

# SQS polling configuration
MAX_MESSAGES_PER_POLL = 1
LONG_POLL_WAIT_TIME = 20      # seconds

# Error handling
ERROR_RETRY_DELAY = 10        # seconds
NO_MESSAGE_SLEEP = 5          # seconds
