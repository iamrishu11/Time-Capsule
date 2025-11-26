/**
 * Capsule Detail Page Component
 * 
 * Displays a single capsule with decrypted message, recipients, and attachments.
 */

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  getCapsuleById,
  updateCapsule,
  deleteCapsule,
  getAttachments,
  uploadAttachment,
  deleteAttachment,
} from '../api/capsulesApi';
import './CapsuleDetail.css';

function CapsuleDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const [capsule, setCapsule] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [isEditing, setIsEditing] = useState(false);
  const [editFormData, setEditFormData] = useState({ title: '', message: '' });
  const [updateError, setUpdateError] = useState('');
  const [updating, setUpdating] = useState(false);
  
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchCapsuleData();
  }, [id]);

  const fetchCapsuleData = async () => {
    setLoading(true);
    setError('');
    try {
      const [capsuleData, attachmentsData] = await Promise.all([
        getCapsuleById(id),
        getAttachments(id),
      ]);
      setCapsule(capsuleData);
      setAttachments(attachmentsData);
      setEditFormData({
        title: capsuleData.title,
        message: capsuleData.message,
      });
    } catch (err) {
      console.error('Failed to fetch capsule:', err);
      setError(
        err.response?.status === 404
          ? 'Capsule not found'
          : 'Failed to load capsule. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleEditToggle = () => {
    setIsEditing(!isEditing);
    setUpdateError('');
    if (!isEditing && capsule) {
      setEditFormData({
        title: capsule.title,
        message: capsule.message,
      });
    }
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditFormData((prev) => ({ ...prev, [name]: value }));
    if (updateError) setUpdateError('');
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    
    if (!editFormData.title.trim()) {
      setUpdateError('Title is required');
      return;
    }
    if (!editFormData.message.trim()) {
      setUpdateError('Message is required');
      return;
    }

    setUpdating(true);
    setUpdateError('');

    try {
      const updated = await updateCapsule(id, {
        title: editFormData.title.trim(),
        message: editFormData.message.trim(),
      });
      setCapsule(updated);
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to update capsule:', err);
      setUpdateError(
        err.response?.data?.message || 'Failed to update capsule. Please try again.'
      );
    } finally {
      setUpdating(false);
    }
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
      setUploadError('File size must be less than 16MB');
      return;
    }

    setUploading(true);
    setUploadError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      await uploadAttachment(id, formData);
      
      // Refresh attachments list
      const attachmentsData = await getAttachments(id);
      setAttachments(attachmentsData);
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error('Failed to upload attachment:', err);
      setUploadError(
        err.response?.data?.message || 'Failed to upload attachment. Please try again.'
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteAttachment = async (attachmentId) => {
    if (!window.confirm('Are you sure you want to delete this attachment?')) {
      return;
    }

    try {
      await deleteAttachment(id, attachmentId);
      setAttachments((prev) => prev.filter((a) => a.id !== attachmentId));
    } catch (err) {
      console.error('Failed to delete attachment:', err);
      alert('Failed to delete attachment. Please try again.');
    }
  };

  const handleDeleteCapsule = async () => {
    setDeleting(true);
    try {
      await deleteCapsule(id);
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to delete capsule:', err);
      alert('Failed to delete capsule. Please try again.');
      setDeleting(false);
      setDeleteConfirm(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'PENDING':
        return 'badge-warning';
      case 'RELEASED':
        return 'badge-success';
      case 'DELIVERED':
        return 'badge-info';
      case 'CANCELLED':
        return 'badge-error';
      default:
        return '';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (loading) {
    return (
      <div className="capsule-detail-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading capsule...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="capsule-detail-page">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <Link to="/dashboard" className="btn btn-primary">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!capsule) {
    return null;
  }

  return (
    <div className="capsule-detail-page">
      <div className="capsule-detail-container">
        {/* Header */}
        <header className="capsule-header">
          <Link to="/dashboard" className="back-link">
            ← Back to Dashboard
          </Link>
          
          <div className="header-content">
            <div className="header-left">
              <h1>{capsule.title}</h1>
              <span className={`badge ${getStatusBadgeClass(capsule.status)}`}>
                {capsule.status}
              </span>
            </div>
            
            {capsule.status === 'PENDING' && (
              <div className="header-actions">
                <button
                  className="btn btn-secondary"
                  onClick={handleEditToggle}
                  disabled={updating}
                >
                  {isEditing ? 'Cancel Edit' : 'Edit'}
                </button>
                <button
                  className="btn btn-danger"
                  onClick={() => setDeleteConfirm(true)}
                  disabled={deleting}
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        </header>

        {/* Delete Confirmation */}
        {deleteConfirm && (
          <div className="delete-confirmation">
            <p>Are you sure you want to delete this capsule? This action cannot be undone.</p>
            <div className="confirmation-actions">
              <button
                className="btn btn-secondary"
                onClick={() => setDeleteConfirm(false)}
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDeleteCapsule}
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        )}

        {/* Capsule Info */}
        <section className="capsule-info">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Release Date</span>
              <span className="info-value">{formatDate(capsule.release_at)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Release Type</span>
              <span className="info-value">{capsule.release_type}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Guardian Required</span>
              <span className="info-value">{capsule.requires_guardian ? 'Yes' : 'No'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Created</span>
              <span className="info-value">{formatDate(capsule.created_at)}</span>
            </div>
          </div>
        </section>

        {/* Recipients */}
        <section className="capsule-section">
          <h2>Recipients</h2>
          {capsule.recipients && capsule.recipients.length > 0 ? (
            <div className="recipients-list">
              {capsule.recipients.map((recipient) => (
                <div key={recipient.id} className="recipient-item">
                  <span className="recipient-name">{recipient.name}</span>
                  <span className="recipient-email">{recipient.email}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-text">No recipients assigned</p>
          )}
        </section>

        {/* Message */}
        <section className="capsule-section">
          <h2>Message</h2>
          {isEditing ? (
            <form onSubmit={handleEditSubmit} className="edit-form">
              {updateError && <div className="alert alert-error">{updateError}</div>}
              
              <div className="form-group">
                <label htmlFor="title">Title</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={editFormData.title}
                  onChange={handleEditChange}
                  disabled={updating}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="message">Message</label>
                <textarea
                  id="message"
                  name="message"
                  value={editFormData.message}
                  onChange={handleEditChange}
                  rows={10}
                  disabled={updating}
                />
              </div>
              
              <div className="edit-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleEditToggle}
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={updating}
                >
                  {updating ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          ) : (
            <div className="message-content">
              <p className="encryption-badge">🔒 Securely encrypted</p>
              <div className="message-text">{capsule.message}</div>
            </div>
          )}
        </section>

        {/* Attachments */}
        <section className="capsule-section">
          <div className="section-header">
            <h2>Attachments</h2>
            {capsule.status === 'PENDING' && (
              <button
                className="btn btn-secondary btn-small"
                onClick={handleFileSelect}
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Add Attachment'}
              </button>
            )}
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />

          {uploadError && <div className="alert alert-error">{uploadError}</div>}

          {attachments.length > 0 ? (
            <div className="attachments-list">
              {attachments.map((attachment) => (
                <div key={attachment.id} className="attachment-item">
                  <div className="attachment-info">
                    <span className="attachment-name">{attachment.filename}</span>
                    <span className="attachment-meta">
                      {formatFileSize(attachment.file_size)} • {attachment.mime_type}
                    </span>
                  </div>
                  {capsule.status === 'PENDING' && (
                    <button
                      className="btn btn-danger btn-icon"
                      onClick={() => handleDeleteAttachment(attachment.id)}
                      title="Delete attachment"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-text">No attachments</p>
          )}
          
          <p className="helper-text">
            Allowed file types: Images, PDFs, Documents, Videos (max 16MB each)
          </p>
        </section>
      </div>
    </div>
  );
}

export default CapsuleDetail;
