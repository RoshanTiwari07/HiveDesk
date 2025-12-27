"""
Task model definitions
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

from ..core.enums import TaskType, TaskStatus, DocumentType


class TaskModel(SQLModel, table=True):
    """Task database model"""
    __tablename__ = "tasks"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    task_type: TaskType
    content: Optional[str] = None  # For READ tasks
    required_document_type: Optional[DocumentType] = None  # For UPLOAD tasks
    is_active: bool = Field(default=True)
    created_by: Optional[str] = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: Optional["UserModel"] = Relationship(back_populates="created_tasks")
    employee_assignments: List["EmployeeTaskModel"] = Relationship(back_populates="task")
    documents: List["DocumentModel"] = Relationship(back_populates="related_task")


class EmployeeTaskModel(SQLModel, table=True):
    """Employee task assignment database model"""
    __tablename__ = "employee_tasks"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    employee_id: str = Field(foreign_key="users.id")
    task_id: str = Field(foreign_key="tasks.id")
    assigned_by: Optional[str] = Field(foreign_key="users.id")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    notes: Optional[str] = None
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Simplified relationships
    task: TaskModel = Relationship(back_populates="employee_assignments")