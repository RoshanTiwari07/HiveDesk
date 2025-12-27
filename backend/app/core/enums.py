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
    AADHAR = "aadhar"
    RESUME = "resume"
    OTHER = "other"


class VerificationStatus(str, Enum):
    """Document verification status enumeration"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"