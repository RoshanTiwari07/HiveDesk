"""
Documents Router - Document upload and management endpoints
"""
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form

from ..core.dependencies import SessionDep, CurrentUserDep
from ..services.document_service import DocumentService
from ..schemas.document import DocumentUploadResponseSchema

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
