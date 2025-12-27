"""
Training Service - Handles training module and progress management
"""
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from fastapi import HTTPException, status

from ..models.training import TrainingModuleModel, EmployeeTrainingModel
from ..core.enums import TaskStatus


class TrainingService:
    """Service for training management operations"""
    
    @staticmethod
    async def get_all_training_modules(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        employee_id: str = None
    ) -> Dict[str, Any]:
        """Get paginated list of training modules"""
        # Get total count
        count_stmt = select(func.count()).select_from(TrainingModuleModel).where(
            TrainingModuleModel.is_active == True
        )
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # Get paginated modules
        offset = (page - 1) * page_size
        modules_stmt = select(TrainingModuleModel).where(
            TrainingModuleModel.is_active == True
        ).offset(offset).limit(page_size)
        modules_result = await session.execute(modules_stmt)
        modules = modules_result.scalars().all()
        
        if employee_id:
            # Include employee progress
            return await TrainingService._build_employee_training_data(
                session, modules, employee_id, total, page, page_size
            )
        else:
            # HR view - just modules
            return {
                "training_modules": [
                    {
                        "id": module.id,
                        "title": module.title,
                        "description": module.description,
                        "content": module.content,
                        "duration_minutes": module.duration_minutes,
                        "is_mandatory": module.is_mandatory,
                        "created_at": module.created_at
                    } for module in modules
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
    
    @staticmethod
    async def _build_employee_training_data(
        session: AsyncSession,
        modules: list,
        employee_id: str,
        total: int,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """Build training data with employee progress"""
        progress_data = []
        
        for module in modules:
            progress_stmt = select(EmployeeTrainingModel).where(
                EmployeeTrainingModel.employee_id == employee_id,
                EmployeeTrainingModel.training_module_id == module.id
            )
            progress_result = await session.execute(progress_stmt)
            progress = progress_result.scalar_one_or_none()
            
            progress_data.append({
                "id": module.id,
                "title": module.title,
                "description": module.description,
                "duration_minutes": module.duration_minutes,
                "is_mandatory": module.is_mandatory,
                "progress": {
                    "status": progress.status.value if progress else "pending",
                    "progress_percentage": progress.progress_percentage if progress else 0,
                    "started_at": progress.started_at if progress else None,
                    "completed_at": progress.completed_at if progress else None
                }
            })
        
        return {
            "training_modules": progress_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def update_training_progress(
        session: AsyncSession,
        training_id: str,
        employee_id: str,
        progress_percentage: float
    ) -> EmployeeTrainingModel:
        """Update employee's training progress"""
        # Find or create training record
        progress_stmt = select(EmployeeTrainingModel).where(
            EmployeeTrainingModel.employee_id == employee_id,
            EmployeeTrainingModel.training_module_id == training_id
        )
        progress_result = await session.execute(progress_stmt)
        progress = progress_result.scalar_one_or_none()
        
        if not progress:
            # Create new progress record
            initial_status = TaskStatus.COMPLETED if progress_percentage >= 100 else TaskStatus.PENDING
            progress = EmployeeTrainingModel(
                employee_id=employee_id,
                training_module_id=training_id,
                progress_percentage=progress_percentage,
                status=initial_status,
                started_at=datetime.utcnow()
            )
            if progress_percentage >= 100:
                progress.completed_at = datetime.utcnow()
            session.add(progress)
        else:
            # Update existing record
            progress.progress_percentage = progress_percentage
            
            # Mark as completed if 100%
            if progress_percentage >= 100:
                progress.status = TaskStatus.COMPLETED
                progress.completed_at = datetime.utcnow()
            else:
                progress.status = TaskStatus.PENDING
        
        await session.commit()
        await session.refresh(progress)
        
        return progress
    
    @staticmethod
    async def get_employee_training_stats(
        session: AsyncSession,
        employee_id: str
    ) -> Dict[str, Any]:
        """Get training statistics for an employee"""
        training_stmt = select(EmployeeTrainingModel).where(
            EmployeeTrainingModel.employee_id == employee_id
        )
        training_result = await session.execute(training_stmt)
        trainings = training_result.scalars().all()
        
        total_training = len(trainings)
        completed_training = len([t for t in trainings if t.status == TaskStatus.COMPLETED])
        training_completion_rate = (completed_training / total_training * 100) if total_training > 0 else 0
        
        return {
            "total_training": total_training,
            "completed_training": completed_training,
            "training_completion_rate": training_completion_rate
        }
