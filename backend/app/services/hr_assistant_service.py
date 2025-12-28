"""
HR Natural Language Assistant
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, cast, String
from typing import Dict, Any

from .base_ai_service import BaseAIService
from ..models.user import UserModel
from ..models.document import DocumentModel
from ..models.task import EmployeeTaskModel
from ..core.enums import OnboardingStatus, VerificationStatus, TaskStatus

class HRAssistantService(BaseAIService):
    """AI assistant for HR queries"""
    
    async def answer_query(
        self,
        query: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Process HR natural language query"""
        
        # Step 1: Classify the query intent
        intent = await self._classify_query(query)
        
        # Step 2: Fetch relevant data based on intent
        data = await self._fetch_data_for_intent(intent, session)
        
        # Step 3: Generate natural language answer
        answer = await self._generate_answer(query, intent, data)
        
        return answer
    
    async def _classify_query(self, query: str) -> str:
        """Classify HR query intent"""
        
        prompt = f"""
        Classify this HR query into one of these categories:
        - stuck_employees: Questions about blocked/delayed onboarding
        - pending_documents: Questions about document verification
        - task_completion: Questions about task progress
        - employee_status: Questions about specific employee status
        - general_stats: Questions about overall metrics
        
        Query: "{query}"
        
        Return JSON:
        {{
            "intent": "category_name",
            "confidence": 0.9
        }}
        """
        
        result = await self.call_gemini(prompt, json_mode=True)
        return result.get('intent', 'general_stats')
    
    async def _fetch_data_for_intent(
        self,
        intent: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Fetch data based on query intent"""
        
        if intent == "stuck_employees":
            # Get employees with blocked/in-progress status
            result = await session.execute(
                select(UserModel)
                .where(cast(UserModel.onboarding_status, String).in_(['BLOCKED', 'IN_PROGRESS']))
            )
            employees = result.scalars().all()
            
            return {
                "employees": [
                    {
                        "name": emp.name,
                        "status": emp.onboarding_status.value,
                        "notes": emp.onboarding_notes or "No notes"
                    } for emp in employees[:20]
                ]
            }
        
        elif intent == "pending_documents":
            # Get pending documents
            result = await session.execute(
                select(DocumentModel, UserModel)
                .join(UserModel, DocumentModel.employee_id == UserModel.id)
                .where(cast(DocumentModel.verification_status, String) == 'PENDING')
            )
            docs = result.all()
            
            return {
                "pending_documents": [
                    {
                        "employee_name": d[1].name,
                        "document_type": d[0].document_type.value,
                        "uploaded_at": str(d[0].uploaded_at),
                        "ai_confidence": d[0].ai_confidence_score or 0
                    } for d in docs[:20]
                ]
            }
        
        elif intent == "task_completion":
            # Get task stats
            total_result = await session.execute(select(func.count()).select_from(EmployeeTaskModel))
            total_tasks = total_result.scalar() or 0
            
            completed_result = await session.execute(
                select(func.count()).select_from(EmployeeTaskModel)
                .where(cast(EmployeeTaskModel.status, String) == 'COMPLETED')
            )
            completed_tasks = completed_result.scalar() or 0
            
            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
        
        else:
            # General stats
            total_employees_result = await session.execute(select(func.count()).select_from(UserModel))
            completed_onboarding_result = await session.execute(
                select(func.count()).select_from(UserModel)
                .where(cast(UserModel.onboarding_status, String) == 'COMPLETED')
            )
            
            return {
                "total_employees": total_employees_result.scalar() or 0,
                "completed_onboarding": completed_onboarding_result.scalar() or 0
            }
    
    async def _generate_answer(
        self,
        query: str,
        intent: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate natural language answer"""
        
        prompt = f"""
        HR asked: "{query}"
        
        Query type: {intent}
        
        Database shows:
        {str(data)[:2000]}
        
        Provide a helpful, concise answer in natural language.
        Also suggest actionable next steps.
        
        Return JSON:
        {{
            "answer": "Natural language response",
            "data_summary": {{}},
            "suggestions": ["action1", "action2"],
            "priority": "low"
        }}
        """
        
        result = await self.call_gemini(prompt, json_mode=True)
        result['raw_data'] = data
        
        return result
