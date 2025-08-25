"""
Authentication schemas.
"""

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    token_type: str = "bearer"
    username: str


class UserInfo(BaseModel):
    """User information schema."""
    username: str
    role: str
    email: str


class UserList(BaseModel):
    """User list response schema."""
    users: list[UserInfo]
    total: int
