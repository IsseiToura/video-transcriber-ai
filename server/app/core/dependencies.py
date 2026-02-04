"""
FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.core.cognito_auth import verify_cognito_token

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User information dict
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    user_info = verify_cognito_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user from JWT token (optional).
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        
    Returns:
        User information dict if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return verify_cognito_token(token)


async def require_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require admin user role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information dict
        
    Raises:
        HTTPException: If user is not admin
    """
    # Check if user is in admin group
    user_groups = current_user.get('cognito_groups', [])
    if 'admin' not in user_groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user