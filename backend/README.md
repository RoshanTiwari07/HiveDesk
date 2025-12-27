# HR Onboarding System - Backend API

A complete **FastAPI backend** for HR Onboarding System with PostgreSQL, JWT authentication, and comprehensive REST API endpoints.

## ✅ Setup Verified & Working (Dec 27, 2025)

**Status**: All systems operational  
- ✅ CORS middleware configured
- ✅ Async database operations fixed
- ✅ Docker containers running
- ✅ PostgreSQL database healthy
- ✅ API endpoints tested and functional

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running

### One-Command Setup
```bash
cd backend
docker-compose up --build
```

**That's it!** The API will be running at:
- **API Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Database**: PostgreSQL on port 5434

### Test Credentials (Already Created)
```
HR User:
  Email: john.hr@company.com
  Password: password123

Employee Users:
  Email: jane.employee@company.com
  Password: password123
  
  Email: bob.employee@company.com
  Password: password123
  
  Email: alice.employee@company.com
  Password: password123
```

### Create Additional Test Users (Optional)
```bash
docker exec hr_backend python simple_sample_data.py
```

## 📋 Frontend Integration Guide

### Base Configuration
```javascript
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINTS = {
  // Authentication
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  
  // Dashboard
  DASHBOARD: (name, role) => `/${name}/${role}/dashboard`,
  
  // Employee Management (HR only)
  EMPLOYEES: (name, role) => `/${name}/${role}/employees`,
  MANAGE_EMPLOYEE: (name, role, employeeName) => `/${name}/${role}/manage/${employeeName}`,
  ASSIGN_TASK: (name, role) => `/${name}/${role}/assign-task`,
  
  // Tasks
  TASKS: (name, role) => `/${name}/${role}/tasks`,
  COMPLETE_TASK: (name, role) => `/${name}/${role}/tasks/complete`,
  
  // Documents
  DOCUMENTS: (name, role) => `/${name}/${role}/documents`,
  UPLOAD_DOCUMENT: (name, role) => `/${name}/${role}/documents/upload`,
  
  // Training
  TRAINING: (name, role) => `/${name}/${role}/training`
};
```

### Authentication Flow

#### 1. Login
```javascript
const login = async (email, password) => {
  const formData = new FormData();
  formData.append('email', email);
  formData.append('password', password);
  
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Store token and user info
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  } else {
    throw new Error(data.detail);
  }
};
```

#### 2. Authenticated Requests
```javascript
const makeAuthenticatedRequest = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  
  if (response.status === 401) {
    // Token expired, redirect to login
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    return;
  }
  
  return response.json();
};
```

### API Endpoints Reference

#### Authentication
```javascript
// Login
POST /auth/login
Content-Type: application/x-www-form-urlencoded
Body: email=user@example.com&password=password123

Response: {
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "hr", // or "employee"
    "is_active": true,
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  }
}

// Register (HR only)
POST /auth/register
Authorization: Bearer {token}
Content-Type: application/json
Body: {
  "name": "New Employee",
  "email": "employee@example.com",
  "role": "employee",
  "password": "password123",
  "is_active": true
}
```

#### Dashboard
```javascript
// Get Dashboard Data
GET /{name}/{role}/dashboard
Authorization: Bearer {token}

// HR Response:
{
  "role": "hr",
  "total_employees": 10,
  "pending_tasks": 5,
  "pending_documents": 3,
  "recent_activities": []
}

// Employee Response:
{
  "role": "employee",
  "total_tasks": 8,
  "completed_tasks": 5,
  "pending_tasks": 3,
  "completion_rate": 62.5
}
```

#### Employee Management (HR Only)
```javascript
// Get All Employees
GET /{name}/{role}/employees
Authorization: Bearer {token}

Response: {
  "employees": [
    {
      "id": "uuid",
      "name": "Jane Employee",
      "email": "jane@example.com",
      "is_active": true,
      "total_tasks": 5,
      "completed_tasks": 3,
      "completion_rate": 60.0
    }
  ]
}

// Manage Specific Employee
GET /{name}/{role}/manage/{employee_name}
Authorization: Bearer {token}

Response: {
  "employee": {
    "id": "uuid",
    "name": "Jane Employee",
    "email": "jane@example.com",
    "is_active": true
  },
  "tasks": [...],
  "documents": [...]
}

// Assign Task to Employee
POST /{name}/{role}/assign-task
Authorization: Bearer {token}
Content-Type: application/x-www-form-urlencoded
Body: employee_id=uuid&task_id=uuid
```

#### Tasks
```javascript
// Get Tasks
GET /{name}/{role}/tasks
Authorization: Bearer {token}

// HR sees all tasks, Employee sees assigned tasks
Response: {
  "tasks": [
    {
      "id": "uuid",
      "title": "Read Company Policy",
      "description": "Please read...",
      "task_type": "read", // "read", "upload", "sign"
      "status": "pending", // "pending", "completed"
      "assigned_at": "2025-01-01T00:00:00",
      "completed_at": null
    }
  ]
}

// Complete Task
POST /{name}/{role}/tasks/complete
Authorization: Bearer {token}
Content-Type: application/x-www-form-urlencoded
Body: assignment_id=uuid
```

#### Documents
```javascript
// Get Documents
GET /{name}/{role}/documents
Authorization: Bearer {token}

Response: {
  "documents": [
    {
      "id": "uuid",
      "employee_id": "uuid",
      "document_type": "aadhar", // "aadhar", "resume"
      "original_filename": "document.pdf",
      "verification_status": "pending", // "pending", "verified", "failed"
      "uploaded_at": "2025-01-01T00:00:00",
      "verified_at": null
    }
  ]
}

// Upload Document
POST /{name}/{role}/documents/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data
Body: FormData with file, document_type, and optional task_id

Response: {
  "message": "Document uploaded successfully",
  "document_id": "uuid"
}
```

#### Training
```javascript
// Get Training Modules
GET /{name}/{role}/training
Authorization: Bearer {token}

// Employee Response (with progress):
{
  "training_modules": [
    {
      "id": "uuid",
      "title": "Workplace Safety",
      "description": "Essential safety guidelines",
      "duration_minutes": 30,
      "is_mandatory": true,
      "progress": {
        "status": "pending", // "pending", "completed"
        "progress_percentage": 0,
        "started_at": null,
        "completed_at": null
      }
    }
  ]
}
```

### Error Handling
```javascript
const handleApiError = (error, response) => {
  switch (response.status) {
    case 401:
      // Unauthorized - redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
      break;
    case 403:
      // Forbidden - show access denied message
      alert('Access denied');
      break;
    case 404:
      // Not found
      alert('Resource not found');
      break;
    case 422:
      // Validation error
      console.error('Validation errors:', error.detail);
      break;
    default:
      alert('An error occurred');
  }
};
```

### User Roles & Access Control

#### HR Role (`"hr"`)
- Can access all endpoints
- Can view all employees, tasks, and documents
- Can register new users
- Can assign tasks to employees
- Can manage employee data

#### Employee Role (`"employee"`)
- Can only access their own data
- Can view assigned tasks and complete them
- Can upload documents
- Can view training modules and track progress
- Cannot access other employees' data

### URL Pattern
All endpoints follow the pattern: `/{name}/{role}/endpoint`
- `name`: User's name (from JWT token)
- `role`: User's role ("hr" or "employee")

### Test Credentials

After running the sample data script:

```javascript
const TEST_USERS = {
  HR: {
    email: 'john.hr@company.com',
    password: 'password123',
    name: 'john',
    role: 'hr'
  },
  EMPLOYEES: [
    {
      email: 'jane.employee@company.com',
      password: 'password123',
      name: 'jane',
      role: 'employee'
    },
    {
      email: 'bob.employee@company.com',
      password: 'password123',
      name: 'bob',
      role: 'employee'
    },
    {
      email: 'alice.employee@company.com',
      password: 'password123',
      name: 'alice',
      role: 'employee'
    }
  ]
};
```

### React Example Components

#### Login Component
```jsx
import React, { useState } from 'react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('email', email);
      formData.append('password', password);
      
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        // Redirect based on role
        window.location.href = data.user.role === 'hr' ? '/hr-dashboard' : '/employee-dashboard';
      } else {
        alert(data.detail);
      }
    } catch (error) {
      alert('Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

#### Dashboard Component
```jsx
import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      const user = JSON.parse(localStorage.getItem('user'));
      const token = localStorage.getItem('token');
      
      try {
        const response = await fetch(
          `http://localhost:8000/${user.name}/${user.role}/dashboard`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        const data = await response.json();
        setDashboardData(data);
      } catch (error) {
        console.error('Failed to fetch dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      {dashboardData?.role === 'hr' ? (
        <div>
          <p>Total Employees: {dashboardData.total_employees}</p>
          <p>Pending Tasks: {dashboardData.pending_tasks}</p>
          <p>Pending Documents: {dashboardData.pending_documents}</p>
        </div>
      ) : (
        <div>
          <p>Total Tasks: {dashboardData.total_tasks}</p>
          <p>Completed: {dashboardData.completed_tasks}</p>
          <p>Pending: {dashboardData.pending_tasks}</p>
          <p>Completion Rate: {dashboardData.completion_rate}%</p>
        </div>
      )}
    </div>
  );
};
```

## 🛠️ Development

### Project Structure
```
backend/
├── app/
│   ├── models/          # Database models
│   ├── schemas/         # API request/response schemas
│   ├── core/           # Enums and utilities
│   ├── main.py         # FastAPI application
│   ├── database.py     # Database configuration
│   └── auth.py         # Authentication utilities
├── uploads/            # File upload directory
├── docker-compose.yml  # Docker configuration
├── Dockerfile         # Application container
├── requirements.txt   # Python dependencies
├── simple_sample_data.py # Test data creation
└── README.md          # This file
```

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://postgres:roshan@postgres:5432/hr_onboarding_system
SECRET_KEY=your-super-secret-key-for-docker-deployment
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Stop the System
```bash
docker-compose down
```

## 🔧 CORS Configuration

If you need to enable CORS for frontend development, add this to `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📚 API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation with all endpoints, request/response schemas, and the ability to test API calls directly.

---

**Ready for Frontend Integration!** 🚀

The backend is fully operational and provides all necessary endpoints for a complete HR onboarding system. Use the examples above to integrate with your frontend framework of choice.