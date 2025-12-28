// API Endpoints
export const API_ENDPOINTS = {
  // Employee Management
  EMPLOYEES: '/api/employees',
  EMPLOYEE_BY_ID: (id) => `/api/employees/${id}`,
  
  // Documents
  DOCUMENTS: '/api/documents',
  UPLOAD_DOCUMENT: '/api/documents/upload',
  VERIFY_DOCUMENT: (id) => `/api/documents/verify/${id}`,
  
  // Tasks
  TASKS: '/api/tasks',
  EMPLOYEE_TASKS: (id) => `/api/employees/${id}/tasks`,
  
  // Training
  TRAINING: '/api/training',
  EMPLOYEE_TRAINING: (id) => `/api/employees/${id}/training`,
  
  // Auth
  LOGIN: '/api/auth/login',
  LOGOUT: '/api/auth/logout',
  REFRESH_TOKEN: '/api/auth/refresh',
};

// User Roles
export const USER_ROLES = {
  HR: 'hr',
  EMPLOYEE: 'employee',
  ADMIN: 'admin',
  MANAGER: 'manager'
};

// Document Types (aligned with backend)
export const DOCUMENT_TYPES = {
  AADHAAR: 'aadhaar',
  PAN: 'pan',
  RESUME: 'resume',
  OFFER_LETTER: 'offer_letter',
  PF_FORM: 'pf_form',
  PHOTO: 'photo'
};

// Document Type Labels
export const DOCUMENT_TYPE_LABELS = {
  aadhaar: 'Aadhaar Card',
  pan: 'PAN Card',
  resume: 'Resume/CV',
  offer_letter: 'Offer Letter',
  pf_form: 'PF Form',
  photo: 'Employee Photo'
};

// Document Status
export const DOCUMENT_STATUS = {
  PENDING: 'pending',
  VERIFIED: 'verified',
  REJECTED: 'rejected'
};

// Task Status
export const TASK_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  OVERDUE: 'overdue'
};

// Training Categories
export const TRAINING_CATEGORIES = {
  REQUIRED: 'required',
  ROLE_SPECIFIC: 'role_specific',
  OPTIONAL: 'optional',
  TOOLS: 'tools'
};

// Mock Data for Development
export const MOCK_DATA = {
  EMPLOYEES: [
    { id: 1, name: 'John Doe', email: 'john@company.com', role: 'Developer', status: 'active' },
    { id: 2, name: 'Jane Smith', email: 'jane@company.com', role: 'Designer', status: 'onboarding' },
  ],
  TASKS: [
    { id: 1, title: 'Complete tax forms', completed: true },
    { id: 2, title: 'Setup work email', completed: false },
  ]
};