"""
Utility functions for Lambda function.
"""

import json
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import unquote_plus

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)


def extract_video_id_from_s3_key(s3_key: str) -> Optional[str]:
    """
    Extract video_id from S3 key.
    Expected format: videos/{video_id}_{filename}
    Example: videos/513cfba9-0227-4480-abf4-639c558e1dbc_CAB432_Lecture_4.3_-_Persistence.webm
    """
    try:
        # Decode URL-encoded characters
        decoded_key = unquote_plus(s3_key)
        
        # Remove 'videos/' prefix if present
        if decoded_key.startswith('videos/'):
            filename_part = decoded_key[7:]  # Remove 'videos/' (7 characters)
        else:
            filename_part = decoded_key
        
        # Extract video_id from filename
        # Format: {video_id}_{rest_of_filename}
        # Example: 513cfba9-0227-4480-abf4-639c558e1dbc_CAB432_Lecture_4.3_-_Persistence.webm
        if '_' in filename_part:
            video_id = filename_part.split('_')[0]
            # Validate that it looks like a UUID (basic check)
            if len(video_id) == 36 and '-' in video_id:
                return video_id
        
        logger.error(f"Could not extract valid video_id from S3 key: {s3_key}")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting video_id from S3 key {s3_key}: {e}")
        return None


def get_video_metadata_from_dynamodb(videos_table, qut_username: str, video_id: str, max_retries: int = 3, retry_delay: int = 2) -> Optional[Dict[str, Any]]:
    """
    Retrieve video metadata from DynamoDB.
    Since we don't know the owner_username initially, we need to scan the partition.
    Implements retry logic to handle timing issues between S3 upload and metadata save.
    """
    for attempt in range(max_retries):
        try:
            response = videos_table.query(
                KeyConditionExpression=Key('qut-username').eq(qut_username),
                FilterExpression=Key('video_id').eq(video_id)
            )
            
            items = response.get('Items', [])
            
            if items:
                # Return the first item (should be unique for a given video_id)
                return items[0]
            
            # If not found and we have retries left, wait and try again
            if attempt < max_retries - 1:
                logger.warning(f"Metadata not found for video_id: {video_id}, attempt {attempt + 1}/{max_retries}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Metadata not found for video_id: {video_id} after {max_retries} attempts")
                return None
                
        except ClientError as e:
            logger.error(f"DynamoDB error while fetching metadata for video_id {video_id}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return None
    
    return None


def update_video_status(videos_table, qut_username: str, video_id: str, owner_username: str, status: str) -> bool:
    """
    Update video status in DynamoDB.
    """
    try:
        sort_key = f"{owner_username}#{video_id}"
        
        videos_table.update_item(
            Key={
                'qut-username': qut_username,
                'sort-key': sort_key
            },
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':status': status
            }
        )
        
        logger.info(f"Updated video {video_id} status to {status}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to update video status: {e}")
        return False


def send_message_to_sqs(sqs_client, sqs_queue_url: str, video_id: str, owner_username: str) -> bool:
    """
    Send processing job message to SQS queue.
    """
    try:
        message_body = {
            "video_id": video_id,
            "owner_username": owner_username,
            "timestamp": time.time()
        }
        
        response = sqs_client.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(message_body),
            MessageAttributes={
                'MessageType': {
                    'StringValue': 'VideoProcessingJob',
                    'DataType': 'String'
                },
                'VideoId': {
                    'StringValue': video_id,
                    'DataType': 'String'
                },
                'Source': {
                    'StringValue': 'S3TriggerLambda',
                    'DataType': 'String'
                }
            }
        )
        
        logger.info(f"Message sent to SQS: {response['MessageId']}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to send message to SQS: {e}")
        return False
