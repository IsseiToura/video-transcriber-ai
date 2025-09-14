"""
Configuration API endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.core.config import get_settings
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class ConfigResponse(BaseModel):
    """Configuration response model."""
    cognito: Dict[str, Any]
    api: Dict[str, Any]

@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get application configuration for client."""
    try:
        settings = get_settings()
        
        # Cognito configuration
        cognito_config = {
            "region": settings.AWS_REGION,
            "userPoolId": settings.COGNITO_USER_POOL_ID,
            "userPoolWebClientId": settings.COGNITO_APP_CLIENT_ID,
            "authenticationFlowType": "USER_SRP_AUTH",
            "oauth": {
                "domain": "",  # Add OAuth domain if needed
                "scope": ["email", "openid", "profile"],
                "redirectSignIn": settings.APP_URL,
                "redirectSignOut": settings.APP_URL,
                "responseType": "code"
            }
        }
        
        # API configuration
        api_config = {
            "baseUrl": settings.API_BASE_URL,
            "allowedOrigins": settings.ALLOWED_ORIGINS
        }
        
        return ConfigResponse(
            cognito=cognito_config,
            api=api_config
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve configuration: {str(e)}"
        )
