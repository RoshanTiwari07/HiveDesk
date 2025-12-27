"""
Performance Router - Performance metrics and analytics
"""
from fastapi import APIRouter, Depends

from ..core.dependencies import SessionDep, CurrentUserDep, require_role
from ..services.performance_service import PerformanceService
from ..schemas.responses import OverallPerformanceSchema, EmployeePerformanceSchema
from ..core.enums import UserRole

router = APIRouter(prefix="/api/performance", tags=["Performance"])


@router.get(
    "/",
    response_model=OverallPerformanceSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def get_overall_performance(
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Get overall performance statistics (HR only)
    """
    return await PerformanceService.get_overall_performance(session)


@router.get(
    "/{employee_id}",
    response_model=EmployeePerformanceSchema,
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def get_employee_performance(
    employee_id: str,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Get individual employee performance (HR only)
    """
    return await PerformanceService.get_employee_performance(session, employee_id)
