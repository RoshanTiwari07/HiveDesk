"""
Generate employee token for testing
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.user import UserModel
from app.core.enums import UserRole
from app.auth import get_password_hash, create_access_token
from sqlalchemy import select

async def get_employee_token():
    async with AsyncSessionLocal() as session:
        # Check if employee exists
        result = await session.execute(
            select(UserModel).where(UserModel.role == UserRole.EMPLOYEE)
        )
        employee = result.scalars().first()
        
        if not employee:
            # Create test employee
            employee = UserModel(
                name="Test Employee",
                email="test.employee@company.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.EMPLOYEE,
                is_active=True
            )
            session.add(employee)
            await session.commit()
            await session.refresh(employee)
            print("✓ Created new employee user")
        
        # Generate token
        token = create_access_token(data={"sub": employee.email})
        
        print("\n" + "="*70)
        print("EMPLOYEE TOKEN FOR TESTING")
        print("="*70)
        print(f"\nEmail: {employee.email}")
        print(f"Password: password123")
        print(f"Role: {employee.role.value}")
        print(f"User ID: {employee.id}")
        print(f"\nACCESS TOKEN:")
        print(token)
        print("\n" + "="*70)
        print("HOW TO USE IN SWAGGER:")
        print("="*70)
        print("1. Go to http://localhost:8000/docs")
        print("2. Click 'Authorize' button (top right)")
        print("3. Paste the token above")
        print("4. Click 'Authorize' then 'Close'")
        print("5. Test any endpoint!")
        print("="*70 + "\n")

asyncio.run(get_employee_token())
