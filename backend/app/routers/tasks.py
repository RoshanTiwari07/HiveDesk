"""
Tasks Router - Task management and assignment endpoints
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..core.dependencies import SessionDep, CurrentUserDep, require_role
from ..services.task_service import TaskService
from ..schemas.task import TaskCreateSchema, TaskUpdateSchema, TaskResponseSchema
from ..schemas.responses import MessageResponseSchema
from ..core.enums import UserRole

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


class AssignTaskRequest(BaseModel):
    employee_id: str


class CompleteTaskRequest(BaseModel):
    assignment_id: str


@router.get("/")
async def get_tasks(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = 1,
    page_size: int = 50
):
    """
    Get tasks - HR sees all tasks, Employee sees assigned tasks
    """
    if current_user.role == UserRole.HR:
        return await TaskService.get_all_tasks(session, page, page_size)
    else:
        return await TaskService.get_employee_tasks(session, current_user.id, page, page_size)


@router.post(
    "/",
    response_model=TaskResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def create_task(
    task_data: TaskCreateSchema,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Create new task (HR only)
    """
    task = await TaskService.create_task(session, task_data, current_user.id)
    return TaskResponseSchema.from_orm(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def update_task(
    task_id: str,
    update_data: TaskUpdateSchema,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Update task (HR only)
    """
    task = await TaskService.update_task(session, task_id, update_data)
    return TaskResponseSchema.from_orm(task)


@router.delete(
    "/{task_id}",
    response_model=MessageResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def delete_task(
    task_id: str,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Delete task (HR only)
    """
    await TaskService.delete_task(session, task_id)
    return {"message": "Task deleted successfully"}


@router.post(
    "/{task_id}/assign",
    response_model=MessageResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def assign_task(
    task_id: str,
    request_data: AssignTaskRequest,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Assign task to employee (HR only)
    """
    await TaskService.assign_task_to_employee(
        session,
        request_data.employee_id,
        task_id,
        current_user.id
    )
    return {"message": "Task assigned successfully"}


@router.patch("/{task_id}/complete", response_model=MessageResponseSchema)
async def complete_task(
    task_id: str,
    request_data: CompleteTaskRequest,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Mark task as completed (Employee)
    """
    await TaskService.complete_task(session, request_data.assignment_id, current_user.id)
    return {"message": "Task marked as completed"}
