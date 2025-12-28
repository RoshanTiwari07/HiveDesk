import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ AUTH APIs ============
export const login = async (email, password) => {
  const response = await api.post('/api/auth/login', { email, password });
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
};

// ============ EMPLOYEE APIs ============
export const getEmployees = async () => {
  const response = await api.get('/api/employees/');
  return response.data;
};

export const getEmployeeProfile = async (employeeId) => {
  const response = await api.get(`/api/employees/${employeeId}/profile`);
  return response.data;
};

export const createEmployee = async (employeeData) => {
  const response = await api.post('/api/employees/', employeeData);
  return response.data;
};

export const updateEmployee = async (employeeId, employeeData) => {
  const response = await api.put(`/api/employees/${employeeId}`, employeeData);
  return response.data;
};

// ============ DOCUMENT APIs ============
export const uploadDocument = async (file, employeeId, documentType) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('employee_id', employeeId);
  formData.append('document_type', documentType);

  const response = await api.post('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async (employeeId) => {
  const response = await api.get(`/api/documents/?employee_id=${employeeId}`);
  return response.data;
};

export const verifyDocument = async (documentId, status, notes) => {
  const response = await api.put(`/api/documents/${documentId}/verify`, {
    status,
    verification_notes: notes,
  });
  return response.data;
};

// ============ TASK APIs ============
export const getTasks = async (employeeId) => {
  const response = await api.get(`/api/tasks/?employee_id=${employeeId}`);
  return response.data;
};

export const createTask = async (taskData) => {
  const response = await api.post('/api/tasks/', taskData);
  return response.data;
};

export const updateTask = async (taskId, taskData) => {
  const response = await api.put(`/api/tasks/${taskId}`, taskData);
  return response.data;
};

// ============ TRAINING APIs ============
export const getTrainings = async (employeeId) => {
  const response = await api.get(`/api/training/?employee_id=${employeeId}`);
  return response.data;
};

export const assignTraining = async (trainingData) => {
  const response = await api.post('/api/training/', trainingData);
  return response.data;
};

export const updateTrainingProgress = async (trainingId, progressData) => {
  const response = await api.put(`/api/training/${trainingId}/progress`, progressData);
  return response.data;
};

// ============ AI APIs ============
export const analyzeDocumentQuality = async (documentId) => {
  const response = await api.post(`/api/ai/analyze-document-quality/${documentId}`);
  return response.data;
};

export const generateOnboardingPlan = async (employeeId) => {
  const response = await api.post(`/api/ai/generate-onboarding-plan/${employeeId}`);
  return response.data;
};

export const getSmartTaskSuggestions = async (employeeId) => {
  const response = await api.get(`/api/ai/smart-task-suggestions/${employeeId}`);
  return response.data;
};

export const analyzePerformance = async (employeeId) => {
  const response = await api.post(`/api/ai/analyze-performance/${employeeId}`);
  return response.data;
};

// ============ DASHBOARD APIs ============
export const getDashboardStats = async () => {
  const response = await api.get('/api/dashboard/stats');
  return response.data;
};

export default api;
