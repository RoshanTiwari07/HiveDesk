# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_async_session
from app.models.user import UserModel
from app.schemas.user import (
    UserLoginSchema,
    UserCreateSchema,
    UserLoginResponseSchema,
    UserResponseSchema,
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.core.enums import UserRole

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=UserLoginResponseSchema)
async def login(
    data: UserLoginSchema,
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(UserModel).where(
            UserModel.email == data.email,
            UserModel.is_active == True,
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value},
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponseSchema.from_orm(user),
    }


@router.post("/register")
async def register(
    data: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(UserModel).where(UserModel.email == data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = UserModel(
        name=data.name,
        email=data.email,
        password_hash=get_password_hash(data.password),
        role=data.role,
        is_active=True,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {"message": "Registered successfully"}
