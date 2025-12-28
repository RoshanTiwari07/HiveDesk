"""
AI Assistants Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..core.dependencies import SessionDep, CurrentUserDep
from ..services.hr_assistant_service import HRAssistantService
from ..services.employee_assistant_service import EmployeeAssistantService
from ..core.enums import UserRole

router = APIRouter(prefix="/api/assistant", tags=["assistants"])
hr_assistant = HRAssistantService()
employee_assistant = EmployeeAssistantService()

class QueryRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

# HR Assistant
@router.post("/hr/ask")
async def ask_hr_assistant(
    request: QueryRequest,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """HR natural language query assistant"""
    
    # Only HR can use this
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="HR access only")
    
    try:
        answer = await hr_assistant.answer_query(request.query, session)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# Employee Assistant
@router.post("/employee/chat")
async def employee_chat(
    request: ChatRequest,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Employee onboarding chatbot"""
    
    try:
        response = await employee_assistant.chat(
            employee_id=current_user.id,
            message=request.message,
            session=session,
            conversation_history=request.history
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
