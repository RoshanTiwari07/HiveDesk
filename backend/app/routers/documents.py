"""
Documents Router - Document upload and management endpoints
"""
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
import json

from ..core.dependencies import SessionDep, CurrentUserDep
from ..services.document_service import DocumentService
from ..schemas.document import DocumentUploadResponseSchema
from ..models.document import DocumentModel
from ..core.enums import UserRole
from sqlmodel import select

router = APIRouter(prefix="/api/documents", tags=["Documents"])

# Upload directory setup
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("/")
async def get_documents(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = 1,
    page_size: int = 50
):
    """
    Get documents - HR sees all, Employee sees their own
    """
    document_service = DocumentService(UPLOAD_DIR)
    from ..core.enums import UserRole
    employee_id = None if current_user.role == UserRole.HR else current_user.id
    
    return await document_service.get_all_documents(
        session,
        page=page,
        page_size=page_size,
        employee_id=employee_id
    )


@router.post(
    "/upload",
    response_model=DocumentUploadResponseSchema
)
async def upload_document(
    session: SessionDep,
    current_user: CurrentUserDep,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    task_id: Optional[str] = Form(None)
):
    """
    Upload document
    """
    document_service = DocumentService(UPLOAD_DIR)
    document = await document_service.upload_document(
        session,
        file=file,
        document_type=document_type,
        employee_id=current_user.id,
        task_id=task_id
    )
    
    return DocumentUploadResponseSchema(
        message="Document uploaded successfully",
        document_id=document.id
    )


@router.get("/{document_id}/ai-analysis")
async def get_document_ai_analysis(
    document_id: str,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Get AI analysis results for a document"""
    
    # Get document
    result = await session.execute(
        select(DocumentModel).where(DocumentModel.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions (employee can see own, HR can see all)
    if current_user.role != UserRole.HR and document.employee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Return AI analysis
    ai_result = {}
    if document.ai_validation_result:
        try:
            ai_result = json.loads(document.ai_validation_result)
        except:
            ai_result = {}
    
    return {
        "document_id": document.id,
        "document_type": document.document_type.value,
        "extracted_text": document.extracted_text,
        "ai_analysis": ai_result,
        "confidence_score": document.ai_confidence_score,
        "processed_at": document.ai_processed_at
    }
