"""
Database models for HR Onboarding System
"""
from .user import UserModel
from .task import TaskModel, EmployeeTaskModel
from .document import DocumentModel
from .training import TrainingModuleModel, EmployeeTrainingModel

# Import all models to ensure they are registered with SQLModel
__all__ = [
    "UserModel",
    "TaskModel", 
    "EmployeeTaskModel",
    "DocumentModel",
    "TrainingModuleModel",
    "EmployeeTrainingModel"
]