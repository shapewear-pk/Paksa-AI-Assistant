"""
Paksa AI Assistant - User Models

Defines the user-related Pydantic models for the application.
Copyright © 2025 Paksa IT Solutions (www.paksa.com.pk)
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    CUSTOMER = "customer"

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    disabled: bool = False
    role: UserRole = UserRole.CUSTOMER

class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

class UserUpdate(BaseModel):
    """Model for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(UserBase):
    """User model as stored in the database"""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserBase):
    """User model for API responses"""
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    """Authentication token model"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    scopes: List[str] = []

class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str

class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Password reset model"""
    token: str
    new_password: str
