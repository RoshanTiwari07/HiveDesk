import asyncio
from app.database import AsyncSessionLocal
from app.models.user import UserModel
from sqlalchemy import select

async def check_users():
    async with AsyncSessionLocal() as s:
        r = await s.execute(select(UserModel))
        users = r.scalars().all()
        print("\n=== ALL USERS IN DATABASE ===")
        for u in users:
            print(f"Email: {u.email} | Role: {u.role.value} | Active: {u.is_active}")
        print()

asyncio.run(check_users())
