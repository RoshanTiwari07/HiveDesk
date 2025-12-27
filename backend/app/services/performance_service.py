"""
Performance Service - Handles performance metrics and analytics
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from ..models.user import UserModel
from ..models.task import EmployeeTaskModel
from ..models.training import TrainingModuleModel, EmployeeTrainingModel
from ..models.document import DocumentModel
from ..core.enums import UserRole, TaskStatus, VerificationStatus


class PerformanceService:
    """Service for performance metrics and analytics"""
    
    @staticmethod
    async def get_overall_performance(session: AsyncSession) -> Dict[str, Any]:
        """Get overall HR dashboard performance statistics"""
        # Total employees
        total_emp_stmt = select(func.count()).select_from(UserModel).where(
            UserModel.role == UserRole.EMPLOYEE
        )
        total_emp_result = await session.execute(total_emp_stmt)
        total_employees = total_emp_result.scalar()
        
        # Active employees
        active_emp_stmt = select(func.count()).select_from(UserModel).where(
            UserModel.role == UserRole.EMPLOYEE,
            UserModel.is_active == True
        )
        active_emp_result = await session.execute(active_emp_stmt)
        active_employees = active_emp_result.scalar()
        
        # Total tasks assigned
        total_tasks_stmt = select(func.count()).select_from(EmployeeTaskModel)
        total_tasks_result = await session.execute(total_tasks_stmt)
        total_tasks_assigned = total_tasks_result.scalar()
        
        # Total tasks completed
        completed_tasks_stmt = select(func.count()).select_from(EmployeeTaskModel).where(
            EmployeeTaskModel.status == TaskStatus.COMPLETED
        )
        completed_tasks_result = await session.execute(completed_tasks_stmt)
        total_tasks_completed = completed_tasks_result.scalar()
        
        # Overall task completion rate
        overall_task_completion_rate = (
            (total_tasks_completed / total_tasks_assigned * 100)
            if total_tasks_assigned > 0 else 0
        )
        
        # Total training modules
        total_training_stmt = select(func.count()).select_from(TrainingModuleModel).where(
            TrainingModuleModel.is_active == True
        )
        total_training_result = await session.execute(total_training_stmt)
        total_training_modules = total_training_result.scalar()
        
        # Average training completion
        completed_training_stmt = select(func.count()).select_from(EmployeeTrainingModel).where(
            EmployeeTrainingModel.status == TaskStatus.COMPLETED
        )
        completed_training_result = await session.execute(completed_training_stmt)
        completed_training_count = completed_training_result.scalar()
        
        total_training_assignments_stmt = select(func.count()).select_from(EmployeeTrainingModel)
        total_training_assignments_result = await session.execute(total_training_assignments_stmt)
        total_training_assignments = total_training_assignments_result.scalar()
        
        avg_training_completion = (
            (completed_training_count / total_training_assignments * 100)
            if total_training_assignments > 0 else 0
        )
        
        # Pending documents
        pending_docs_stmt = select(func.count()).select_from(DocumentModel).where(
            DocumentModel.verification_status == VerificationStatus.PENDING
        )
        pending_docs_result = await session.execute(pending_docs_stmt)
        pending_documents = pending_docs_result.scalar()
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "total_tasks_assigned": total_tasks_assigned,
            "total_tasks_completed": total_tasks_completed,
            "overall_task_completion_rate": overall_task_completion_rate,
            "total_training_modules": total_training_modules,
            "avg_training_completion": avg_training_completion,
            "pending_documents": pending_documents
        }
    
    @staticmethod
    async def get_employee_performance(
        session: AsyncSession,
        employee_id: str
    ) -> Dict[str, Any]:
        """Get individual employee performance metrics"""
        # Get employee
        employee = await session.get(UserModel, employee_id)
        if not employee or employee.role != UserRole.EMPLOYEE:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Get task statistics
        tasks_stmt = select(EmployeeTaskModel).where(
            EmployeeTaskModel.employee_id == employee_id
        )
        tasks_result = await session.execute(tasks_stmt)
        tasks = tasks_result.scalars().all()
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        pending_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average task completion time
        completed_with_dates = [
            t for t in tasks
            if t.status == TaskStatus.COMPLETED and t.completed_at and t.assigned_at
        ]
        if completed_with_dates:
            total_days = sum([
                (t.completed_at - t.assigned_at).days
                for t in completed_with_dates
            ])
            avg_task_completion_days = total_days / len(completed_with_dates)
        else:
            avg_task_completion_days = None
        
        # Get training statistics
        training_stmt = select(EmployeeTrainingModel).where(
            EmployeeTrainingModel.employee_id == employee_id
        )
        training_result = await session.execute(training_stmt)
        trainings = training_result.scalars().all()
        
        total_training = len(trainings)
        completed_training = len([t for t in trainings if t.status == TaskStatus.COMPLETED])
        training_completion_rate = (
            (completed_training / total_training * 100)
            if total_training > 0 else 0
        )
        
        return {
            "employee_id": employee.id,
            "employee_name": employee.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": completion_rate,
            "total_training": total_training,
            "completed_training": completed_training,
            "training_completion_rate": training_completion_rate,
            "avg_task_completion_days": avg_task_completion_days
        }
    
    @staticmethod
    async def get_dashboard_metrics(
        session: AsyncSession,
        user_role: str,
        employee_id: str = None
    ) -> Dict[str, Any]:
        """Get role-specific dashboard metrics"""
        if user_role.lower() == "hr":
            # HR Dashboard
            employees_stmt = select(UserModel).where(UserModel.role == UserRole.EMPLOYEE)
            employees_result = await session.execute(employees_stmt)
            total_employees = employees_result.scalars().all()
            
            pending_tasks_stmt = select(EmployeeTaskModel).where(
                EmployeeTaskModel.status == TaskStatus.PENDING
            )
            pending_tasks_result = await session.execute(pending_tasks_stmt)
            pending_tasks = pending_tasks_result.scalars().all()
            
            pending_docs_stmt = select(DocumentModel).where(
                DocumentModel.verification_status == VerificationStatus.PENDING
            )
            pending_docs_result = await session.execute(pending_docs_stmt)
            pending_documents = pending_docs_result.scalars().all()
            
            return {
                "role": "hr",
                "total_employees": len(total_employees),
                "pending_tasks": len(pending_tasks),
                "pending_documents": len(pending_documents),
                "recent_activities": []
            }
        
        elif user_role.lower() == "employee":
            # Employee Dashboard
            user_tasks_stmt = select(EmployeeTaskModel).where(
                EmployeeTaskModel.employee_id == employee_id
            )
            user_tasks_result = await session.execute(user_tasks_stmt)
            user_tasks = user_tasks_result.scalars().all()
            
            completed_tasks = [task for task in user_tasks if task.status == TaskStatus.COMPLETED]
            pending_tasks = [task for task in user_tasks if task.status == TaskStatus.PENDING]
            
            return {
                "role": "employee",
                "total_tasks": len(user_tasks),
                "completed_tasks": len(completed_tasks),
                "pending_tasks": len(pending_tasks),
                "completion_rate": len(completed_tasks) / len(user_tasks) * 100 if user_tasks else 0
            }
