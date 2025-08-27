"""
Application configuration settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Video Transcriber AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(..., env="DEBUG")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(..., env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # File Storage
    UPLOAD_DIR: str = Field(..., env="UPLOAD_DIR") 
    MAX_FILE_SIZE: str = Field(..., env="MAX_FILE_SIZE")
    ALLOWED_VIDEO_EXTENSIONS: List[str] = ["mp4", "avi", "mov", "wmv", "flv", "webm", "mp3", "wav", "aac", "ogg", "flac", "m4a", "wma"]
    
    # AI Services
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(env="OPENAI_MODEL")
    
    # Logging
    LOG_LEVEL: str = Field(..., env="LOG_LEVEL")
    LOG_FORMAT: str = Field(..., env="LOG_FORMAT")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]
    
    @field_validator("ALLOWED_VIDEO_EXTENSIONS", mode="before")
    @classmethod
    def parse_video_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
