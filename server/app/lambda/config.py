"""
Configuration and initialization for Lambda function.
"""

import logging
import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def initialize_config():
    """Initialize configuration and AWS clients."""
    # Get settings from config file
    settings = get_settings()

    # Use configuration values from config.py
    AWS_REGION = settings.AWS_REGION
    DYNAMODB_TABLE_NAME = settings.DDB_VIDEOS_TABLE
    SQS_QUEUE_NAME = settings.SQS_VIDEO_PROCESSING_QUEUE
    QUT_USERNAME = settings.QUT_USERNAME

    # Validation
    if not DYNAMODB_TABLE_NAME:
        raise ValueError("DDB_VIDEOS_TABLE configuration is required")
    if not SQS_QUEUE_NAME:
        raise ValueError("SQS_VIDEO_PROCESSING_QUEUE configuration is required")
    if not QUT_USERNAME:
        raise ValueError("QUT_USERNAME configuration is required")

    # Initialize AWS clients
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    sqs = boto3.client('sqs', region_name=AWS_REGION)

    # Get SQS queue URL from queue name
    try:
        response = sqs.get_queue_url(QueueName=SQS_QUEUE_NAME)
        SQS_QUEUE_URL = response['QueueUrl']
        logger.info(f"SQS queue URL initialized: {SQS_QUEUE_URL}")
    except ClientError as e:
        logger.error(f"Failed to get SQS queue URL for {SQS_QUEUE_NAME}: {e}")
        raise

    # Initialize DynamoDB table
    videos_table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    return {
        'AWS_REGION': AWS_REGION,
        'DYNAMODB_TABLE_NAME': DYNAMODB_TABLE_NAME,
        'SQS_QUEUE_NAME': SQS_QUEUE_NAME,
        'SQS_QUEUE_URL': SQS_QUEUE_URL,
        'QUT_USERNAME': QUT_USERNAME,
        'videos_table': videos_table,
        'sqs': sqs
    }

# Global config variable - will be initialized lazily
config = None

def get_config():
    """Get configuration, initializing if needed."""
    global config
    if config is None:
        config = initialize_config()
    return config
