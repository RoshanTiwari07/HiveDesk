"""
FastAPI HR Onboarding System - Clean Architecture Main Application
Refactored with Service Layer, Dependency Injection, and Router Separation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_and_tables
from .routers import (
    auth_router,
    dashboard_router,
    employees_router,
    tasks_router,
    documents_router,
    training_router,
    performance_router,
    onboarding_router,
    assistants_router
)

# Create FastAPI app
app = FastAPI(
    title="HR Onboarding System",
    version="3.0.0",
    description="Clean Architecture HR Onboarding System with Service Layer & Dependency Injection"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        # Add your production frontend URL here when deploying
        # "https://your-app.vercel.app",
        # "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers - Clean separation of concerns
app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router)
app.include_router(employees_router)
app.include_router(tasks_router)
app.include_router(documents_router)
app.include_router(training_router)
app.include_router(performance_router)
app.include_router(onboarding_router)
app.include_router(assistants_router)


# Startup event - Database initialization
@app.on_event("startup")
async def on_startup():
    """
    Initialize database tables and create default users
    Separated startup logic for clarity
    """
    from .models.user import UserModel
    from .core.enums import UserRole
    from .auth import get_password_hash
    from .database import AsyncSessionLocal
    from sqlmodel import select
    
    # Create database tables
    await create_db_and_tables()
    
    # Seed default users if not exists
    async with AsyncSessionLocal() as session:
        hr_stmt = select(UserModel).where(UserModel.email == "john.hr@company.com")
        result = await session.execute(hr_stmt)
        hr_exists = result.scalar_one_or_none()
        
        if not hr_exists:
            print("\n" + "="*50)
            print("🔧 Creating default users...")
            print("="*50)
            
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
            print("\n✅ Default users created successfully!")
            print("\n📋 Test Credentials:")
            print("   HR User:")
            print("   └─ Email: john.hr@company.com")
            print("   └─ Password: password123")
            print("\n   Employees:")
            print("   └─ jane.employee@company.com / password123")
            print("   └─ bob.employee@company.com / password123")
            print("   └─ alice.employee@company.com / password123")
            print("="*50 + "\n")
        else:
            print("✓ Default users already exist, skipping creation.")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    API health check endpoint
    """
    return {
        "status": "healthy",
        "message": "HR Onboarding System API v3.0",
        "architecture": "Clean Architecture with Service Layer"
    }


# Scalar health check endpoint (for Render deployment)
@app.get("/scalar", tags=["Health"])
async def scalar_health():
    """
    Health check endpoint for Render
    """
    return {"status": "ok"}


# Application entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)