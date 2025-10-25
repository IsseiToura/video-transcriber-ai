"""
Application configuration settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from .aws_config import AWSConfigManager

# Application Constants
class AppConstants:
    """Application constants that don't change between environments."""
    
    # Application Info
    APP_NAME: str = "Video Transcriber AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # File Storage
    UPLOAD_DIR: str = "data/videos"
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [
        "mp4", "avi", "mov", "wmv", "flv", "webm", 
        "mp3", "wav", "aac", "ogg", "flac", "m4a", "wma"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ElastiCache Memcached
    ELASTICACHE_MEMCACHED_TTL: int = 3600  # 1 hour default TTL

class Settings(BaseSettings):
    """Application settings with AWS integration."""
    
    # Application
    APP_NAME: str = AppConstants.APP_NAME
    APP_VERSION: str = AppConstants.APP_VERSION
    DEBUG: bool = AppConstants.DEBUG
    
    # File Storage
    UPLOAD_DIR: str = AppConstants.UPLOAD_DIR
    ALLOWED_VIDEO_EXTENSIONS: List[str] = AppConstants.ALLOWED_VIDEO_EXTENSIONS
    
    # AI Services - Define as fields to allow environment variable override
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Logging
    LOG_LEVEL: str = AppConstants.LOG_LEVEL
    LOG_FORMAT: str = AppConstants.LOG_FORMAT
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"

    # AWS
    AWS_REGION: str = "ap-southeast-2"
    S3_BUCKET: str = ""
    
    # DynamoDB
    DDB_VIDEOS_TABLE: str = ""
    
    # ElastiCache Memcached
    ELASTICACHE_MEMCACHED_ENDPOINT: str = ""
    ELASTICACHE_MEMCACHED_TTL: int = AppConstants.ELASTICACHE_MEMCACHED_TTL
    
    # SQS Configuration
    SQS_VIDEO_PROCESSING_QUEUE: str = ""
    SQS_VIDEO_PROCESSING_DLQ: str = ""
    
    # AWS Cognito
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_APP_CLIENT_ID: str = ""
    
    # Application URLs
    APP_URL: str = "http://localhost:5173"
    API_BASE_URL: str = "http://localhost:8000/api/v1"
    
    # QUT Configuration
    QUT_USERNAME: str = ""
    
    # File size limit
    MAX_FILE_SIZE: str = "100MB"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize AWS config manager with current region
        self._aws_config_manager = AWSConfigManager(region_name=self.AWS_REGION)
        
        # Set values from AWS if not provided via environment
        self._load_aws_config()
    
    def _load_aws_config(self) -> None:
        """Load configuration values from AWS if not provided via environment."""
        try:
            # Only use AWS values if environment variables are not set or empty
            if not self.OPENAI_API_KEY:
                self.OPENAI_API_KEY = self._aws_config_manager.get_secret(
                    "video-transcriber-ai/dev/openai-api-key",
                    fallback_env_var="OPENAI_API_KEY"
                )
            
            if not self.OPENAI_MODEL or self.OPENAI_MODEL == "gpt-4o-mini":
                self.OPENAI_MODEL = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/ai/openai-model",
                    fallback_env_var="OPENAI_MODEL"
                )
            
            if not self.AWS_REGION or self.AWS_REGION == "ap-southeast-2":
                self.AWS_REGION = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/aws/region",
                    fallback_env_var="AWS_REGION"
                )
            
            if not self.S3_BUCKET:
                self.S3_BUCKET = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/aws/s3-bucket",
                    fallback_env_var="S3_BUCKET"
                )
            
            if not self.DDB_VIDEOS_TABLE:
                self.DDB_VIDEOS_TABLE = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/aws/ddb-videos-table",
                    fallback_env_var="DDB_VIDEOS_TABLE"
                )
            
            if not self.ELASTICACHE_MEMCACHED_ENDPOINT:
                self.ELASTICACHE_MEMCACHED_ENDPOINT = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/aws/elasticache-memcached-endpoint",
                    fallback_env_var="ELASTICACHE_MEMCACHED_ENDPOINT"
                )
            
            if not self.SQS_VIDEO_PROCESSING_QUEUE:
                self.SQS_VIDEO_PROCESSING_QUEUE = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/aws/sqs-video-processing-queue",
                    fallback_env_var="SQS_VIDEO_PROCESSING_QUEUE"
                )
            
            if not self.SQS_VIDEO_PROCESSING_DLQ:
                self.SQS_VIDEO_PROCESSING_DLQ = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/aws/sqs-video-processing-dlq",
                    fallback_env_var="SQS_VIDEO_PROCESSING_DLQ"
                )
                
            # Always try to get from Parameter Store first, then fallback to environment
            try:
                user_pool_id = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/cognito/user-pool-id",
                    fallback_env_var="COGNITO_USER_POOL_ID"
                )
                if user_pool_id:
                    self.COGNITO_USER_POOL_ID = user_pool_id
                else:
                    print(f"COGNITO_USER_POOL_ID is empty from Parameter Store")
            except ValueError as e:
                print(f"Failed to get COGNITO_USER_POOL_ID from Parameter Store: {e}")
                # If Parameter Store fails, keep the current value (from environment or default)
                pass
            
            try:
                app_client_id = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/cognito/app-client-id",
                    fallback_env_var="COGNITO_APP_CLIENT_ID"
                )
                if app_client_id:
                    self.COGNITO_APP_CLIENT_ID = app_client_id
                else:
                    print(f"COGNITO_APP_CLIENT_ID is empty from Parameter Store")
            except ValueError as e:
                print(f"Failed to get COGNITO_APP_CLIENT_ID from Parameter Store: {e}")
                # If Parameter Store fails, keep the current value (from environment or default)
                pass
            
            # Always try to get from Parameter Store first, then fallback to environment
            try:
                app_url = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/app/url",
                    fallback_env_var="APP_URL"
                )
                if app_url:
                    self.APP_URL = app_url
                else:
                    print(f"APP_URL is empty from Parameter Store")
            except ValueError as e:
                print(f"Failed to get APP_URL from Parameter Store: {e}")
                # If Parameter Store fails, keep the current value (from environment or default)
                pass
            
            try:
                api_base_url = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/api/base-url",
                    fallback_env_var="API_BASE_URL"
                )
                if api_base_url:
                    self.API_BASE_URL = api_base_url
                else:
                    print(f"API_BASE_URL is empty from Parameter Store")
            except ValueError as e:
                print(f"Failed to get API_BASE_URL from Parameter Store: {e}")
                # If Parameter Store fails, keep the current value (from environment or default)
                pass
            
            if not self.QUT_USERNAME:
                self.QUT_USERNAME = self._aws_config_manager.get_secret(
                    "video-transcriber-ai/dev/qut-username",
                    fallback_env_var="QUT_USERNAME"
                )
            
            # Parse ALLOWED_ORIGINS if it's a string
            if isinstance(self.ALLOWED_ORIGINS, str):
                origins_str = self._aws_config_manager.get_parameter(
                    "/video-transcriber-ai/dev/cors/allowed-origins",
                    fallback_env_var="ALLOWED_ORIGINS"
                )
                if origins_str and origins_str != self.ALLOWED_ORIGINS:
                    self.ALLOWED_ORIGINS = origins_str
        except Exception as e:
            # If AWS config fails, continue with environment variables or defaults
            print(f"Warning: Failed to load AWS configuration: {e}")
            pass
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get ALLOWED_ORIGINS as a list."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields from environment variables


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings