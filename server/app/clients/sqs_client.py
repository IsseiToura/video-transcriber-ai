"""
SQS client service for video processing job queue.
"""

import json
import logging
import boto3
from typing import Dict, List, Optional
from botocore.exceptions import ClientError
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SQSClient:
    """SQS client for video processing jobs."""
    
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name=settings.AWS_REGION)
        self.queue_url = None
        self.dlq_url = None
        self._init_queues()
    
    def _init_queues(self):
        """Initialize SQS queue URLs from AWS Parameters Store."""
        # Get queue names from AWS Parameters Store via settings
        queue_name = settings.SQS_VIDEO_PROCESSING_QUEUE
        dlq_name = settings.SQS_VIDEO_PROCESSING_DLQ
        
        if not queue_name or not dlq_name:
            raise ValueError("SQS queue names not configured in AWS Parameters Store")
        
        try:
            # Get queue URL
            response = self.sqs.get_queue_url(QueueName=queue_name)
            self.queue_url = response['QueueUrl']
            logger.info(f"SQS queue URL initialized: {self.queue_url}")
        except ClientError as e:
            logger.error(f"Failed to get SQS queue URL for {queue_name}: {e}")
            raise
        
        try:
            # Get DLQ URL
            response = self.sqs.get_queue_url(QueueName=dlq_name)
            self.dlq_url = response['QueueUrl']
            logger.info(f"SQS DLQ URL initialized: {self.dlq_url}")
        except ClientError as e:
            logger.error(f"Failed to get SQS DLQ URL for {dlq_name}: {e}")
            raise
    
    def send_message(self, message_body: Dict) -> bool:
        """Send a message to the SQS queue."""
        if not self.queue_url:
            logger.error("SQS queue URL not initialized")
            return False
        
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    'MessageType': {
                        'StringValue': 'VideoProcessingJob',
                        'DataType': 'String'
                    },
                    'VideoId': {
                        'StringValue': message_body.get('video_id', ''),
                        'DataType': 'String'
                    }
                }
            )
            logger.info(f"Message sent to SQS: {response['MessageId']}")
            return True
        except ClientError as e:
            logger.error(f"Failed to send message to SQS: {e}")
            return False
    
    def receive_messages(self, max_messages: int = 1, wait_time_seconds: int = 20) -> List[Dict]:
        """Receive messages from the SQS queue."""
        if not self.queue_url:
            logger.error("SQS queue URL not initialized")
            return []
        
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            logger.info(f"Received {len(messages)} messages from SQS")
            return messages
        except ClientError as e:
            logger.error(f"Failed to receive messages from SQS: {e}")
            return []
    
    def receive_messages_from_dlq(self, max_messages: int = 1, wait_time_seconds: int = 20) -> List[Dict]:
        """Receive messages from the DLQ."""
        if not self.dlq_url:
            logger.error("SQS DLQ URL not initialized")
            return []
        
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.dlq_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            logger.info(f"Received {len(messages)} messages from DLQ")
            return messages
        except ClientError as e:
            logger.error(f"Failed to receive messages from DLQ: {e}")
            return []
    
    def delete_message(self, message: Dict) -> bool:
        """Delete a message from the SQS queue."""
        if not self.queue_url:
            logger.error("SQS queue URL not initialized")
            return False
        
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            logger.info("Message deleted from SQS")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete message from SQS: {e}")
            return False
    
    def delete_message_from_dlq(self, message: Dict) -> bool:
        """Delete a message from the DLQ."""
        if not self.dlq_url:
            logger.error("SQS DLQ URL not initialized")
            return False
        
        try:
            self.sqs.delete_message(
                QueueUrl=self.dlq_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            logger.info("Message deleted from DLQ")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete message from DLQ: {e}")
            return False
    
    def change_message_visibility(self, message: Dict, visibility_timeout: int) -> bool:
        """Change message visibility timeout."""
        if not self.queue_url:
            logger.error("SQS queue URL not initialized")
            return False
        
        try:
            self.sqs.change_message_visibility(
                QueueUrl=self.queue_url,
                ReceiptHandle=message['ReceiptHandle'],
                VisibilityTimeoutSeconds=visibility_timeout
            )
            logger.info(f"Message visibility timeout changed to {visibility_timeout} seconds")
            return True
        except ClientError as e:
            logger.error(f"Failed to change message visibility: {e}")
            return False


# Global SQS client instance
sqs_client = SQSClient()
