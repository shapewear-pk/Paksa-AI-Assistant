"""
Paksa AI Assistant - API Router

This module contains the main API router and endpoint definitions.
Copyright © 2025 Paksa IT Solutions (www.paksa.com.pk)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
import logging

from app.models.user import User, UserInDB, UserCreate, Token, TokenData
from app.services.auth import (
    get_current_active_user,
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from app.core.license import validate_license

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"api/v1/auth/token")

@router.get("/")
async def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Paksa AI Assistant API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@router.post("/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 token endpoint"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    # Implementation would go here
    pass

@router.get("/license/validate")
async def validate_license_endpoint():
    """Validate the current license"""
    is_valid, message = validate_license()
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )
    return {"status": "valid", "message": message}

# Import and include other routers
# from . import items, users, etc.
# router.include_router(items.router, prefix="/items", tags=["items"])
# router.include_router(users.router, prefix="/users", tags=["users"])
