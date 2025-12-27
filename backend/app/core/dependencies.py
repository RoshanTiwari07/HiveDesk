"""
Core Dependencies - Reusable dependency injection utilities
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session
from ..models.user import UserModel
from ..auth import get_current_user
from ..core.enums import UserRole


# Type aliases for cleaner dependency injection
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]


def require_role(*roles: UserRole):
    """
    Dependency factory to require specific roles
    Usage: dependencies=[Depends(require_role(UserRole.HR))]
    """
    async def role_checker(current_user: CurrentUserDep) -> UserModel:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in roles]}"
            )
        return current_user
    return role_checker
