"""
Message handling utilities for DLQ processing jobs.
"""

import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DLQMessageHandler:
    """Handles SQS DLQ message parsing and job data extraction."""
    
    @staticmethod
    def parse_message(message: Dict) -> Optional[Dict]:
        """Parse SQS message and extract job data."""
        try:
            body = json.loads(message['Body'])
            return {
                'video_id': body.get('video_id'),
                'owner_username': body.get('owner_username'),
                'message_id': message.get('MessageId'),
                'receipt_handle': message.get('ReceiptHandle')
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse DLQ message: {e}")
            return None
    
    @staticmethod
    def is_valid_job_data(job_data: Dict) -> bool:
        """Validate that job data contains required fields."""
        if not job_data:
            return False
        
        required_fields = ['video_id', 'owner_username']
        return all(job_data.get(field) for field in required_fields)
