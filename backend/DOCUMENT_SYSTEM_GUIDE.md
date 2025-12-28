# 📋 Document Management System - Frontend Integration Guide

## Overview
Complete document upload, verification, and profile display system with **automatic data masking** for sensitive information like Aadhaar and PAN cards.

---

## 🎯 Features Implemented

### ✅ Document Types Supported
1. **Aadhaar Card** - Shows only last 4 digits (XXXX XXXX X123)
2. **PAN Card** - Shows only last 4 characters (XXXXX234F)
3. **Resume** - Full details displayed
4. **Offer Letter** - Full details displayed
5. **PF Form** - UAN and PF numbers displayed
6. **Photo** - Image validation only

### ✅ Privacy & Security
- **Automatic Masking**: Aadhaar and PAN numbers are automatically masked
- **HR View Only**: Only shows last 4 digits to HR for verification
- **AI Extraction**: Extracts all fields from documents using AI
- **Validation**: Each document is validated and scored by AI
- **Confidence Scoring**: AI provides confidence level for each document

---

## 📡 API Endpoints

### 1. Upload Document
**Endpoint:** `POST /api/documents/upload`  
**Auth:** Required (Bearer token)  
**Content-Type:** `multipart/form-data`

**Request Parameters:**
```javascript
{
  file: File,                    // The document file (PDF, JPG, PNG)
  document_type: string,         // "aadhaar", "pan", "resume", "offer_letter", "pf_form", "photo"
  task_id: string (optional)     // Link to specific task if needed
}
```

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document_id": "30947b63-15df-4f0b-a5a3-3a1ff2f74354"
}
```

**Example (React/Axios):**
```javascript
const uploadDocument = async (file, documentType) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);
  
  const response = await axios.post(
    'http://localhost:8000/api/documents/upload',
    formData,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    }
  );
  
  return response.data;
};
```

---

### 2. Get Employee Profile with All Documents (✨ NEW)
**Endpoint:** `GET /api/employees/{employee_id}/profile`  
**Auth:** HR only  
**Purpose:** Get complete employee profile with ALL documents and masked sensitive data

**Response:**
```json
{
  "employee": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@company.com",
    "role": "employee",
    "onboarding_status": "IN_PROGRESS",
    "is_active": true,
    "created_at": "2025-12-28T..."
  },
  "documents": [
    {
      "document_id": "uuid",
      "document_type": "aadhaar",
      "original_filename": "aadhaar_scan.pdf",
      "uploaded_at": "2025-12-28T...",
      "verification_status": "pending",  // "pending", "verified", "rejected"
      "verification_notes": "AI: Ready for HR review",
      "verified_at": null,
      "ai_confidence_score": 0.95,
      "extracted_fields": {
        "name": "John Doe",
        "aadhaar_number": "XXXX XXXX X234",  // ⚠️ MASKED
        "dob": "01/01/1990",
        "gender": "Male",
        "address": "123 Main St..."
      },
      "issues": [],
      "missing_fields": []
    },
    {
      "document_id": "uuid",
      "document_type": "pan",
      "original_filename": "pan_card.jpg",
      "uploaded_at": "2025-12-28T...",
      "verification_status": "pending",
      "verification_notes": "AI: Ready for HR review",
      "verified_at": null,
      "ai_confidence_score": 0.92,
      "extracted_fields": {
        "name": "JOHN DOE",
        "pan_number": "XXXXX789F",  // ⚠️ MASKED
        "dob": "01/01/1990",
        "father_name": "Father Name"
      },
      "issues": [],
      "missing_fields": []
    },
    {
      "document_id": "uuid",
      "document_type": "resume",
      "original_filename": "resume.pdf",
      "uploaded_at": "2025-12-28T...",
      "verification_status": "verified",
      "verification_notes": "AI: Ready for HR review",
      "verified_at": "2025-12-28T...",
      "ai_confidence_score": 0.88,
      "extracted_fields": {
        "name": "John Doe",
        "email": "jo****@gmail.com",  // Partially masked
        "phone": "XXXXX X1234",      // Partially masked
        "skills": ["Python", "React", "Docker"],
        "experience_years": 5,
        "education": "B.Tech Computer Science",
        "current_company": "Tech Corp"
      },
      "issues": [],
      "missing_fields": []
    }
  ],
  "documents_by_type": {
    "aadhaar": [/* Aadhaar document object */],
    "pan": [/* PAN document object */],
    "resume": [/* Resume document object */]
  },
  "document_summary": {
    "total_documents": 3,
    "verified": 1,
    "pending": 2,
    "rejected": 0,
    "types_uploaded": ["aadhaar", "pan", "resume"]
  }
}
```

**Example Usage:**
```javascript
const getEmployeeProfile = async (employeeId) => {
  const response = await axios.get(
    `http://localhost:8000/api/employees/${employeeId}/profile`,
    {
      headers: {
        'Authorization': `Bearer ${hrToken}`
      }
    }
  );
  
  return response.data;
};
```

---

### 3. Verify Document (HR Only)
**Endpoint:** `PUT /api/documents/{document_id}/verify`  
**Auth:** HR only

**Request:**
```json
{
  "verification_status": "verified",  // or "rejected"
  "verification_notes": "Document verified successfully"
}
```

**Response:**
```json
{
  "message": "Document verification updated"
}
```

---

## 🎨 Frontend Implementation Guide

### React Component Example: Employee Document Dropzone

```jsx
import React, { useState } from 'react';
import { Upload, File, Check, AlertCircle } from 'lucide-react';

const DocumentUploadDropzone = ({ employeeId }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState([]);

  const documentTypes = [
    { value: 'aadhaar', label: 'Aadhaar Card', required: true },
    { value: 'pan', label: 'PAN Card', required: true },
    { value: 'resume', label: 'Resume', required: true },
    { value: 'offer_letter', label: 'Offer Letter', required: true },
    { value: 'pf_form', label: 'PF Form', required: false },
    { value: 'photo', label: 'Photo', required: true }
  ];

  const handleFileUpload = async (file, docType) => {
    setUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', docType);

    try {
      const response = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      const data = await response.json();
      
      setUploadedDocs(prev => [...prev, {
        type: docType,
        filename: file.name,
        id: data.document_id
      }]);
      
      alert('Document uploaded successfully!');
    } catch (error) {
      alert('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Upload Required Documents</h3>
      
      {documentTypes.map(docType => (
        <div key={docType.value} className="border rounded-lg p-4">
          <div className="flex justify-between items-center">
            <div>
              <h4 className="font-medium">{docType.label}</h4>
              {docType.required && (
                <span className="text-xs text-red-500">* Required</span>
              )}
            </div>
            
            {uploadedDocs.find(d => d.type === docType.value) ? (
              <div className="flex items-center text-green-600">
                <Check size={20} />
                <span className="ml-2">Uploaded</span>
              </div>
            ) : (
              <label className="cursor-pointer bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e.target.files[0], docType.value)}
                  disabled={uploading}
                />
                {uploading ? 'Uploading...' : 'Choose File'}
              </label>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentUploadDropzone;
```

---

### React Component Example: HR Document Verification View

```jsx
import React, { useState, useEffect } from 'react';
import { Eye, Check, X, AlertTriangle } from 'lucide-react';

const EmployeeDocumentProfile = ({ employeeId }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmployeeProfile();
  }, [employeeId]);

  const fetchEmployeeProfile = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/employees/${employeeId}/profile`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      const data = await response.json();
      setProfile(data);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const verifyDocument = async (documentId, status, notes) => {
    try {
      await fetch(`http://localhost:8000/api/documents/${documentId}/verify`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          verification_status: status,
          verification_notes: notes
        })
      });
      
      // Refresh profile
      fetchEmployeeProfile();
      alert('Document verification updated!');
    } catch (error) {
      alert('Verification failed: ' + error.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!profile) return <div>Profile not found</div>;

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Employee Info */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-2xl font-bold mb-4">{profile.employee.name}</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>Email: {profile.employee.email}</div>
          <div>Status: {profile.employee.onboarding_status}</div>
        </div>
      </div>

      {/* Document Summary */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <h3 className="font-semibold mb-2">Document Summary</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>Total: {profile.document_summary.total_documents}</div>
          <div className="text-green-600">Verified: {profile.document_summary.verified}</div>
          <div className="text-yellow-600">Pending: {profile.document_summary.pending}</div>
          <div className="text-red-600">Rejected: {profile.document_summary.rejected}</div>
        </div>
      </div>

      {/* Documents List */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Documents</h3>
        
        {profile.documents.map(doc => (
          <div key={doc.document_id} className="bg-white rounded-lg shadow p-6">
            {/* Document Header */}
            <div className="flex justify-between items-start mb-4">
              <div>
                <h4 className="font-semibold text-lg capitalize">
                  {doc.document_type.replace('_', ' ')}
                </h4>
                <p className="text-sm text-gray-500">{doc.original_filename}</p>
                <p className="text-xs text-gray-400">
                  Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                {doc.verification_status === 'verified' && (
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                    ✓ Verified
                  </span>
                )}
                {doc.verification_status === 'pending' && (
                  <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                    ⏳ Pending
                  </span>
                )}
                {doc.verification_status === 'rejected' && (
                  <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">
                    ✗ Rejected
                  </span>
                )}
              </div>
            </div>

            {/* AI Confidence */}
            {doc.ai_confidence_score && (
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span>AI Confidence</span>
                  <span>{(doc.ai_confidence_score * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      doc.ai_confidence_score > 0.8 ? 'bg-green-500' : 
                      doc.ai_confidence_score > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${doc.ai_confidence_score * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* Extracted Fields */}
            <div className="bg-gray-50 rounded p-4 mb-4">
              <h5 className="font-medium mb-2">Extracted Information</h5>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {Object.entries(doc.extracted_fields).map(([key, value]) => {
                  // Skip internal fields
                  if (['confidence', 'issues', 'missing_fields', 'extracted_data'].includes(key)) {
                    return null;
                  }
                  
                  return (
                    <div key={key}>
                      <span className="text-gray-600 capitalize">
                        {key.replace('_', ' ')}:
                      </span>
                      <span className="ml-2 font-medium">
                        {Array.isArray(value) ? value.join(', ') : value || 'N/A'}
                      </span>
                      
                      {/* Highlight masked fields */}
                      {(key.includes('aadhaar') || key.includes('pan')) && 
                       value && value.includes('XXX') && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                          🔒 Masked
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Issues & Missing Fields */}
            {doc.issues.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
                <div className="flex items-center text-red-800 mb-1">
                  <AlertTriangle size={16} className="mr-2" />
                  <span className="font-medium">Issues Found</span>
                </div>
                <ul className="text-sm text-red-700 list-disc list-inside">
                  {doc.issues.map((issue, idx) => <li key={idx}>{issue}</li>)}
                </ul>
              </div>
            )}

            {doc.missing_fields.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
                <div className="flex items-center text-yellow-800 mb-1">
                  <AlertTriangle size={16} className="mr-2" />
                  <span className="font-medium">Missing Fields</span>
                </div>
                <ul className="text-sm text-yellow-700 list-disc list-inside">
                  {doc.missing_fields.map((field, idx) => <li key={idx}>{field}</li>)}
                </ul>
              </div>
            )}

            {/* Verification Actions */}
            {doc.verification_status === 'pending' && (
              <div className="flex space-x-3">
                <button
                  onClick={() => verifyDocument(doc.document_id, 'verified', 'Verified by HR')}
                  className="flex-1 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                >
                  <Check size={16} className="inline mr-2" />
                  Verify
                </button>
                <button
                  onClick={() => {
                    const reason = prompt('Rejection reason:');
                    if (reason) verifyDocument(doc.document_id, 'rejected', reason);
                  }}
                  className="flex-1 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                >
                  <X size={16} className="inline mr-2" />
                  Reject
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmployeeDocumentProfile;
```

---

## 🔒 Data Privacy & Masking

### How Masking Works

1. **Document Upload**: Employee uploads Aadhaar/PAN
2. **AI Extraction**: AI extracts full number from document
3. **Automatic Masking**: Backend automatically masks sensitive data
4. **HR View**: HR sees only masked version (XXXX XXXX X234)
5. **Database Storage**: Full data stored securely, masked data sent to frontend

### Masked Fields

| Document Type | Masked Fields | Display Format |
|---------------|---------------|----------------|
| Aadhaar | aadhaar_number | XXXX XXXX X234 |
| PAN | pan_number | XXXXX234F |
| Resume | email | jo****@gmail.com |
| Resume | phone | XXXXX X1234 |
| All | Other PII | As extracted |

---

## 📊 Document Status Flow

```
┌─────────────┐
│   Upload    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ AI Process  │ ← Extracts fields
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Pending   │ ← Awaiting HR review
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ HR Reviews  │ ← Sees masked data
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐
  │Verified │   │Rejected │   │ Pending │
  └─────────┘   └─────────┘   └─────────┘
```

---

## 🧪 Testing

### Test the System

```bash
# 1. Login as HR
POST /api/auth/login
{
  "email": "john.hr@company.com",
  "password": "password123"
}

# 2. Get employee list
GET /api/employees/

# 3. Get employee profile with all documents
GET /api/employees/{employee_id}/profile

# 4. Upload document (as employee)
POST /api/documents/upload
FormData: file, document_type="aadhaar"

# 5. Verify document (as HR)
PUT /api/documents/{document_id}/verify
{
  "verification_status": "verified",
  "verification_notes": "Aadhaar verified"
}
```

---

## 🎯 Summary

✅ **Implemented Features**:
- 6 document types (Aadhaar, PAN, Resume, Offer Letter, PF, Photo)
- Automatic AI extraction of all fields
- Privacy-preserving masking (Aadhaar/PAN show last 4 only)
- Employee profile endpoint with all documents
- Document verification workflow
- Confidence scoring for each document
- Issue detection and missing field alerts

✅ **Security**:
- Sensitive data never exposed to frontend
- Automatic masking before sending to HR
- Full data stored securely in database
- Only authorized HR can view profiles

✅ **Ready for Frontend**:
- Clear API endpoints documented
- Example React components provided
- Complete data structures defined
- Validation schemas in place

---

🚀 **Your frontend team can now build the dropzone UI and profile display!**
