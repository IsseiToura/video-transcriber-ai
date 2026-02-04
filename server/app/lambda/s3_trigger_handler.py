"""
Lambda function to handle S3 upload events and trigger video processing.

This function is triggered when a video file is uploaded to S3.
It retrieves metadata from DynamoDB and sends a processing job to SQS.
"""

import json
import logging
from typing import Any, Dict

# Add parent directory to path to import app modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from .config import get_config
from .utils import (
    extract_video_id_from_s3_key,
    get_video_metadata_from_dynamodb,
    update_video_status,
    send_message_to_sqs
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_s3_record(record: Dict[str, Any], config: Dict[str, Any]) -> bool:
    """
    Process a single S3 record.
    Returns True if processing was successful, False otherwise.
    """
    # Get S3 bucket and key
    s3_bucket = record['s3']['bucket']['name']
    s3_key = record['s3']['object']['key']
    
    logger.info(f"Processing S3 upload: bucket={s3_bucket}, key={s3_key}")
    
    # Extract video_id from S3 key
    video_id = extract_video_id_from_s3_key(s3_key)
    if not video_id:
        logger.error(f"Could not extract video_id from S3 key: {s3_key}")
        return False
    
    # Get metadata from DynamoDB (with retry logic)
    metadata = get_video_metadata_from_dynamodb(
        config['videos_table'], 
        config['QUT_USERNAME'], 
        video_id
    )
    if not metadata:
        logger.error(f"Metadata not found for video_id: {video_id}. Skipping processing.")
        return False
    
    # Extract owner_username
    owner_username = metadata.get('owner_username')
    if not owner_username:
        logger.error(f"owner_username not found in metadata for video_id: {video_id}")
        return False
    
    # Check current status
    current_status = metadata.get('status', 'uploaded')
    if current_status in ['processing', 'completed']:
        logger.info(f"Video {video_id} is already {current_status}. Skipping.")
        return True
    
    # Update status to processing
    update_success = update_video_status(
        config['videos_table'], 
        config['QUT_USERNAME'], 
        video_id, 
        owner_username, 
        'processing'
    )
    if not update_success:
        logger.error(f"Failed to update status for video_id: {video_id}")
        # Continue anyway to try sending to SQS
    
    # Send message to SQS
    sqs_success = send_message_to_sqs(
        config['sqs'], 
        config['SQS_QUEUE_URL'], 
        video_id, 
        owner_username
    )
    if not sqs_success:
        logger.error(f"Failed to send SQS message for video_id: {video_id}")
        # Revert status to uploaded
        update_video_status(
            config['videos_table'], 
            config['QUT_USERNAME'], 
            video_id, 
            owner_username, 
            'uploaded'
        )
        return False
    
    logger.info(f"Successfully triggered processing for video_id: {video_id}")
    return True


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for S3 upload events.
    
    Args:
        event: S3 event notification
        context: Lambda context
        
    Returns:
        Response dict with status code and message
    """
    try:
        # Initialize configuration in invoke phase (not init phase)
        config = get_config()
        
        # Process each S3 record
        for record in event.get('Records', []):
            process_s3_record(record, config)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing triggered successfully'
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }

