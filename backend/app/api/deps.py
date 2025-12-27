# app/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import UserModel
from app.core.security import decode_token
from app.core.enums import UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session),
) -> UserModel:
    token = credentials.credentials

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    result = await session.execute(
        select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_active == True,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


def require_role(role: UserRole):
    async def checker(
        user: UserModel = Depends(get_current_user),
    ) -> UserModel:
        if user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        return user

    return checker


def verify_user_access(name: str, role: str, current_user: UserModel) -> bool:
    """Verify if current user can access the requested user's data"""
    # HR can access any employee's data
    if current_user.role == UserRole.HR:
        return True

    # Employee can only access their own data
    if current_user.role == UserRole.EMPLOYEE:
        return current_user.name.lower() == name.lower() and current_user.role.value == role.lower()

    return False
