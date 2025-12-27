"""
User Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from ..core.enums import UserRole


class UserBaseSchema(BaseModel):
    """Base user schema"""
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool = True


class UserCreateSchema(UserBaseSchema):
    """Schema for creating a new user"""
    password: str


class UserUpdateSchema(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponseSchema(UserBaseSchema):
    """Schema for user response"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserLoginResponseSchema(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str
    user: UserResponseSchema