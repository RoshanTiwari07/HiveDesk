"""
Main entry point for the HR Onboarding System
"""
import asyncio
import uvicorn
import os
from app.main import app
from app.database import create_db_and_tables, AsyncSessionLocal
from app.core.enums import UserRole
from app.auth import get_password_hash

async def create_default_users():
    """Create default HR and employee users if they don't exist"""
    from app.models.user import UserModel
    from sqlmodel import select
    
    async with AsyncSessionLocal() as session:
        # Check if HR user exists
        hr_stmt = select(UserModel).where(UserModel.email == "john.hr@company.com")
        result = await session.execute(hr_stmt)
        hr_exists = result.scalar_one_or_none()
        
        if not hr_exists:
            print("Creating default users...")
            
            # Create HR user
            hr_user = UserModel(
                name="John HR",
                email="john.hr@company.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.HR
            )
            session.add(hr_user)
            
            # Create sample employees
            employees = [
                ("Jane Employee", "jane.employee@company.com"),
                ("Bob Employee", "bob.employee@company.com"),
                ("Alice Employee", "alice.employee@company.com")
            ]
            
            for name, email in employees:
                employee = UserModel(
                    name=name,
                    email=email,
                    password_hash=get_password_hash("password123"),
                    role=UserRole.EMPLOYEE
                )
                session.add(employee)
            
            await session.commit()
            print("✅ Default users created!")
            print("   HR: john.hr@company.com / password123")
            print("   Employees: jane.employee@company.com, bob.employee@company.com, alice.employee@company.com")
            print("   Password for all: password123")
        else:
            print("Default users already exist, skipping creation.")

async def startup():
    """Initialize the application"""
    print("Creating database tables...")
    await create_db_and_tables()
    print("Database tables created successfully!")
    
    # Create default users if they don't exist
    await create_default_users()

if __name__ == "__main__":
    # Database initialization happens in app startup event
    # No need to run it here to avoid event loop conflicts
    
    # Start the server
    print("Starting FastAPI server...")
    
    # Get port from environment (for cloud platforms like Render, Railway)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )