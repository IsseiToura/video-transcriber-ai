"""
Authentication endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, LoginResponse
from app.core.security import authenticate_user, create_access_token

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login endpoint with hardcoded credentials."""
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    return LoginResponse(
        access_token=access_token,
        username=user["username"],
    )
