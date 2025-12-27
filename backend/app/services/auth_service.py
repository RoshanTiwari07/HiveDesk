"""
Authentication Service - Handles user authentication and registration logic
"""
from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from ..models.user import UserModel
from ..schemas.user import UserCreateSchema
from ..auth import authenticate_user, create_access_token, get_password_hash
from ..core.enums import UserRole


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    async def login_user(session: AsyncSession, email: str, password: str) -> tuple[str, UserModel]:
        """
        Authenticate user and generate access token
        Returns: (access_token, user)
        """
        user = await authenticate_user(session, email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return access_token, user
    
    @staticmethod
    async def register_user(
        session: AsyncSession,
        user_data: UserCreateSchema,
        created_by: str
    ) -> UserModel:
        """
        Register a new user (HR only operation)
        """
        # Check if user already exists
        statement = select(UserModel).where(UserModel.email == user_data.email)
        result = await session.execute(statement)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = UserModel(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
            is_active=user_data.is_active
        )
        
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[UserModel]:
        """Get user by email"""
        statement = select(UserModel).where(UserModel.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
