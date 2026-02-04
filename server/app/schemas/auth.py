"""
Authentication schemas.
"""

from pydantic import BaseModel
from typing import List, Optional


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
