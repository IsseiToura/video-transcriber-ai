"""
Security utilities for authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Multiple users with role-based access control
USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123", 
        "role": "admin",
        "email": "admin@example.com"
    },
    "user1": {
        "username": "user1",
        "password": "user123",
        "role": "user",
        "email": "user1@example.com"
    },
    "user2": {
        "username": "user2",
        "password": "user456",
        "role": "user",
        "email": "user2@example.com"
    },
    "moderator": {
        "username": "moderator",
        "password": "mod123",
        "role": "moderator",
        "email": "moderator@example.com"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with role-based credentials."""
    if username in USERS and USERS[username]["password"] == password:
        user_data = USERS[username].copy()
        # Remove password from returned data for security
        user_data.pop("password", None)
        return user_data
    return None

def get_user_by_username(username: str) -> Optional[dict]:
    """Get user information by username (without password)."""
    if username in USERS:
        user_data = USERS[username].copy()
        user_data.pop("password", None)
        return user_data
    return None

def get_all_users(requester_role: str) -> Optional[List[Dict]]:
    """Get all users information. Only admins can access this."""
    if requester_role != "admin":
        return None
    
    all_users = []
    for user_data in USERS.items():
        user_info = user_data.copy()
        user_info.pop("password", None)  # Remove password for security
        all_users.append(user_info)
    
    return all_users

def is_admin(username: str) -> bool:
    """Check if user has admin role."""
    if username in USERS:
        return USERS[username]["role"] == "admin"
    return False

def get_user_role(username: str) -> Optional[str]:
    """Get user role by username."""
    if username in USERS:
        return USERS[username]["role"]
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return {"username": username}
    except JWTError:
        return None
