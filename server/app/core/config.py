"""
Application configuration settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Video Transcriber AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24時間
    
    # File Storage
    UPLOAD_DIR: str = "./data"
    MAX_FILE_SIZE: str = "100MB"
    ALLOWED_VIDEO_EXTENSIONS: List[str] = ["mp4", "avi", "mov", "wmv", "flv", "webm", "mp3", "wav", "aac", "ogg", "flac", "m4a", "wma"]
    
    # AI Services
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
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
