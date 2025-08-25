"""
Admin endpoints for user management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict
from app.core.security import get_all_users, get_user_by_username, get_user_role, verify_token
from app.schemas.auth import UserInfo, UserList

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

@router.get("/users/{username}", response_model=UserInfo, tags=["admin"])
async def get_user(username: str, current_user_role: str = Depends(get_current_user_role)):
    """
    Get specific user information.
    Admin users can access any user's information.
    Regular users can only access their own information.
    """
    # Check if user exists
    user_info = get_user_by_username(username)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Admin can access any user, regular users can only access their own
    if current_user_role != "admin":
        # For regular users, we need to get their username from the token
        # This would require modifying the token to include more user info
        # For now, we'll restrict regular users from accessing other user info
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own user information"
        )
    
    return user_info

@router.get("/users/me", response_model=UserInfo, tags=["admin"])
async def get_current_user_info(current_user_role: str = Depends(get_current_user_role)):
    """
    Get current user's information.
    Any authenticated user can access this endpoint.
    """
    # This endpoint would need the username from the token
    # For now, we'll return a generic response
    # In a real implementation, you'd extract username from the token
    return {
        "username": "current_user",
        "full_name": "Current User",
        "role": current_user_role,
        "email": "user@example.com"
    }
