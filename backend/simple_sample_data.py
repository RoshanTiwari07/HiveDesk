"""
Simple script to create sample data without using relationships
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.core.enums import UserRole, TaskType, DocumentType
from app.auth import get_password_hash


async def create_simple_sample_data():
    """Create sample users and tasks without relationships"""
    async with AsyncSessionLocal() as session:
        # Create HR user
        from app.models.user import UserModel
        
        hr_user = UserModel(
            name="John HR",
            email="john.hr@company.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.HR
        )
        session.add(hr_user)
        await session.commit()
        await session.refresh(hr_user)
        
        # Create Employee users
        employees = []
        employee_data = [
            ("Jane Employee", "jane.employee@company.com"),
            ("Bob Employee", "bob.employee@company.com"),
            ("Alice Employee", "alice.employee@company.com")
        ]
        
        for name, email in employee_data:
            employee = UserModel(
                name=name,
                email=email,
                password_hash=get_password_hash("password123"),
                role=UserRole.EMPLOYEE
            )
            session.add(employee)
            employees.append(employee)
        
        await session.commit()
        
        for employee in employees:
            await session.refresh(employee)
        
        print("Sample data created successfully!")
        print("\nLogin credentials:")
        print("HR User: john.hr@company.com / password123")
        print("Employees:")
        for employee in employees:
            print(f"  {employee.email} / password123")


if __name__ == "__main__":
    asyncio.run(create_simple_sample_data())