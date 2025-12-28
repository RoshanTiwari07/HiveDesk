"""
Onboarding AI Router
"""
from fastapi import APIRouter, HTTPException

from ..core.dependencies import SessionDep, CurrentUserDep
from ..services.onboarding_ai_service import OnboardingAIService
from ..core.enums import UserRole

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])
onboarding_service = OnboardingAIService()

@router.get("/employee/{employee_id}/status")
async def get_onboarding_status(
    employee_id: str,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Get AI-powered onboarding status for an employee"""
    
    # Access control: HR can see all, employees can see own
    if current_user.role != UserRole.HR and current_user.id != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        analysis = await onboarding_service.analyze_employee_onboarding(
            employee_id, session
        )
        
        return {
            "employee_id": employee_id,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/employee/{employee_id}/refresh")
async def refresh_onboarding_status(
    employee_id: str,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Manually refresh onboarding status (recalculate with AI)"""
    
    if current_user.role != UserRole.HR and current_user.id != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        analysis = await onboarding_service.analyze_employee_onboarding(
            employee_id, session
        )
        
        return {
            "message": "Onboarding status refreshed",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")
