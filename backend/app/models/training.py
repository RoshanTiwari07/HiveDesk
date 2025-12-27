"""
Training model definitions
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

from ..core.enums import TaskStatus


class TrainingModuleModel(SQLModel, table=True):
    """Training module database model"""
    __tablename__ = "training_modules"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    content: str
    duration_minutes: Optional[int] = None
    is_mandatory: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_by: Optional[str] = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: Optional["UserModel"] = Relationship(back_populates="created_training_modules")
    employee_progress: List["EmployeeTrainingModel"] = Relationship(back_populates="training_module")


class EmployeeTrainingModel(SQLModel, table=True):
    """Employee training progress database model"""
    __tablename__ = "employee_training"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    employee_id: str = Field(foreign_key="users.id")
    training_module_id: str = Field(foreign_key="training_modules.id")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    progress_percentage: int = Field(default=0, ge=0, le=100)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Simplified relationships
    training_module: TrainingModuleModel = Relationship(back_populates="employee_progress")