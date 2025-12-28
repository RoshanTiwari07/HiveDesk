"""
AI-powered Onboarding Analysis Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Dict, Any
from datetime import datetime

from .base_ai_service import BaseAIService
from ..models.user import UserModel
from ..models.task import TaskModel, EmployeeTaskModel
from ..models.document import DocumentModel
from ..models.training import EmployeeTrainingModel
from ..core.enums import TaskStatus, VerificationStatus, OnboardingStatus, EnrollmentStatus

class OnboardingAIService(BaseAIService):
    """AI-powered onboarding status tracking"""
    
    async def analyze_employee_onboarding(
        self,
        employee_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Comprehensive AI analysis of employee onboarding progress"""
        
        # Step 1: Gather all onboarding data
        data = await self._gather_onboarding_data(employee_id, session)
        
        # Step 2: Send to Gemini for analysis
        analysis = await self._get_ai_analysis(data)
        
        # Step 3: Update employee status based on analysis
        await self._update_employee_status(employee_id, analysis, session)
        
        return analysis
    
    async def _gather_onboarding_data(
        self,
        employee_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Collect all onboarding-related data"""
        
        # Get employee
        employee_result = await session.execute(
            select(UserModel).where(UserModel.id == employee_id)
        )
        employee = employee_result.scalar_one()
        
        # Get tasks
        tasks_result = await session.execute(
            select(EmployeeTaskModel, TaskModel)
            .join(TaskModel)
            .where(EmployeeTaskModel.employee_id == employee_id)
        )
        tasks = tasks_result.all()
        
        # Get documents
        docs_result = await session.execute(
            select(DocumentModel).where(DocumentModel.employee_id == employee_id)
        )
        documents = docs_result.scalars().all()
        
        # Get training
        training_result = await session.execute(
            select(EmployeeTrainingModel)
            .where(EmployeeTrainingModel.employee_id == employee_id)
        )
        training = training_result.scalars().all()
        
        # Structure the data
        return {
            "employee": {
                "id": employee.id,
                "name": employee.name,
                "role": employee.role.value,
                "onboarding_status": employee.onboarding_status.value
            },
            "tasks": {
                "total": len(tasks),
                "completed": len([t for t in tasks if t[0].status == TaskStatus.COMPLETED]),
                "pending": len([t for t in tasks if t[0].status == TaskStatus.PENDING]),
                "details": [
                    {
                        "title": t[1].title,
                        "status": t[0].status.value,
                        "type": t[1].task_type.value
                    } for t in tasks[:10]  # Limit for token usage
                ]
            },
            "documents": {
                "total": len(documents),
                "verified": len([d for d in documents if d.verification_status == VerificationStatus.VERIFIED]),
                "pending": len([d for d in documents if d.verification_status == VerificationStatus.PENDING]),
                "rejected": len([d for d in documents if d.verification_status == VerificationStatus.REJECTED]),
                "details": [
                    {
                        "type": d.document_type.value,
                        "status": d.verification_status.value,
                        "ai_confidence": d.ai_confidence_score
                    } for d in documents
                ]
            },
            "training": {
                "total": len(training),
                "completed": len([t for t in training if t.status == EnrollmentStatus.COMPLETED]),
                "in_progress": len([t for t in training if t.status == EnrollmentStatus.IN_PROGRESS]),
                "not_started": len([t for t in training if t.status == EnrollmentStatus.NOT_STARTED])
            }
        }
    
    async def _get_ai_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI analysis of onboarding status"""
        
        prompt = f"""
        Analyze this employee's onboarding progress:
        
        Employee: {data['employee']['name']} ({data['employee']['role']})
        Current Status: {data['employee']['onboarding_status']}
        
        Tasks:
        - Total: {data['tasks']['total']}
        - Completed: {data['tasks']['completed']}
        - Pending: {data['tasks']['pending']}
        
        Documents:
        - Total: {data['documents']['total']}
        - Verified: {data['documents']['verified']}
        - Pending: {data['documents']['pending']}
        - Rejected: {data['documents']['rejected']}
        
        Training:
        - Total: {data['training']['total']}
        - Completed: {data['training']['completed']}
        - In Progress: {data['training']['in_progress']}
        
        Determine:
        1. Overall onboarding status (not_started / in_progress / completed / blocked)
        2. What is blocking completion (if any)
        3. Next steps for the employee
        4. Estimated completion time
        
        Return JSON:
        {{
            "recommended_status": "in_progress",
            "completion_percentage": 65,
            "blockers": ["Document verification pending"],
            "completed_steps": ["Training", "Profile setup"],
            "pending_steps": ["Document verification", "IT setup"],
            "next_action": "Complete document verification",
            "estimated_days_to_complete": 3,
            "summary": "Employee has completed training but documents are pending verification.",
            "is_on_track": true
        }}
        """
        
        result = await self.call_gemini(
            prompt=prompt,
            system_instruction="You are an onboarding progress analyst. Be accurate and helpful.",
            json_mode=True
        )
        
        return result
    
    async def _update_employee_status(
        self,
        employee_id: str,
        analysis: Dict[str, Any],
        session: AsyncSession
    ):
        """Update employee onboarding status based on AI analysis"""
        
        employee_result = await session.execute(
            select(UserModel).where(UserModel.id == employee_id)
        )
        employee = employee_result.scalar_one()
        
        # Update status
        recommended_status = analysis.get('recommended_status', 'in_progress')
        try:
            employee.onboarding_status = OnboardingStatus(recommended_status)
        except:
            employee.onboarding_status = OnboardingStatus.IN_PROGRESS
        
        # Update notes with AI insights
        employee.onboarding_notes = analysis.get('summary', '')[:500]
        
        # Set completion timestamp if completed
        if recommended_status == 'completed' and not employee.onboarding_completed_at:
            employee.onboarding_completed_at = datetime.utcnow()
        
        # Set started timestamp if in progress
        if recommended_status in ['in_progress', 'blocked'] and not employee.onboarding_started_at:
            employee.onboarding_started_at = datetime.utcnow()
        
        session.add(employee)
        await session.commit()
