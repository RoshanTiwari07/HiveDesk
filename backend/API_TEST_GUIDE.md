# API Testing Guide - HR Onboarding System

## Authentication

### 1. Login (POST /auth/login) ✅
**Request:**
```json
{
  "email": "john.hr@company.com",
  "password": "password123"
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "name": "John HR",
    "email": "john.hr@company.com",
    "role": "hr",
    "is_active": true,
    "id": "uuid",
    "created_at": "2025-12-27T07:00:38.280471",
    "updated_at": "2025-12-27T07:00:38.280475"
  }
}
```

**Status**: ✅ Working correctly (JSON request/response)

---

### 2. Register User (POST /auth/register) ✅ FIXED
**Headers:**
```
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "name": "New Employee",
  "email": "new.employee@company.com",
  "password": "password123",
  "role": "employee",
  "is_active": true
}
```

**Expected Response (200):**
```json
{
  "name": "New Employee",
  "email": "new.employee@company.com",
  "role": "employee",
  "is_active": true,
  "id": "uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**Fixes Applied:**
- ✅ Added response schema (UserResponseSchema)
- ✅ Returns proper user object instead of plain dict
- ✅ JSON request/response

**Required Role**: HR

---

## HR Endpoints

### 3. HR Dashboard (GET /{name}/{role}/dashboard) ⚠️
**Headers:**
```
Authorization: Bearer {access_token}
```

**URL Example:** `/John%20HR/hr/dashboard`

**Expected Response:**
```json
{
  "role": "hr",
  "total_employees": 3,
  "pending_tasks": 0,
  "pending_documents": 0,
  "recent_activities": []
}
```

**Issues Found:**
- ⚠️ No response schema
- ⚠️ Non-standard URL structure
- ⚠️ Should use token for auth, not URL parameters

**Recommendation:** Create `/api/v1/dashboard` endpoint that uses token

---

### 4. Get All Employees (GET /{name}/{role}/employees) ⚠️
**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response:**
```json
{
  "employees": [
    {
      "id": "uuid",
      "name": "Jane Employee",
      "email": "jane.employee@company.com",
      "is_active": true,
      "total_tasks": 5,
      "completed_tasks": 3,
      "completion_rate": 60.0
    }
  ]
}
```

**Issues Found:**
- ⚠️ No response schema
- ⚠️ N+1 query problem (fetches tasks for each employee in loop)
- ⚠️ No pagination

**Required Role**: HR

---

### 5. Manage Employee (GET /{name}/{role}/manage/{employee_id}) ✅ FIXED
**Headers:**
```
Authorization: Bearer {access_token}
```

**URL Example:** `/John%20HR/hr/manage/{employee_uuid}`

**Expected Response:**
```json
{
  "employee": {
    "id": "uuid",
    "name": "Jane Employee",
    "email": "jane.employee@company.com",
    "is_active": true
  },
  "tasks": [...],
  "documents": [...]
}
```

**Fixes Applied:**
- ✅ Changed from employee_name to employee_id
- ✅ Fixed SQL injection vulnerability (removed ilike search)
- ✅ Now uses secure UUID lookup

**Required Role**: HR

---

### 6. Assign Task (POST /{name}/{role}/assign-task) ✅ FIXED
**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request (BEFORE - Form):**
```
employee_id=uuid&task_id=uuid
```

**Request (NOW - JSON):**
```json
{
  "employee_id": "employee-uuid",
  "task_id": "task-uuid"
}
```

**Expected Response (200):**
```json
{
  "message": "Task assigned successfully"
}
```

**Fixes Applied:**
- ✅ Changed from Form data to JSON
- ✅ Added request schema (AssignTaskRequest)
- ✅ Consistent with other endpoints

**Required Role**: HR

---

## Employee Endpoints

### 7. Get Tasks (GET /{name}/{role}/tasks) ⚠️
**Headers:**
```
Authorization: Bearer {access_token}
```

**Employee Response:**
```json
{
  "tasks": [
    {
      "assignment_id": "uuid",
      "task_id": "uuid",
      "title": "Read Company Handbook",
      "description": "...",
      "task_type": "read",
      "content": "...",
      "status": "pending",
      "assigned_at": "timestamp",
      "completed_at": null
    }
  ]
}
```

**Issues Found:**
- ⚠️ No response schema
- ⚠️ N+1 query problem (fetches each task individually)
- ⚠️ No pagination

---

### 8. Complete Task (POST /{name}/{role}/tasks/complete) ✅ FIXED
**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request (BEFORE - Form):**
```
assignment_id=uuid
```

**Request (NOW - JSON):**
```json
{
  "assignment_id": "uuid"
}
```

**Expected Response (200):**
```json
{
  "message": "Task marked as completed"
}
```

**Fixes Applied:**
- ✅ Changed from Form data to JSON
- ✅ Added request schema (CompleteTaskRequest)

---

### 9. Get Documents (GET /{name}/{role}/documents) ⚠️
**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response:**
```json
{
  "documents": [
    {
      "id": "uuid",
      "employee_id": "uuid",
      "document_type": "aadhar",
      "original_filename": "aadhar.pdf",
      "verification_status": "pending",
      "uploaded_at": "timestamp",
      "verified_at": null
    }
  ]
}
```

**Issues Found:**
- ⚠️ No response schema
- ⚠️ No pagination
- ⚠️ No filtering options

---

### 10. Upload Document (POST /{name}/{role}/documents/upload) ✅
**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request (Form-Data):**
```
file: [binary]
document_type: aadhar
task_id: uuid (optional)
```

**Expected Response (200):**
```json
{
  "message": "Document uploaded successfully",
  "document_id": "uuid"
}
```

**Status**: ✅ Correct (multipart is appropriate for file uploads)

**Potential Issues:**
- ⚠️ No file size validation
- ⚠️ No file type validation
- ⚠️ Potential path traversal vulnerability

---

### 11. Get Training Modules (GET /{name}/{role}/training) ⚠️
**Headers:**
```
Authorization: Bearer {access_token}
```

**Employee Response:**
```json
{
  "training_modules": [
    {
      "id": "uuid",
      "title": "Security Training",
      "description": "...",
      "duration_minutes": 30,
      "is_mandatory": true,
      "progress": {
        "status": "pending",
        "progress_percentage": 0,
        "started_at": null,
        "completed_at": null
      }
    }
  ]
}
```

**Issues Found:**
- ⚠️ No response schema
- ⚠️ N+1 query problem
- ✅ Boolean comparison fixed

---

## Summary of Fixes Applied

### ✅ Fixed Issues (5)
1. Login endpoint - Changed from Form to JSON ✅
2. Register endpoint - Added response schema ✅
3. Manage employee - Fixed SQL injection ✅
4. Assign task - Changed from Form to JSON ✅
5. Complete task - Changed from Form to JSON ✅

### ⚠️ Remaining Issues (8)
1. No response schemas for dashboard endpoints
2. Non-standard URL structure (name/role in path)
3. N+1 query problems in multiple endpoints
4. No pagination anywhere
5. No input validation on file uploads
6. No rate limiting
7. No request/response logging
8. Missing error handling in some places

### 📊 Endpoint Health Status
- ✅ Fully Working: 3/11 (27%)
- ⚠️ Working with Issues: 8/11 (73%)
- ❌ Broken: 0/11 (0%)

---

## Test Credentials

### HR User
```
Email: john.hr@company.com
Password: password123
```

### Employees
```
jane.employee@company.com / password123
bob.employee@company.com / password123
alice.employee@company.com / password123
```
