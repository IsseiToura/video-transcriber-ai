"""
Authentication endpoints.
These endpoints provide user information and token validation.
"""

from fastapi import APIRouter, Depends
from app.schemas.auth import UserInfo, TokenValidationResponse
from app.core.dependencies import get_current_user, get_current_user_optional
from typing import Dict, Any

router = APIRouter()

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information.
    Requires valid Cognito JWT token.
    """
    return UserInfo(
        username=current_user.get("username"),
        email=current_user.get("email"),
        email_verified=current_user.get("email_verified", False),
        cognito_groups=current_user.get("cognito_groups", [])
    )

@router.get("/validate-token", response_model=TokenValidationResponse)
async def validate_token(current_user: Dict[str, Any] = Depends(get_current_user_optional)):
    """
    Validate JWT token.
    Returns user information if token is valid, None if not authenticated.
    """
    if current_user:
        return TokenValidationResponse(
            valid=True,
            user_info=UserInfo(
                username=current_user.get("username"),
                email=current_user.get("email"),
                email_verified=current_user.get("email_verified", False),
                cognito_groups=current_user.get("cognito_groups", [])
            )
        )
    else:
        return TokenValidationResponse(valid=False, user_info=None)
