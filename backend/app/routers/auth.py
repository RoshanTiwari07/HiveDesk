"""
Authentication Router - Login, Register, Token Management
"""
from fastapi import APIRouter, Depends
from typing import Annotated

from ..core.dependencies import SessionDep, CurrentUserDep, require_role
from ..services.auth_service import AuthService
from ..schemas.user import (
    UserLoginSchema, UserLoginResponseSchema,
    UserCreateSchema, UserResponseSchema
)
from ..schemas.responses import MessageResponseSchema
from ..core.enums import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=UserLoginResponseSchema)
async def login(login_data: UserLoginSchema, session: SessionDep):
    """
    Authenticate user and return access token
    """
    access_token, user = await AuthService.login_user(
        session,
        login_data.email,
        login_data.password
    )
    
    return UserLoginResponseSchema(
        access_token=access_token,
        token_type="bearer",
        user=UserResponseSchema.from_orm(user)
    )


@router.post(
    "/register",
    response_model=UserResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def register_user(
    user_data: UserCreateSchema,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Register new user (HR only)
    """
    user = await AuthService.register_user(session, user_data, current_user.id)
    return UserResponseSchema.from_orm(user)


@router.post("/logout", response_model=MessageResponseSchema)
async def logout(current_user: CurrentUserDep):
    """
    Logout endpoint - client should discard token
    """
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponseSchema)
async def get_current_user_info(current_user: CurrentUserDep):
    """
    Get current authenticated user information
    """
    return UserResponseSchema.from_orm(current_user)


@router.get("/verify", response_model=MessageResponseSchema)
async def verify_token(current_user: CurrentUserDep):
    """
    Verify if token is valid
    """
    return {"message": "Token is valid"}
