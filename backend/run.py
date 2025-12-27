"""
Main entry point for the HR Onboarding System
"""
import asyncio
import uvicorn
from app.main import app
from app.database import create_db_and_tables

async def startup():
    """Initialize the application"""
    print("Creating database tables...")
    await create_db_and_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    # Create database tables
    asyncio.run(startup())
    
    # Start the server
    print("Starting FastAPI server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )