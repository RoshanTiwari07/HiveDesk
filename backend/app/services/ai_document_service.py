"""
AI Document Analysis Service
"""
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import PyPDF2
from PIL import Image
import pytesseract
from datetime import datetime
import json

from .base_ai_service import BaseAIService
from ..models.document import DocumentModel
from ..core.enums import DocumentType
from ..utils.masking import DataMasker

class AIDocumentService(BaseAIService):
    """AI-powered document analysis"""
    
    async def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or Image"""
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        
        try:
            # PDF extraction
            if extension == '.pdf':
                return self._extract_from_pdf(file_path)
            
            # Image extraction (OCR)
            elif extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                return self._extract_from_image_tesseract(file_path)
            
            # Text file
            elif extension in ['.txt', '.text']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            else:
                return ""
                
        except Exception as e:
            print(f"Text extraction failed: {str(e)}")
            return ""
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"PDF extraction failed: {e}")
        return text.strip()
    
    def _extract_from_image_tesseract(self, file_path: str) -> str:
        """Extract text using Tesseract OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"OCR failed: {e}")
            return ""
    
    async def validate_document(
        self,
        text: str,
        doc_type: DocumentType
    ) -> Dict[str, Any]:
        """Validate document using Gemini AI"""
        
        # Build validation prompt based on document type
        prompt = self._build_validation_prompt(text, doc_type)
        
        system_instruction = """
        You are a document verification assistant for HR onboarding.
        Analyze documents and extract key information.
        Be strict but fair. Flag genuine issues only.
        """
        
        result = await self.call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            json_mode=True
        )
        
        return result
    
    def _build_validation_prompt(self, text: str, doc_type: DocumentType) -> str:
        """Build document-specific validation prompt"""
        
        if doc_type == DocumentType.PAN:
            return f"""
            Analyze this PAN card document and extract all fields:
            
            Extracted Text:
            {text[:2000]}
            
            Return JSON with these exact fields:
            {{
                "is_valid_pan": true/false,
                "pan_number": "10-character PAN like ABCDE1234F",
                "name": "Full name as on card",
                "father_name": "Father's name if visible",
                "dob": "Date of birth in DD/MM/YYYY format",
                "missing_fields": ["list any critical missing data"],
                "issues": ["any validation issues found"],
                "confidence": 0.0-1.0,
                "extracted_data": {{"any additional fields found"}}
            }}
            """
        
        elif doc_type == DocumentType.AADHAAR:
            return f"""
            Analyze this Aadhaar card document and extract all fields:
            
            Extracted Text:
            {text[:2000]}
            
            Return JSON with these exact fields:
            {{
                "is_valid_aadhaar": true/false,
                "aadhaar_number": "12-digit Aadhaar number",
                "name": "Full name as on card",
                "dob": "Date of birth in DD/MM/YYYY format",
                "gender": "Male/Female/Other",
                "address": "Full address from card",
                "missing_fields": ["list any critical missing data"],
                "issues": ["any validation issues found"],
                "confidence": 0.0-1.0,
                "extracted_data": {{"any additional fields found"}}
            }}
            
            IMPORTANT: Extract the full 12-digit Aadhaar number (will be masked later for security).
            """
        
        elif doc_type == DocumentType.RESUME:
            return f"""
            Analyze this resume and extract professional details:
            
            Extracted Text:
            {text[:3000]}
            
            Return JSON with these exact fields:
            {{
                "is_valid_resume": true/false,
                "name": "Candidate's full name",
                "email": "Email address",
                "phone": "Phone number",
                "skills": ["skill1", "skill2", "skill3"],
                "experience_years": number (total years of experience),
                "education": "Highest qualification",
                "current_company": "Current/last company name",
                "missing_fields": ["list any critical missing data"],
                "issues": ["any validation issues found"],
                "confidence": 0.0-1.0,
                "extracted_data": {{"certifications": [], "languages": []}}
            }}
            """
        
        elif doc_type == DocumentType.OFFER_LETTER:
            return f"""
            Analyze this offer letter and extract employment details:
            
            Extracted Text:
            {text[:3000]}
            
            Return JSON with these exact fields:
            {{
                "is_valid_offer": true/false,
                "candidate_name": "Candidate's name",
                "position": "Job title/position",
                "salary": "Annual CTC or monthly salary",
                "joining_date": "Date of joining in DD/MM/YYYY",
                "department": "Department name",
                "reporting_to": "Manager/reporting authority",
                "company_name": "Hiring company name",
                "missing_fields": ["list any critical missing data"],
                "issues": ["any validation issues found"],
                "confidence": 0.0-1.0,
                "extracted_data": {{"location": "", "employment_type": ""}}
            }}
            """
        
        elif doc_type == DocumentType.PF_FORM:
            return f"""
            Analyze this PF (Provident Fund) form and extract details:
            
            Extracted Text:
            {text[:2000]}
            
            Return JSON with these exact fields:
            {{
                "is_valid_pf": true/false,
                "employee_name": "Employee's full name",
                "uan_number": "Universal Account Number (UAN)",
                "pf_number": "PF account number",
                "previous_employer": "Previous company name if any",
                "date_of_joining": "DOJ with previous employer",
                "missing_fields": ["list any critical missing data"],
                "issues": ["any validation issues found"],
                "confidence": 0.0-1.0,
                "extracted_data": {{"nominee_name": "", "relationship": ""}}
            }}
            """
        
        elif doc_type == DocumentType.PHOTO:
            return f"""
            Validate this employee photo:
            
            Metadata/Info:
            {text[:500] if text else "Image file"}
            
            Return JSON with these exact fields:
            {{
                "is_valid_photo": true/false,
                "file_type": "jpg/png/etc",
                "quality": "good/acceptable/poor",
                "issues": ["any issues like blurry, inappropriate, etc"],
                "confidence": 0.0-1.0,
                "extracted_data": {{"dimensions": "", "size_kb": 0}}
            }}
            """
        
        else:  # OTHER
            return f"""
            Analyze this document:
            
            Extracted Text:
            {text[:2000]}
            
            Return JSON:
            {{
                "is_valid_document": true/false,
                "document_type_detected": "type if identifiable",
                "extracted_data": {{}},
                "missing_fields": [],
                "issues": [],
                "confidence": 0.0-1.0
            }}
            """
    
    async def process_document(
        self,
        document: DocumentModel,
        session: AsyncSession
    ) -> DocumentModel:
        """Full AI processing pipeline for a document"""
        
        try:
            # Step 1: Extract text
            text = await self.extract_text(document.file_path)
            document.extracted_text = text[:5000] if text else ""  # Limit storage
            
            if not text or len(text) < 10:
                document.verification_notes = "AI: No readable text found in document"
                document.ai_confidence_score = 0.0
                document.ai_processed_at = datetime.utcnow()
                session.add(document)
                await session.commit()
                await session.refresh(document)
                return document
            
            # Step 2: Validate with AI
            validation = await self.validate_document(text, document.document_type)
            
            # Step 3: Apply data masking for sensitive fields
            masked_validation = DataMasker.mask_document_data(
                validation, 
                document.document_type.value
            )
            
            # Store masked version for HR viewing
            document.ai_validation_result = json.dumps(masked_validation)
            document.ai_confidence_score = float(validation.get('confidence', 0.0))
            document.ai_processed_at = datetime.utcnow()
            
            # Step 4: Auto-update verification status based on AI result
            if validation.get('confidence', 0) > 0.8 and not validation.get('issues', []):
                document.verification_notes = "AI: Ready for HR review (high confidence)"
            else:
                issues = validation.get('issues', [])
                if issues:
                    document.verification_notes = f"AI: Needs review - {', '.join(issues[:3])}"
                else:
                    document.verification_notes = "AI: Processed successfully"
            
            # Save to database
            session.add(document)
            await session.commit()
            await session.refresh(document)
            
            return document
            
        except Exception as e:
            # If AI fails, don't block upload - just log it
            print(f"AI processing error: {str(e)}")
            document.verification_notes = f"AI processing failed: {str(e)[:100]}"
            document.ai_processed_at = datetime.utcnow()
            session.add(document)
            await session.commit()
            return document
    
    def get_masked_document_data(self, document: DocumentModel) -> Dict[str, Any]:
        """Get document data with sensitive fields masked for HR viewing"""
        try:
            if not document.ai_validation_result:
                return {"status": "not_processed"}
            
            data = json.loads(document.ai_validation_result)
            
            # Get only the fields that should be displayed for this doc type
            display_fields = DataMasker.get_display_fields(document.document_type.value)
            
            # Filter to only include allowed fields
            filtered_data = {
                k: v for k, v in data.items() 
                if k in display_fields or k in ['confidence', 'issues', 'missing_fields']
            }
            
            return filtered_data
            
        except Exception as e:
            return {"error": f"Failed to parse document data: {str(e)}"}
