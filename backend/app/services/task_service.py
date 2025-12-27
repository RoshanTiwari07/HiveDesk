"""
Task Service - Handles task management business logic
"""
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from fastapi import HTTPException, status

from ..models.task import TaskModel, EmployeeTaskModel
from ..schemas.task import TaskCreateSchema, TaskUpdateSchema
from ..core.enums import TaskStatus


class TaskService:
    """Service for task management operations"""
    
    @staticmethod
    async def get_all_tasks(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get paginated list of all tasks (HR view)"""
        # Get total count
        count_stmt = select(func.count()).select_from(TaskModel)
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # Get paginated tasks
        offset = (page - 1) * page_size
        tasks_stmt = select(TaskModel).offset(offset).limit(page_size)
        tasks_result = await session.execute(tasks_stmt)
        tasks = tasks_result.scalars().all()
        
        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "task_type": task.task_type.value,
                    "is_active": task.is_active,
                    "created_at": task.created_at
                } for task in tasks
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_employee_tasks(
        session: AsyncSession,
        employee_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get paginated list of tasks assigned to an employee"""
        # Get total count
        count_stmt = select(func.count()).select_from(EmployeeTaskModel).where(
            EmployeeTaskModel.employee_id == employee_id
        )
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # Get paginated employee tasks
        offset = (page - 1) * page_size
        employee_tasks_stmt = select(EmployeeTaskModel).where(
            EmployeeTaskModel.employee_id == employee_id
        ).offset(offset).limit(page_size)
        employee_tasks_result = await session.execute(employee_tasks_stmt)
        employee_tasks = employee_tasks_result.scalars().all()
        
        # Build task data with details
        task_data = []
        for emp_task in employee_tasks:
            task = await session.get(TaskModel, emp_task.task_id)
            if task:
                task_data.append({
                    "assignment_id": emp_task.id,
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "task_type": task.task_type.value,
                    "content": task.content,
                    "status": emp_task.status.value,
                    "assigned_at": emp_task.assigned_at,
                    "completed_at": emp_task.completed_at
                })
        
        return {
            "tasks": task_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def create_task(
        session: AsyncSession,
        task_data: TaskCreateSchema,
        created_by: str
    ) -> TaskModel:
        """Create a new task"""
        new_task = TaskModel(
            title=task_data.title,
            description=task_data.description,
            task_type=task_data.task_type,
            content=task_data.content,
            required_document_type=task_data.required_document_type,
            is_active=task_data.is_active,
            created_by=created_by
        )
        
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        
        return new_task
    
    @staticmethod
    async def get_task_by_id(
        session: AsyncSession,
        task_id: str,
        raise_if_not_found: bool = True
    ) -> TaskModel:
        """Get task by ID"""
        task = await session.get(TaskModel, task_id)
        if not task and raise_if_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
    
    @staticmethod
    async def update_task(
        session: AsyncSession,
        task_id: str,
        update_data: TaskUpdateSchema
    ) -> TaskModel:
        """Update task information"""
        task = await TaskService.get_task_by_id(session, task_id)
        
        if update_data.title is not None:
            task.title = update_data.title
        if update_data.description is not None:
            task.description = update_data.description
        if update_data.content is not None:
            task.content = update_data.content
        if update_data.is_active is not None:
            task.is_active = update_data.is_active
        
        task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(task)
        
        return task
    
    @staticmethod
    async def delete_task(session: AsyncSession, task_id: str) -> None:
        """Delete task and all assignments"""
        task = await TaskService.get_task_by_id(session, task_id)
        
        # Delete task assignments first
        assignments_stmt = select(EmployeeTaskModel).where(
            EmployeeTaskModel.task_id == task_id
        )
        assignments_result = await session.execute(assignments_stmt)
        for assignment in assignments_result.scalars().all():
            await session.delete(assignment)
        
        # Delete task
        await session.delete(task)
        await session.commit()
    
    @staticmethod
    async def assign_task_to_employee(
        session: AsyncSession,
        employee_id: str,
        task_id: str,
        assigned_by: str
    ) -> EmployeeTaskModel:
        """Assign a task to an employee"""
        # Check if assignment already exists
        existing_stmt = select(EmployeeTaskModel).where(
            EmployeeTaskModel.employee_id == employee_id,
            EmployeeTaskModel.task_id == task_id
        )
        existing_result = await session.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task already assigned"
            )
        
        # Create assignment
        assignment = EmployeeTaskModel(
            employee_id=employee_id,
            task_id=task_id,
            assigned_by=assigned_by
        )
        
        session.add(assignment)
        await session.commit()
        await session.refresh(assignment)
        
        return assignment
    
    @staticmethod
    async def complete_task(
        session: AsyncSession,
        assignment_id: str,
        employee_id: str
    ) -> EmployeeTaskModel:
        """Mark task as completed"""
        assignment = await session.get(EmployeeTaskModel, assignment_id)
        
        if not assignment or assignment.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task assignment not found"
            )
        
        assignment.status = TaskStatus.COMPLETED
        assignment.completed_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(assignment)
        
        return assignment
