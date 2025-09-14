"""
Admin endpoints for user management.
Note: Admin functionality with Cognito requires AWS Cognito Admin APIs.
This is a simplified version for demonstration.
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.core.dependencies import require_admin_user
from app.schemas.auth import UserInfo

router = APIRouter()

@router.get("/users", response_model=List[UserInfo], tags=["admin"])
async def get_users(current_user: Dict[str, Any] = Depends(require_admin_user)):
    """
    Get all users information.
    Only admin users can access this endpoint.
    
    Note: This is a simplified implementation. In a real application,
    you would need to use AWS Cognito Admin APIs to list users.
    """
    # For demonstration purposes, return current user info
    # In a real implementation, you would call Cognito Admin APIs
    return [
        UserInfo(
            username=current_user.get("username"),
            email=current_user.get("email"),
            email_verified=current_user.get("email_verified", False),
            cognito_groups=current_user.get("cognito_groups", [])
        )
    ]

@router.get("/admin-info", tags=["admin"])
async def get_admin_info(current_user: Dict[str, Any] = Depends(require_admin_user)):
    """
    Get admin user information.
    Only admin users can access this endpoint.
    """
    return {
        "message": "Admin access granted",
        "user": {
            "username": current_user.get("username"),
            "email": current_user.get("email"),
            "groups": current_user.get("cognito_groups", [])
        }
    }
