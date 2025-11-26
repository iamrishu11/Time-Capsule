/**
 * Create Capsule Page Component
 * 
 * Form for creating a new time capsule with message encryption.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRecipients } from '../api/recipientsApi';
import { createCapsule } from '../api/capsulesApi';
import './CreateCapsule.css';

function CreateCapsule() {
  const navigate = useNavigate();
  
  const [recipients, setRecipients] = useState([]);
  const [loadingRecipients, setLoadingRecipients] = useState(true);
  
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    recipient_ids: [],
    release_type: 'TIME',
    release_date: '',
    release_time: '',
    requires_guardian: false,
  });
  
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Fetch recipients on mount
  useEffect(() => {
    fetchRecipients();
  }, []);

  const fetchRecipients = async () => {
    try {
      const data = await getRecipients();
      setRecipients(data);
    } catch (err) {
      console.error('Failed to fetch recipients:', err);
      setError('Failed to load recipients. Please try again.');
    } finally {
      setLoadingRecipients(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    if (error) setError('');
  };

  const handleRecipientToggle = (recipientId) => {
    setFormData((prev) => {
      const isSelected = prev.recipient_ids.includes(recipientId);
      return {
        ...prev,
        recipient_ids: isSelected
          ? prev.recipient_ids.filter((id) => id !== recipientId)
          : [...prev.recipient_ids, recipientId],
      };
    });
    if (error) setError('');
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      return 'Title is required';
    }
    if (!formData.message.trim()) {
      return 'Message is required';
    }
    if (formData.recipient_ids.length === 0) {
      return 'Please select at least one recipient';
    }
    if (formData.release_type === 'TIME') {
      if (!formData.release_date) {
        return 'Release date is required for time-based capsules';
      }
      if (!formData.release_time) {
        return 'Release time is required for time-based capsules';
      }
      
      // Check if date is in the future
      const releaseDateTime = new Date(`${formData.release_date}T${formData.release_time}`);
      if (releaseDateTime <= new Date()) {
        return 'Release date must be in the future';
      }
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);

    try {
      // Build ISO datetime string
      const releaseAt = formData.release_type === 'TIME'
        ? new Date(`${formData.release_date}T${formData.release_time}`).toISOString()
        : null;

      const payload = {
        title: formData.title.trim(),
        message: formData.message.trim(),
        recipient_ids: formData.recipient_ids,
        release_type: formData.release_type,
        release_at: releaseAt,
        requires_guardian: formData.requires_guardian,
      };

      const result = await createCapsule(payload);
      
      // Navigate to the capsule detail page or dashboard
      navigate(`/capsules/${result.id}`);
    } catch (err) {
      console.error('Failed to create capsule:', err);
      setError(
        err.response?.data?.message || 'Failed to create capsule. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  // Get minimum date for date picker (today)
  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  return (
    <div className="create-capsule-page">
      <div className="create-capsule-container">
        <header className="page-header">
          <h1>Create Time Capsule</h1>
          <p className="subtitle">
            Write a message that will be delivered to your loved ones at a future date
          </p>
        </header>

        <form onSubmit={handleSubmit} className="capsule-form">
          {error && <div className="alert alert-error">{error}</div>}

          {/* Title */}
          <div className="form-section">
            <div className="form-group">
              <label htmlFor="title">Capsule Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="e.g., For your 18th birthday"
                disabled={submitting}
              />
            </div>
          </div>

          {/* Recipients Selection */}
          <div className="form-section">
            <label className="section-label">Select Recipients *</label>
            {loadingRecipients ? (
              <div className="loading-inline">Loading recipients...</div>
            ) : recipients.length === 0 ? (
              <div className="no-recipients">
                <p>No recipients found.</p>
                <button
                  type="button"
                  className="btn btn-secondary btn-small"
                  onClick={() => navigate('/recipients')}
                >
                  Add Recipients First
                </button>
              </div>
            ) : (
              <div className="recipients-selection">
                {recipients.map((recipient) => (
                  <label
                    key={recipient.id}
                    className={`recipient-checkbox ${
                      formData.recipient_ids.includes(recipient.id) ? 'selected' : ''
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={formData.recipient_ids.includes(recipient.id)}
                      onChange={() => handleRecipientToggle(recipient.id)}
                      disabled={submitting}
                    />
                    <span className="recipient-info">
                      <span className="name">{recipient.name}</span>
                      <span className="email">{recipient.email}</span>
                    </span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Message */}
          <div className="form-section">
            <div className="form-group">
              <label htmlFor="message">Your Message *</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleInputChange}
                placeholder="Write your heartfelt message here... This will be encrypted and securely stored."
                rows={10}
                disabled={submitting}
              />
              <p className="helper-text">
                🔒 Your message will be encrypted before being stored in the database.
              </p>
            </div>
          </div>

          {/* Release Settings */}
          <div className="form-section">
            <label className="section-label">Delivery Settings</label>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="release_type">Release Type</label>
                <select
                  id="release_type"
                  name="release_type"
                  value={formData.release_type}
                  onChange={handleInputChange}
                  disabled={submitting}
                >
                  <option value="TIME">Time-based (specific date)</option>
                  <option value="EVENT">Event-based (coming soon)</option>
                </select>
              </div>
            </div>

            {formData.release_type === 'TIME' && (
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="release_date">Release Date *</label>
                  <input
                    type="date"
                    id="release_date"
                    name="release_date"
                    value={formData.release_date}
                    onChange={handleInputChange}
                    min={getMinDate()}
                    disabled={submitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="release_time">Release Time *</label>
                  <input
                    type="time"
                    id="release_time"
                    name="release_time"
                    value={formData.release_time}
                    onChange={handleInputChange}
                    disabled={submitting}
                  />
                </div>
              </div>
            )}

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="requires_guardian"
                  checked={formData.requires_guardian}
                  onChange={handleInputChange}
                  disabled={submitting}
                />
                <span>Require guardian confirmation before delivery</span>
              </label>
              <p className="helper-text">
                If enabled, a trusted guardian must confirm certain conditions before the capsule is delivered.
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/dashboard')}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting || loadingRecipients}
            >
              {submitting ? 'Creating Capsule...' : 'Create Capsule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateCapsule;
