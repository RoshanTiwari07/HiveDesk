"""
FastAPI HR Onboarding System - Async Main Application
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime, timedelta
import os
import aiofiles
from pathlib import Path

from .database import create_db_and_tables, get_async_session
from .models import (
    UserModel, TaskModel, EmployeeTaskModel, DocumentModel,
    TrainingModuleModel, EmployeeTrainingModel
)
from .schemas import (
    UserCreateSchema, UserResponseSchema, UserLoginResponseSchema,
    TaskResponseSchema, EmployeeTaskResponseSchema, DocumentResponseSchema,
    DocumentUploadResponseSchema, TrainingModuleResponseSchema
)
from .core.enums import UserRole, TaskStatus, VerificationStatus, DocumentType
from .auth import (
    authenticate_user, create_access_token, get_current_user, 
    require_role, verify_user_access, get_password_hash
)

# Create FastAPI app
app = FastAPI(
    title="HR Onboarding System",
    version="2.0.0",
    description="Async HR Onboarding System with FastAPI and SQLModel"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Security
security = HTTPBearer()


@app.on_event("startup")
async def on_startup():
    """Create database tables on startup"""
    await create_db_and_tables()


# Authentication endpoints
@app.post("/auth/login", response_model=UserLoginResponseSchema)
async def login(
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
):
    """Login endpoint"""
    user = await authenticate_user(session, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return UserLoginResponseSchema(
        access_token=access_token,
        token_type="bearer",
        user=UserResponseSchema.from_orm(user)
    )


@app.post("/auth/register", dependencies=[Depends(require_role(UserRole.HR))])
async def register_user(
    user_data: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Register new user (HR only)"""
    # Check if user already exists
    statement = select(UserModel).where(UserModel.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = UserModel(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    
    return {"message": "User created successfully", "user_id": db_user.id}


# Dashboard endpoints
@app.get("/{name}/{role}/dashboard")
async def get_dashboard(
    name: str,
    role: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get dashboard data for HR or Employee"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if role.lower() == "hr":
        # HR Dashboard
        employees_stmt = select(UserModel).where(UserModel.role == UserRole.EMPLOYEE)
        employees_result = await session.execute(employees_stmt)
        total_employees = employees_result.scalars().all()
        
        pending_tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.status == TaskStatus.PENDING)
        pending_tasks_result = await session.execute(pending_tasks_stmt)
        pending_tasks = pending_tasks_result.scalars().all()
        
        pending_docs_stmt = select(DocumentModel).where(DocumentModel.verification_status == VerificationStatus.PENDING)
        pending_docs_result = await session.execute(pending_docs_stmt)
        pending_documents = pending_docs_result.scalars().all()
        
        return {
            "role": "hr",
            "total_employees": len(total_employees),
            "pending_tasks": len(pending_tasks),
            "pending_documents": len(pending_documents),
            "recent_activities": []
        }
    
    elif role.lower() == "employee":
        # Employee Dashboard
        user_tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == current_user.id)
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


@app.get("/{name}/{role}/employees", dependencies=[Depends(require_role(UserRole.HR))])
async def get_all_employees(
    name: str,
    role: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get all employees (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    employees_stmt = select(UserModel).where(UserModel.role == UserRole.EMPLOYEE)
    employees_result = await session.execute(employees_stmt)
    employees = employees_result.scalars().all()
    
    employee_data = []
    for employee in employees:
        # Get task statistics
        tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == employee.id)
        tasks_result = await session.execute(tasks_stmt)
        tasks = tasks_result.scalars().all()
        
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        total = len(tasks)
        
        employee_data.append({
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "is_active": employee.is_active,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": completed / total * 100 if total > 0 else 0
        })
    
    return {"employees": employee_data}


@app.get("/{name}/{role}/manage/{employee_name}", dependencies=[Depends(require_role(UserRole.HR))])
async def manage_employee(
    name: str,
    role: str,
    employee_name: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Manage specific employee (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Find employee
    employee_stmt = select(UserModel).where(
        UserModel.name.ilike(f"%{employee_name}%"), 
        UserModel.role == UserRole.EMPLOYEE
    )
    employee_result = await session.execute(employee_stmt)
    employee = employee_result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    # Get employee's tasks
    tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == employee.id)
    tasks_result = await session.execute(tasks_stmt)
    tasks = tasks_result.scalars().all()
    
    # Get employee's documents
    docs_stmt = select(DocumentModel).where(DocumentModel.employee_id == employee.id)
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


@app.post("/{name}/{role}/assign-task", dependencies=[Depends(require_role(UserRole.HR))])
async def assign_task(
    name: str,
    role: str,
    employee_id: str = Form(...),
    task_id: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Assign task to employee (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Check if assignment already exists
    existing_stmt = select(EmployeeTaskModel).where(
        EmployeeTaskModel.employee_id == employee_id,
        EmployeeTaskModel.task_id == task_id
    )
    existing_result = await session.execute(existing_stmt)
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task already assigned")
    
    # Create assignment
    assignment = EmployeeTaskModel(
        employee_id=employee_id,
        task_id=task_id,
        assigned_by=current_user.id
    )
    
    session.add(assignment)
    await session.commit()
    
    return {"message": "Task assigned successfully"}


@app.get("/{name}/{role}/documents")
async def get_documents(
    name: str,
    role: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get documents - HR sees all, Employee sees their own"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if role.lower() == "hr":
        # HR sees all documents
        docs_stmt = select(DocumentModel)
        docs_result = await session.execute(docs_stmt)
        documents = docs_result.scalars().all()
    else:
        # Employee sees only their documents
        docs_stmt = select(DocumentModel).where(DocumentModel.employee_id == current_user.id)
        docs_result = await session.execute(docs_stmt)
        documents = docs_result.scalars().all()
    
    return {
        "documents": [
            {
                "id": doc.id,
                "employee_id": doc.employee_id,
                "document_type": doc.document_type.value,
                "original_filename": doc.original_filename,
                "verification_status": doc.verification_status.value,
                "uploaded_at": doc.uploaded_at,
                "verified_at": doc.verified_at
            } for doc in documents
        ]
    }


@app.post("/{name}/{role}/documents/upload", response_model=DocumentUploadResponseSchema)
async def upload_document(
    name: str,
    role: str,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    task_id: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Upload document"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Validate document type
    try:
        doc_type = DocumentType(document_type.lower())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document type")
    
    # Create file path
    file_extension = Path(file.filename).suffix
    filename = f"{current_user.id}_{doc_type.value}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    # Save file asynchronously
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed")
    
    # Save document metadata
    document = DocumentModel(
        employee_id=current_user.id,
        document_type=doc_type,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=file.size,
        mime_type=file.content_type,
        task_id=task_id
    )
    
    session.add(document)
    await session.commit()
    await session.refresh(document)
    
    return DocumentUploadResponseSchema(
        message="Document uploaded successfully",
        document_id=document.id
    )


@app.get("/{name}/{role}/tasks")
async def get_tasks(
    name: str,
    role: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get tasks - HR sees all tasks, Employee sees assigned tasks"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if role.lower() == "hr":
        # HR sees all tasks
        tasks_stmt = select(TaskModel)
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
            ]
        }
    else:
        # Employee sees assigned tasks
        employee_tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == current_user.id)
        employee_tasks_result = await session.execute(employee_tasks_stmt)
        employee_tasks = employee_tasks_result.scalars().all()
        
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
        
        return {"tasks": task_data}


@app.post("/{name}/{role}/tasks/complete")
async def complete_task(
    name: str,
    role: str,
    assignment_id: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Mark task as completed"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Find task assignment
    assignment = await session.get(EmployeeTaskModel, assignment_id)
    if not assignment or assignment.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task assignment not found")
    
    # Update status
    assignment.status = TaskStatus.COMPLETED
    assignment.completed_at = datetime.utcnow()
    
    session.add(assignment)
    await session.commit()
    
    return {"message": "Task marked as completed"}


@app.get("/{name}/{role}/training")
async def get_training_modules(
    name: str,
    role: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get training modules"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    modules_stmt = select(TrainingModuleModel).where(TrainingModuleModel.is_active == True)
    modules_result = await session.execute(modules_stmt)
    modules = modules_result.scalars().all()
    
    if role.lower() == "employee":
        # Get employee's progress for each module
        progress_data = []
        for module in modules:
            progress_stmt = select(EmployeeTrainingModel).where(
                EmployeeTrainingModel.employee_id == current_user.id,
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
        
        return {"training_modules": progress_data}
    
    else:
        # HR sees all modules
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
            ]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)