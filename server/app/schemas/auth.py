"""
Authentication schemas.
"""

from pydantic import BaseModel
from typing import List, Optional

class LoginRequest(BaseModel):
    """Login request schema. DEPRECATED: Use Cognito authentication."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response schema. DEPRECATED: Use Cognito authentication."""
    access_token: str
    token_type: str = "bearer"
    username: str


class UserInfo(BaseModel):
    """User information schema."""
    username: Optional[str] = None
    email: Optional[str] = None
    email_verified: bool = False
    cognito_groups: List[str] = []


class TokenValidationResponse(BaseModel):
    """Token validation response schema."""
    valid: bool
    user_info: Optional[UserInfo] = None


class UserList(BaseModel):
    """User list response schema."""
    users: List[UserInfo]
    total: int
