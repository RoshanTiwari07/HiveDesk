"""
Training Router - Training modules and progress tracking
"""
from fastapi import APIRouter, Depends

from ..core.dependencies import SessionDep, CurrentUserDep
from ..services.training_service import TrainingService
from ..schemas.training import TrainingProgressUpdateSchema
from ..schemas.responses import MessageResponseSchema

router = APIRouter(prefix="/api/training", tags=["Training"])


@router.get("/")
async def get_training_modules(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = 1,
    page_size: int = 50
):
    """
    Get training modules with progress for employees
    """
    from ..core.enums import UserRole
    employee_id = current_user.id if current_user.role == UserRole.EMPLOYEE else None
    
    return await TrainingService.get_all_training_modules(
        session,
        page=page,
        page_size=page_size,
        employee_id=employee_id
    )


@router.put(
    "/{training_id}",
    response_model=MessageResponseSchema
)
async def update_training_progress(
    training_id: str,
    progress_data: TrainingProgressUpdateSchema,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """
    Update training progress (Employee)
    """
    await TrainingService.update_training_progress(
        session,
        training_id=training_id,
        employee_id=current_user.id,
        progress_percentage=progress_data.progress_percentage
    )
    
    return {"message": "Training progress updated successfully"}
