"""
Training Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..core.enums import TaskStatus


class TrainingModuleBaseSchema(BaseModel):
    """Base training module schema"""
    title: str
    description: Optional[str] = None
    content: str
    duration_minutes: Optional[int] = None
    is_mandatory: bool = False
    is_active: bool = True


class TrainingModuleCreateSchema(TrainingModuleBaseSchema):
    """Schema for creating a new training module"""
    pass


class TrainingModuleUpdateSchema(BaseModel):
    """Schema for updating training module information"""
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_mandatory: Optional[bool] = None
    is_active: Optional[bool] = None


class TrainingModuleResponseSchema(TrainingModuleBaseSchema):
    """Schema for training module response"""
    id: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeTrainingBaseSchema(BaseModel):
    """Base employee training schema"""
    status: TaskStatus = TaskStatus.PENDING
    progress_percentage: int = 0


class EmployeeTrainingCreateSchema(BaseModel):
    """Schema for creating employee training assignment"""
    employee_id: str
    training_module_id: str


class EmployeeTrainingUpdateSchema(BaseModel):
    """Schema for updating employee training progress"""
    status: Optional[TaskStatus] = None
    progress_percentage: Optional[int] = None


class TrainingProgressUpdateSchema(BaseModel):
    """Schema for updating training progress percentage"""
    progress_percentage: float


class EmployeeTrainingResponseSchema(EmployeeTrainingBaseSchema):
    """Schema for employee training response"""
    id: str
    employee_id: str
    training_module_id: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class EmployeeTrainingWithModuleSchema(EmployeeTrainingResponseSchema):
    """Schema for employee training with module details"""
    training_module: TrainingModuleResponseSchema

    class Config:
        from_attributes = True