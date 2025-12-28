"""
Core enums for the HR Onboarding System
"""
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    HR = "hr"
    EMPLOYEE = "employee"


class TaskType(str, Enum):
    """Task type enumeration"""
    READ = "read"
    UPLOAD = "upload"
    SIGN = "sign"


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"


class DocumentType(str, Enum):
    """Document type enumeration"""
    PAN = "pan"
    AADHAAR = "aadhaar"
    RESUME = "resume"
    OFFER_LETTER = "offer_letter"
    PF_FORM = "pf_form"
    PHOTO = "photo"
    OTHER = "other"


class VerificationStatus(str, Enum):
    """Document verification status enumeration"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    FAILED = "failed"


class OnboardingStatus(str, Enum):
    """Employee onboarding status enumeration"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class EnrollmentStatus(str, Enum):
    """Training enrollment status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"