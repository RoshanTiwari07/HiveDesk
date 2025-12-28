"""
Employee Chat Assistant
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Dict, Any, List

from .base_ai_service import BaseAIService
from ..models.user import UserModel
from ..models.task import TaskModel, EmployeeTaskModel
from ..models.document import DocumentModel
from ..core.enums import TaskStatus, VerificationStatus

class EmployeeAssistantService(BaseAIService):
    """AI chatbot for employee assistance"""
    
    async def chat(
        self,
        employee_id: str,
        message: str,
        session: AsyncSession,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Process employee chat message"""
        
        # Step 1: Get employee context
        context = await self._build_employee_context(employee_id, session)
        
        # Step 2: Generate response with context
        response = await self._generate_response(message, context, conversation_history)
        
        return response
    
    async def _build_employee_context(
        self,
        employee_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Build comprehensive employee context"""
        
        # Get employee
        emp_result = await session.execute(
            select(UserModel).where(UserModel.id == employee_id)
        )
        employee = emp_result.scalar_one()
        
        # Get pending tasks
        tasks_result = await session.execute(
            select(EmployeeTaskModel, TaskModel)
            .join(TaskModel)
            .where(EmployeeTaskModel.employee_id == employee_id)
            .where(EmployeeTaskModel.status != TaskStatus.COMPLETED)
        )
        pending_tasks = tasks_result.all()
        
        # Get documents
        docs_result = await session.execute(
            select(DocumentModel)
            .where(DocumentModel.employee_id == employee_id)
        )
        documents = docs_result.scalars().all()
        
        return {
            "employee": {
                "name": employee.name,
                "role": employee.role.value,
                "onboarding_status": employee.onboarding_status.value,
                "onboarding_notes": employee.onboarding_notes or ""
            },
            "pending_tasks": [
                {
                    "title": t[1].title,
                    "type": t[1].task_type.value,
                    "description": t[1].description or ""
                } for t in pending_tasks[:10]
            ],
            "documents": [
                {
                    "type": d.document_type.value,
                    "status": d.verification_status.value
                } for d in documents
            ],
            "missing_documents": [
                doc_type for doc_type in ["pan", "aadhaar", "resume", "offer_letter"]
                if not any(d.document_type.value == doc_type for d in documents)
            ]
        }
    
    async def _generate_response(
        self,
        message: str,
        context: Dict[str, Any],
        history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate AI response with employee context"""
        
        history_text = ""
        if history:
            for h in history[-3:]:
                history_text += f"Employee: {h.get('user', '')}\nAssistant: {h.get('bot', '')}\n"
        
        prompt = f"""
        You are an onboarding assistant helping an employee.
        
        Employee Context:
        - Name: {context['employee']['name']}
        - Role: {context['employee']['role']}
        - Onboarding Status: {context['employee']['onboarding_status']}
        
        Pending Tasks: {len(context['pending_tasks'])} tasks
        Missing Documents: {context['missing_documents']}
        
        Conversation History:
        {history_text}
        
        Employee's Question: "{message}"
        
        Provide a helpful, friendly response.
        If they need to take action, be specific about next steps.
        
        Return JSON:
        {{
            "reply": "Friendly response text",
            "action_items": ["specific action 1"],
            "helpful_links": ["/tasks"],
            "urgency": "low"
        }}
        """
        
        result = await self.call_gemini(
            prompt,
            system_instruction="You are a helpful, friendly onboarding assistant. Be concise and actionable.",
            json_mode=True
        )
        
        return result
