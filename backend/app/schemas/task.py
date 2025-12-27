"""
Task Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..core.enums import TaskType, TaskStatus, DocumentType


class TaskBaseSchema(BaseModel):
    """Base task schema"""
    title: str
    description: Optional[str] = None
    task_type: TaskType
    content: Optional[str] = None
    required_document_type: Optional[DocumentType] = None
    is_active: bool = True


class TaskCreateSchema(TaskBaseSchema):
    """Schema for creating a new task"""
    pass


class TaskUpdateSchema(BaseModel):
    """Schema for updating task information"""
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


class TaskResponseSchema(TaskBaseSchema):
    """Schema for task response"""
    id: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeTaskBaseSchema(BaseModel):
    """Base employee task assignment schema"""
    status: TaskStatus = TaskStatus.PENDING
    notes: Optional[str] = None


class EmployeeTaskCreateSchema(BaseModel):
    """Schema for creating employee task assignment"""
    employee_id: str
    task_id: str
    notes: Optional[str] = None


class EmployeeTaskUpdateSchema(BaseModel):
    """Schema for updating employee task assignment"""
    status: Optional[TaskStatus] = None
    notes: Optional[str] = None


class EmployeeTaskResponseSchema(EmployeeTaskBaseSchema):
    """Schema for employee task assignment response"""
    id: str
    employee_id: str
    task_id: str
    assigned_by: Optional[str]
    assigned_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class EmployeeTaskWithDetailsSchema(EmployeeTaskResponseSchema):
    """Schema for employee task with task details"""
    task: TaskResponseSchema

    class Config:
        from_attributes = True