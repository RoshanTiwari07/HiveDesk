"""
Document model definitions
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid

from ..core.enums import DocumentType, VerificationStatus


class DocumentModel(SQLModel, table=True):
    """Document database model"""
    __tablename__ = "documents"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    employee_id: str = Field(foreign_key="users.id")
    document_type: DocumentType
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: Optional[int] = None
    mime_type: Optional[str] = Field(max_length=100)
    verification_status: VerificationStatus = Field(default=VerificationStatus.PENDING)
    verification_notes: Optional[str] = None
    verified_by: Optional[str] = Field(foreign_key="users.id")
    verified_at: Optional[datetime] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    task_id: Optional[str] = Field(foreign_key="tasks.id")
    
    # AI fields
    extracted_text: Optional[str] = Field(default=None)
    ai_validation_result: Optional[str] = Field(default=None)
    ai_confidence_score: Optional[float] = Field(default=None)
    ai_processed_at: Optional[datetime] = Field(default=None)
    
    # Simplified relationships
    related_task: Optional["TaskModel"] = Relationship(back_populates="documents")