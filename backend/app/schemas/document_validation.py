"""
Document Validation Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class DocumentFieldsSchema(BaseModel):
    """Base schema for document extracted fields"""
    confidence: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)


class AadhaarFieldsSchema(DocumentFieldsSchema):
    """Aadhaar card extracted fields"""
    is_valid_aadhaar: bool
    aadhaar_number: Optional[str] = Field(None, description="Masked Aadhaar (XXXX XXXX X123)")
    name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('aadhaar_number')
    def validate_aadhaar_masked(cls, v):
        """Ensure Aadhaar is properly masked"""
        if v and not v.startswith('XXXX'):
            # If full number received, mask it
            digits = re.sub(r'\D', '', v)
            if len(digits) == 12:
                return f"XXXX XXXX {digits[-4:]}"
        return v


class PANFieldsSchema(DocumentFieldsSchema):
    """PAN card extracted fields"""
    is_valid_pan: bool
    pan_number: Optional[str] = Field(None, description="Masked PAN (XXXXX234F)")
    name: Optional[str] = None
    father_name: Optional[str] = None
    dob: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('pan_number')
    def validate_pan_masked(cls, v):
        """Ensure PAN is properly masked"""
        if v and not v.startswith('XXXXX'):
            # Mask if full PAN received
            if len(v) == 10:
                return f"XXXXX{v[-4:]}"
        return v


class ResumeFieldsSchema(DocumentFieldsSchema):
    """Resume extracted fields"""
    is_valid_resume: bool
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    education: Optional[str] = None
    current_company: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)


class OfferLetterFieldsSchema(DocumentFieldsSchema):
    """Offer letter extracted fields"""
    is_valid_offer: bool
    candidate_name: Optional[str] = None
    position: Optional[str] = None
    salary: Optional[str] = None
    joining_date: Optional[str] = None
    department: Optional[str] = None
    reporting_to: Optional[str] = None
    company_name: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)


class PFFormFieldsSchema(DocumentFieldsSchema):
    """PF form extracted fields"""
    is_valid_pf: bool
    employee_name: Optional[str] = None
    uan_number: Optional[str] = None
    pf_number: Optional[str] = None
    previous_employer: Optional[str] = None
    date_of_joining: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)


class PhotoFieldsSchema(DocumentFieldsSchema):
    """Photo validation fields"""
    is_valid_photo: bool
    file_type: Optional[str] = None
    quality: Optional[str] = Field(None, description="good/acceptable/poor")
    extracted_data: Dict[str, Any] = Field(default_factory=dict)


class DocumentProfileResponse(BaseModel):
    """Complete employee document profile response"""
    document_id: str
    document_type: str
    original_filename: str
    uploaded_at: str
    verification_status: str
    verification_notes: Optional[str] = None
    verified_at: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    extracted_fields: Dict[str, Any]
    issues: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)


class EmployeeProfileResponse(BaseModel):
    """Complete employee profile with all documents"""
    employee: Dict[str, Any]
    documents: List[DocumentProfileResponse]
    documents_by_type: Dict[str, List[DocumentProfileResponse]]
    document_summary: Dict[str, Any]
