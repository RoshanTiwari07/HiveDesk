"""
Employee Service - Handles employee management business logic
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from fastapi import HTTPException, status

from ..models.user import UserModel
from ..models.task import EmployeeTaskModel
from ..models.document import DocumentModel
from ..models.training import EmployeeTrainingModel
from ..schemas.user import UserUpdateSchema
from ..core.enums import UserRole, TaskStatus


class EmployeeService:
    """Service for employee management operations"""
    
    @staticmethod
    async def get_all_employees(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get paginated list of all employees with statistics"""
        # Get total count
        count_stmt = select(func.count()).select_from(UserModel).where(
            UserModel.role == UserRole.EMPLOYEE
        )
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # Get paginated employees
        offset = (page - 1) * page_size
        employees_stmt = select(UserModel).where(
            UserModel.role == UserRole.EMPLOYEE
        ).offset(offset).limit(page_size)
        employees_result = await session.execute(employees_stmt)
        employees = employees_result.scalars().all()
        
        # Build employee data with statistics
        employee_data = []
        for employee in employees:
            stats = await EmployeeService._get_employee_task_stats(session, employee.id)
            employee_data.append({
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "is_active": employee.is_active,
                **stats
            })
        
        return {
            "employees": employee_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def _get_employee_task_stats(session: AsyncSession, employee_id: str) -> Dict[str, Any]:
        """Get task statistics for an employee"""
        tasks_stmt = select(EmployeeTaskModel).where(
            EmployeeTaskModel.employee_id == employee_id
        )
        tasks_result = await session.execute(tasks_stmt)
        tasks = tasks_result.scalars().all()
        
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        total = len(tasks)
        
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": completed / total * 100 if total > 0 else 0
        }
    
    @staticmethod
    async def get_employee_by_id(
        session: AsyncSession,
        employee_id: str,
        raise_if_not_found: bool = True
    ) -> Optional[UserModel]:
        """Get employee by ID"""
        employee = await session.get(UserModel, employee_id)
        
        if not employee or employee.role != UserRole.EMPLOYEE:
            if raise_if_not_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Employee not found"
                )
            return None
        
        return employee
    
    @staticmethod
    async def get_employee_details(
        session: AsyncSession,
        employee_id: str
    ) -> Dict[str, Any]:
        """Get detailed employee information including tasks and documents"""
        employee = await EmployeeService.get_employee_by_id(session, employee_id)
        
        # Get employee's tasks
        tasks_stmt = select(EmployeeTaskModel).where(
            EmployeeTaskModel.employee_id == employee.id
        )
        tasks_result = await session.execute(tasks_stmt)
        tasks = tasks_result.scalars().all()
        
        # Get employee's documents
        docs_stmt = select(DocumentModel).where(
            DocumentModel.employee_id == employee.id
        )
        docs_result = await session.execute(docs_stmt)
        documents = docs_result.scalars().all()
        
        return {
            "employee": {
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "is_active": employee.is_active
            },
            "tasks": [
                {
                    "id": task.id,
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "assigned_at": task.assigned_at,
                    "completed_at": task.completed_at
                } for task in tasks
            ],
            "documents": [
                {
                    "id": doc.id,
                    "document_type": doc.document_type.value,
                    "original_filename": doc.original_filename,
                    "verification_status": doc.verification_status.value,
                    "uploaded_at": doc.uploaded_at
                } for doc in documents
            ]
        }
    
    @staticmethod
    async def update_employee(
        session: AsyncSession,
        employee_id: str,
        update_data: UserUpdateSchema
    ) -> UserModel:
        """Update employee information"""
        employee = await EmployeeService.get_employee_by_id(session, employee_id)
        
        # Update fields
        if update_data.name is not None:
            employee.name = update_data.name
        
        if update_data.email is not None:
            # Check email uniqueness
            email_stmt = select(UserModel).where(
                UserModel.email == update_data.email,
                UserModel.id != employee_id
            )
            email_result = await session.execute(email_stmt)
            if email_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            employee.email = update_data.email
        
        if update_data.is_active is not None:
            employee.is_active = update_data.is_active
        
        employee.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(employee)
        
        return employee
    
    @staticmethod
    async def delete_employee(session: AsyncSession, employee_id: str) -> None:
        """Delete employee and all related records"""
        employee = await EmployeeService.get_employee_by_id(session, employee_id)
        
        # Delete employee tasks
        tasks_stmt = select(EmployeeTaskModel).where(
            EmployeeTaskModel.employee_id == employee_id
        )
        tasks_result = await session.execute(tasks_stmt)
        for task in tasks_result.scalars().all():
            await session.delete(task)
        
        # Delete employee documents
        docs_stmt = select(DocumentModel).where(
            DocumentModel.employee_id == employee_id
        )
        docs_result = await session.execute(docs_stmt)
        for doc in docs_result.scalars().all():
            await session.delete(doc)
        
        # Delete employee training
        training_stmt = select(EmployeeTrainingModel).where(
            EmployeeTrainingModel.employee_id == employee_id
        )
        training_result = await session.execute(training_stmt)
        for training in training_result.scalars().all():
            await session.delete(training)
        
        # Delete employee
        await session.delete(employee)
        await session.commit()
