"""
Document Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..core.enums import DocumentType, VerificationStatus


class DocumentBaseSchema(BaseModel):
    """Base document schema"""
    document_type: DocumentType
    original_filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_notes: Optional[str] = None


class DocumentCreateSchema(BaseModel):
    """Schema for creating a new document"""
    document_type: DocumentType
    task_id: Optional[str] = None


class DocumentUpdateSchema(BaseModel):
    """Schema for updating document information"""
    verification_status: Optional[VerificationStatus] = None
    verification_notes: Optional[str] = None


class DocumentResponseSchema(DocumentBaseSchema):
    """Schema for document response"""
    id: str
    employee_id: str
    file_path: str
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    uploaded_at: datetime
    task_id: Optional[str]

    class Config:
        from_attributes = True


class DocumentUploadResponseSchema(BaseModel):
    """Schema for document upload response"""
    message: str
    document_id: str