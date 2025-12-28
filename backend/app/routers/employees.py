"""
Employees Router - Employee management endpoints
"""
from fastapi import APIRouter, Depends
from sqlmodel import select
from typing import Dict, Any
import json

from ..core.dependencies import SessionDep, CurrentUserDep, require_role
from ..services.employee_service import EmployeeService
from ..services.ai_document_service import AIDocumentService
from ..schemas.user import UserResponseSchema, UserUpdateSchema
from ..schemas.responses import (
    EmployeeListResponseSchema,
    EmployeeManageResponseSchema,
    MessageResponseSchema
)
from ..core.enums import UserRole
from ..models.document import DocumentModel
from ..models.user import UserModel

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


@router.get(
    "/{employee_id}/profile",
    dependencies=[Depends(require_role(UserRole.HR))]
)
async def get_employee_profile(
    employee_id: str,
    session: SessionDep,
    current_user: CurrentUserDep
) -> Dict[str, Any]:
    """
    Get complete employee profile with ALL 6 document slots
    Shows uploaded documents with masked data, and empty slots for pending uploads
    HR only access
    """
    from ..core.enums import DocumentType
    
    # Get employee basic info
    result = await session.execute(
        select(UserModel).where(UserModel.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get all documents for this employee
    doc_result = await session.execute(
        select(DocumentModel)
        .where(DocumentModel.employee_id == employee_id)
        .order_by(DocumentModel.uploaded_at.desc())
    )
    documents = doc_result.scalars().all()
    
    # Process uploaded documents with masking
    ai_service = AIDocumentService()
    uploaded_docs = {}
    
    for doc in documents:
        # Get masked data
        masked_data = ai_service.get_masked_document_data(doc)
        
        doc_type = doc.document_type.value
        # Keep only the latest document of each type
        if doc_type not in uploaded_docs:
            uploaded_docs[doc_type] = {
                "document_id": doc.id,
                "document_type": doc_type,
                "original_filename": doc.original_filename,
                "uploaded_at": str(doc.uploaded_at),
                "verification_status": doc.verification_status.value,
                "verification_notes": doc.verification_notes,
                "verified_at": str(doc.verified_at) if doc.verified_at else None,
                "ai_confidence_score": doc.ai_confidence_score,
                "extracted_fields": masked_data,
                "issues": masked_data.get('issues', []),
                "missing_fields": masked_data.get('missing_fields', []),
                "status": "uploaded"
            }
    
    # Create document slots for ALL 6 required document types
    ALL_DOCUMENT_TYPES = [
        DocumentType.AADHAAR.value,
        DocumentType.PAN.value,
        DocumentType.RESUME.value,
        DocumentType.OFFER_LETTER.value,
        DocumentType.PF_FORM.value,
        DocumentType.PHOTO.value
    ]
    
    document_slots = []
    for doc_type in ALL_DOCUMENT_TYPES:
        if doc_type in uploaded_docs:
            # Document uploaded
            document_slots.append(uploaded_docs[doc_type])
        else:
            # Pending upload - empty slot
            document_slots.append({
                "document_type": doc_type,
                "status": "pending_upload",
                "verification_status": "not_uploaded",
                "uploaded_at": None,
                "verified_at": None,
                "ai_confidence_score": None,
                "extracted_fields": {},
                "issues": [],
                "missing_fields": []
            })
    
    return {
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "role": employee.role.value,
            "onboarding_status": employee.onboarding_status.value,
            "is_active": employee.is_active,
            "created_at": str(employee.created_at)
        },
        "document_slots": document_slots,  # All 6 slots (uploaded or pending)
        "document_summary": {
            "total_required": 6,
            "uploaded": len(uploaded_docs),
            "verified": len([d for d in uploaded_docs.values() if d['verification_status'] == 'verified']),
            "pending_verification": len([d for d in uploaded_docs.values() if d['verification_status'] == 'pending']),
            "pending_upload": 6 - len(uploaded_docs),
            "rejected": len([d for d in uploaded_docs.values() if d['verification_status'] == 'rejected']),
            "completion_percentage": round((len(uploaded_docs) / 6) * 100)
        }
    }
