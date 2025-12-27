"""
Dashboard Router - Dashboard metrics for HR and Employees
"""
from fastapi import APIRouter, Depends

from ..core.dependencies import SessionDep, CurrentUserDep
from ..services.performance_service import PerformanceService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/")
async def get_dashboard(
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Get dashboard data for HR or Employee
    """
    return await PerformanceService.get_dashboard_metrics(
        session,
        user_role=current_user.role.value,
        employee_id=current_user.id if current_user.role.value.lower() == "employee" else None
    )
