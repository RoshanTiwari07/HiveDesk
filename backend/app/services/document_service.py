"""
Document Service - Handles document management business logic
"""
from typing import Dict, Any
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from fastapi import UploadFile, HTTPException, status
import aiofiles

from ..models.document import DocumentModel
from ..core.enums import DocumentType, VerificationStatus
from .ai_document_service import AIDocumentService


class DocumentService:
    """Service for document management operations"""
    
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.ai_service = AIDocumentService()
    
    async def get_all_documents(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        employee_id: str = None
    ) -> Dict[str, Any]:
        """Get paginated list of documents"""
        # Build base query
        if employee_id:
            count_stmt = select(func.count()).select_from(DocumentModel).where(
                DocumentModel.employee_id == employee_id
            )
            docs_stmt = select(DocumentModel).where(
                DocumentModel.employee_id == employee_id
            )
        else:
            count_stmt = select(func.count()).select_from(DocumentModel)
            docs_stmt = select(DocumentModel)
        
        # Get total count
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # Get paginated documents
        offset = (page - 1) * page_size
        docs_result = await session.execute(docs_stmt.offset(offset).limit(page_size))
        documents = docs_result.scalars().all()
        
        return {
            "documents": [
                {
                    "id": doc.id,
                    "employee_id": doc.employee_id,
                    "document_type": doc.document_type.value,
                    "original_filename": doc.original_filename,
                    "verification_status": doc.verification_status.value,
                    "uploaded_at": doc.uploaded_at,
                    "verified_at": doc.verified_at
                } for doc in documents
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def upload_document(
        self,
        session: AsyncSession,
        file: UploadFile,
        document_type: str,
        employee_id: str,
        task_id: str = None
    ) -> DocumentModel:
        """Upload and save a document"""
        # Validate document type
        try:
            doc_type = DocumentType(document_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document type"
            )
        
        # Create file path
        filename = f"{employee_id}_{doc_type.value}_{file.filename}"
        file_path = self.upload_dir / filename
        
        # Save file asynchronously
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}"
            )
        
        # Save document metadata
        document = DocumentModel(
            employee_id=employee_id,
            document_type=doc_type,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file.size,
            mime_type=file.content_type,
            task_id=task_id
        )
        
        session.add(document)
        await session.commit()
        await session.refresh(document)
        
        # Process with AI asynchronously
        try:
            document = await self.ai_service.process_document(document, session)
        except Exception as e:
            print(f"AI processing failed for document {document.id}: {e}")
        
        return document
    
    async def verify_document(
        self,
        session: AsyncSession,
        document_id: str,
        verification_status: VerificationStatus
    ) -> DocumentModel:
        """Update document verification status"""
        document = await session.get(DocumentModel, document_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document.verification_status = verification_status
        if verification_status in [VerificationStatus.APPROVED, VerificationStatus.REJECTED]:
            from datetime import datetime
            document.verified_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(document)
        
        return document
