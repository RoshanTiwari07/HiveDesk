import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { uploadDocument, getEmployeeProfile } from '../services/api';
import { DOCUMENT_TYPES, DOCUMENT_TYPE_LABELS, DOCUMENT_STATUS } from '../utils/constants';
import Toast from '../components/common/Toast';
import Loader from '../components/common/Loader';

const DocumentVerificationPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedType, setSelectedType] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await getEmployeeProfile(user.id);
      setProfile(data);
    } catch (error) {
      showToast('Failed to load profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file, documentType) => {
    if (!file) return;

    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      showToast('File size must be less than 10MB', 'error');
      return;
    }

    try {
      setUploading(true);
      await uploadDocument(file, user.id, documentType);
      showToast(`${DOCUMENT_TYPE_LABELS[documentType]} uploaded successfully! AI is processing...`, 'success');
      await fetchProfile(); // Refresh profile
      setSelectedType(null);
    } catch (error) {
      showToast(error.response?.data?.detail || 'Upload failed', 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e, documentType) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0], documentType);
    }
  };

  const showToast = (message, type) => {
    setToast({ show: true, message, type });
  };

  const getProgressPercentage = () => {
    if (!profile?.document_summary) return 0;
    const { total_documents, verified } = profile.document_summary;
    const totalRequired = Object.keys(DOCUMENT_TYPES).length;
    return Math.round((verified / totalRequired) * 100);
  };

  const getDocumentByType = (type) => {
    return profile?.documents_by_type?.[type]?.[0] || null;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case DOCUMENT_STATUS.VERIFIED:
        return 'bg-green-100 text-green-800 border-green-300';
      case DOCUMENT_STATUS.REJECTED:
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case DOCUMENT_STATUS.VERIFIED:
        return '✓';
      case DOCUMENT_STATUS.REJECTED:
        return '⚠';
      default:
        return '⏳';
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">H</span>
            </div>
            <span className="font-bold text-xl">HR Portal</span>
          </div>
          <div className="flex items-center space-x-4">
            <button className="text-gray-600 hover:text-gray-900">🔍 Search</button>
            <div className="w-10 h-10 bg-gray-200 rounded-full overflow-hidden">
              <img src="/api/placeholder/40/40" alt="User" className="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="text-sm text-gray-600 mb-6">
          <span className="hover:text-gray-900 cursor-pointer">Home</span>
          <span className="mx-2">/</span>
          <span className="hover:text-gray-900 cursor-pointer">Onboarding</span>
          <span className="mx-2">/</span>
          <span className="text-gray-900 font-medium">Documents</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <h1 className="text-3xl font-bold mb-2">Upload Documents</h1>
            <p className="text-gray-600 mb-8">
              Please upload clear scans or photos of the required documents. Our AI verification
              system will check them instantly for validity.
            </p>

            {/* Document Upload Cards */}
            <div className="space-y-6">
              {Object.entries(DOCUMENT_TYPES).map(([key, type]) => {
                const doc = getDocumentByType(type);
                const isUploaded = !!doc;

                return (
                  <div key={type} className="bg-white rounded-lg shadow-sm border p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                          📄
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{DOCUMENT_TYPE_LABELS[type]}</h3>
                          <p className="text-sm text-gray-600">
                            {type === 'aadhaar' && 'Required for identity verification'}
                            {type === 'pan' && 'Required for payroll setup'}
                            {type === 'resume' && 'Required for HR records'}
                            {type === 'offer_letter' && 'Required for employment verification'}
                            {type === 'pf_form' && 'Required for PF account setup'}
                            {type === 'photo' && 'Required for ID card'}
                          </p>
                        </div>
                      </div>

                      {isUploaded && (
                        <div className={`px-4 py-2 rounded-full text-sm font-medium border ${getStatusColor(doc.verification_status)}`}>
                          {getStatusIcon(doc.verification_status)} {doc.verification_status.toUpperCase()}
                        </div>
                      )}
                    </div>

                    {!isUploaded ? (
                      <div
                        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                          dragActive && selectedType === type
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-300 bg-gray-50'
                        }`}
                        onDragEnter={(e) => { handleDrag(e); setSelectedType(type); }}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={(e) => handleDrop(e, type)}
                      >
                        <div className="text-4xl mb-3">☁️</div>
                        <p className="text-gray-700 mb-2">Click to upload or drag and drop</p>
                        <p className="text-sm text-gray-500 mb-4">PDF, PNG, JPG (max 10MB)</p>
                        <label className="inline-block">
                          <input
                            type="file"
                            className="hidden"
                            accept=".pdf,.png,.jpg,.jpeg"
                            onChange={(e) => handleFileUpload(e.target.files[0], type)}
                            disabled={uploading}
                          />
                          <span className="px-6 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors">
                            {uploading ? 'Uploading...' : 'Browse Files'}
                          </span>
                        </label>
                      </div>
                    ) : (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <p className="font-medium">{doc.original_filename}</p>
                            <p className="text-sm text-gray-600">
                              Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                            </p>
                          </div>
                          {doc.ai_confidence_score && (
                            <div className="text-sm">
                              <span className="text-gray-600">AI Confidence: </span>
                              <span className="font-semibold text-blue-600">
                                {Math.round(doc.ai_confidence_score * 100)}%
                              </span>
                            </div>
                          )}
                        </div>

                        {doc.verification_status === DOCUMENT_STATUS.REJECTED && (
                          <div className="bg-red-50 border border-red-200 rounded p-3 mb-3">
                            <p className="text-sm text-red-800">
                              <strong>Rejected:</strong> {doc.verification_notes}
                            </p>
                          </div>
                        )}

                        {doc.verification_notes && doc.verification_status !== DOCUMENT_STATUS.REJECTED && (
                          <p className="text-sm text-gray-600 mb-3">{doc.verification_notes}</p>
                        )}

                        <div className="flex space-x-3">
                          <button className="text-sm text-blue-600 hover:text-blue-700">
                            👁️ View
                          </button>
                          <label className="text-sm text-blue-600 hover:text-blue-700 cursor-pointer">
                            <input
                              type="file"
                              className="hidden"
                              accept=".pdf,.png,.jpg,.jpeg"
                              onChange={(e) => handleFileUpload(e.target.files[0], type)}
                              disabled={uploading}
                            />
                            🔄 Re-upload
                          </label>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Progress Card */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="font-semibold text-lg mb-4">Onboarding Progress</h3>
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">Overall Progress</span>
                  <span className="font-semibold text-blue-600">{getProgressPercentage()}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${getProgressPercentage()}%` }}
                  />
                </div>
              </div>
              <p className="text-sm text-gray-600">
                {profile?.document_summary?.verified || 0} of {Object.keys(DOCUMENT_TYPES).length} documents verified
              </p>
            </div>

            {/* Checklist */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="font-semibold text-lg mb-4">Verification Checklist</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-sm text-gray-700">Identity Verification</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-sm text-gray-700">Background Check</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-blue-500">⏳</span>
                  <span className="text-sm text-gray-700">Document Collection</span>
                </div>
              </div>
            </div>

            {/* AI Info */}
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
              <div className="flex items-start space-x-3 mb-3">
                <span className="text-2xl">🤖</span>
                <div>
                  <h4 className="font-semibold text-blue-900 mb-1">AI Powered Verification</h4>
                  <p className="text-sm text-blue-800">
                    Our system analyzes your documents in real-time. Please ensure all text is
                    legible and corners are visible to avoid delays.
                  </p>
                </div>
              </div>
            </div>

            {/* Security Notice */}
            <div className="bg-gray-50 rounded-lg border p-4">
              <div className="flex items-start space-x-2">
                <span className="text-lg">🔒</span>
                <p className="text-xs text-gray-600">
                  Your documents are encrypted and secure. Sensitive data like Aadhaar and PAN
                  numbers are automatically masked for privacy.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {toast.show && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast({ ...toast, show: false })}
        />
      )}
    </div>
  );
};

export default DocumentVerificationPage;
