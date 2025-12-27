"""
Employees Router - Employee management endpoints
"""
from fastapi import APIRouter, Depends

from ..core.dependencies import SessionDep, CurrentUserDep, require_role
from ..services.employee_service import EmployeeService
from ..schemas.user import UserResponseSchema, UserUpdateSchema
from ..schemas.responses import (
    EmployeeListResponseSchema,
    EmployeeManageResponseSchema,
    MessageResponseSchema
)
from ..core.enums import UserRole

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get(
    "/",
    response_model=EmployeeListResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def get_all_employees(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = 1,
    page_size: int = 50
):
    """
    Get all employees with pagination (HR only)
    """
    return await EmployeeService.get_all_employees(session, page, page_size)


@router.get(
    "/{employee_id}",
    response_model=EmployeeManageResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def manage_employee(
    employee_id: str,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Get detailed employee information (HR only)
    """
    return await EmployeeService.get_employee_details(session, employee_id)


@router.put(
    "/{employee_id}",
    response_model=UserResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def update_employee(
    employee_id: str,
    update_data: UserUpdateSchema,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Update employee information (HR only)
    """
    employee = await EmployeeService.update_employee(session, employee_id, update_data)
    return UserResponseSchema.from_orm(employee)


@router.delete(
    "/{employee_id}",
    response_model=MessageResponseSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def delete_employee(
    employee_id: str,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Delete employee and all related records (HR only)
    """
    await EmployeeService.delete_employee(session, employee_id)
    return {"message": "Employee deleted successfully"}
