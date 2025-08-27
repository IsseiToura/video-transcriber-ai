"""
Admin endpoints for user management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.core.security import get_all_users, get_user_role, verify_token
from app.schemas.auth import UserInfo

router = APIRouter()

def get_current_user_role(token: str = Depends(verify_token)) -> str:
    """Get current user's role from JWT token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = token.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_role = get_user_role(username)
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_role

@router.get("/users", response_model=List[UserInfo], tags=["admin"])
async def get_users(current_user_role: str = Depends(get_current_user_role)):
    """
    Get all users information.
    Only admin users can access this endpoint.
    """
    if current_user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this endpoint"
        )
    
    users = get_all_users(current_user_role)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return users
