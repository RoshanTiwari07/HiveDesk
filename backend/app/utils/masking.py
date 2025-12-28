"""
Data Masking Utilities for Sensitive Documents
Implements privacy-preserving display of PII data
"""
import re
from typing import Optional, Dict, Any


class DataMasker:
    """Utility class for masking sensitive personal data"""
    
    @staticmethod
    def mask_aadhaar(aadhaar: Optional[str]) -> str:
        """
        Mask Aadhaar number - show only last 4 digits
        Input: "1234 5678 9012" or "123456789012"
        Output: "XXXX XXXX X012"
        """
        if not aadhaar:
            return "Not provided"
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', aadhaar)
        
        if len(digits) != 12:
            return "Invalid format"
        
        # Show only last 4 digits
        masked = f"XXXX XXXX {digits[-4:]}"
        return masked
    
    @staticmethod
    def mask_pan(pan: Optional[str]) -> str:
        """
        Mask PAN number - show only last 4 characters
        Input: "ABCDE1234F"
        Output: "XXXXX234F"
        """
        if not pan:
            return "Not provided"
        
        # Remove spaces and convert to uppercase
        pan = pan.replace(" ", "").upper()
        
        if len(pan) != 10:
            return "Invalid format"
        
        # Show only last 4 characters
        masked = f"XXXXX{pan[-4:]}"
        return masked
    
    @staticmethod
    def mask_email(email: Optional[str]) -> str:
        """
        Mask email - show first 2 chars and domain
        Input: "john.doe@company.com"
        Output: "jo****@company.com"
        """
        if not email or '@' not in email:
            return "Not provided"
        
        local, domain = email.split('@')
        
        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[:2] + '*' * (len(local) - 2)
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: Optional[str]) -> str:
        """
        Mask phone number - show last 4 digits
        Input: "+91 98765 43210"
        Output: "XXXXX X3210"
        """
        if not phone:
            return "Not provided"
        
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) < 4:
            return "Invalid format"
        
        masked = f"XXXXX X{digits[-4:]}"
        return masked
    
    @staticmethod
    def mask_document_data(doc_data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """
        Apply masking to extracted document data based on document type
        
        Args:
            doc_data: Extracted document fields
            doc_type: Type of document (aadhaar, pan, etc.)
        
        Returns:
            Dictionary with masked sensitive fields
        """
        masked_data = doc_data.copy()
        
        if doc_type == "aadhaar":
            if "aadhaar_number" in masked_data:
                masked_data["aadhaar_number_masked"] = DataMasker.mask_aadhaar(
                    masked_data["aadhaar_number"]
                )
                # Remove original unmasked number from display
                masked_data["aadhaar_number"] = masked_data["aadhaar_number_masked"]
        
        elif doc_type == "pan":
            if "pan_number" in masked_data:
                masked_data["pan_number_masked"] = DataMasker.mask_pan(
                    masked_data["pan_number"]
                )
                masked_data["pan_number"] = masked_data["pan_number_masked"]
        
        # Always mask phone and email if present
        if "phone" in masked_data:
            masked_data["phone"] = DataMasker.mask_phone(masked_data["phone"])
        
        if "email" in masked_data:
            masked_data["email"] = DataMasker.mask_email(masked_data["email"])
        
        return masked_data
    
    @staticmethod
    def get_display_fields(doc_type: str) -> list:
        """
        Get list of fields that should be displayed for each document type
        
        Returns:
            List of field names safe for HR viewing
        """
        field_mapping = {
            "aadhaar": [
                "name", "aadhaar_number_masked", "dob", "gender", "address"
            ],
            "pan": [
                "name", "pan_number_masked", "dob", "father_name"
            ],
            "resume": [
                "name", "email", "phone", "education", "experience_years", 
                "skills", "current_company"
            ],
            "offer_letter": [
                "candidate_name", "position", "salary", "joining_date", 
                "department", "reporting_to"
            ],
            "pf_form": [
                "employee_name", "uan_number", "pf_number", "previous_employer",
                "date_of_joining"
            ],
            "photo": [
                "file_type", "uploaded_at"
            ]
        }
        
        return field_mapping.get(doc_type, [])
