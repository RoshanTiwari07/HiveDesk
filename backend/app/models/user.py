"""
User model definitions
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

from ..core.enums import UserRole


class UserModel(SQLModel, table=True):
    """User database model"""
    __tablename__ = "users"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    role: UserRole
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Simplified relationships - only the ones that don't cause conflicts
    created_tasks: List["TaskModel"] = Relationship(back_populates="creator")
    created_training_modules: List["TrainingModuleModel"] = Relationship(back_populates="creator")