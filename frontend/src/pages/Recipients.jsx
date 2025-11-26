/**
 * Recipients Page Component
 * 
 * Allows users to manage their recipients (people who will receive capsules).
 */

import { useState, useEffect } from 'react';
import { getRecipients, createRecipient, deleteRecipient } from '../api/recipientsApi';
import './Recipients.css';

function Recipients() {
  const [recipients, setRecipients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    relation: '',
  });
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Fetch recipients on mount
  useEffect(() => {
    fetchRecipients();
  }, []);

  const fetchRecipients = async () => {
    try {
      setLoading(true);
      const data = await getRecipients();
      setRecipients(data);
      setError('');
    } catch (err) {
      console.error('Failed to fetch recipients:', err);
      setError('Failed to load recipients. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (formError) setFormError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    // Validate
    if (!formData.name.trim()) {
      setFormError('Name is required');
      return;
    }
    if (!formData.email.trim()) {
      setFormError('Email is required');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setFormError('Please enter a valid email address');
      return;
    }

    setSubmitting(true);

    try {
      await createRecipient({
        name: formData.name.trim(),
        email: formData.email.trim(),
        relation: formData.relation.trim() || undefined,
      });

      // Reset form and refresh list
      setFormData({ name: '', email: '', relation: '' });
      setShowForm(false);
      fetchRecipients();
    } catch (err) {
      console.error('Failed to create recipient:', err);
      setFormError(
        err.response?.data?.message || 'Failed to create recipient. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    try {
      await deleteRecipient(id);
      fetchRecipients();
    } catch (err) {
      console.error('Failed to delete recipient:', err);
      alert('Failed to delete recipient. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="recipients-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading recipients...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recipients-page">
      <div className="recipients-container">
        <header className="page-header">
          <div className="header-content">
            <h1>Recipients</h1>
            <p className="subtitle">
              Manage the people who will receive your time capsules
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : '+ Add Recipient'}
          </button>
        </header>

        {error && <div className="alert alert-error">{error}</div>}

        {/* Add Recipient Form */}
        {showForm && (
          <div className="add-recipient-card">
            <h2>Add New Recipient</h2>
            <form onSubmit={handleSubmit} className="recipient-form">
              {formError && <div className="alert alert-error">{formError}</div>}

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="name">Name *</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Enter recipient's name"
                    disabled={submitting}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">Email *</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="recipient@example.com"
                    disabled={submitting}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="relation">Relationship</label>
                  <input
                    type="text"
                    id="relation"
                    name="relation"
                    value={formData.relation}
                    onChange={handleInputChange}
                    placeholder="e.g., daughter, friend"
                    disabled={submitting}
                  />
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? 'Adding...' : 'Add Recipient'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Recipients List */}
        <div className="recipients-list">
          {recipients.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">👥</div>
              <h3>No Recipients Yet</h3>
              <p>Add recipients who will receive your time capsules.</p>
              {!showForm && (
                <button
                  className="btn btn-primary"
                  onClick={() => setShowForm(true)}
                >
                  Add Your First Recipient
                </button>
              )}
            </div>
          ) : (
            <div className="recipients-grid">
              {recipients.map((recipient) => (
                <div key={recipient.id} className="recipient-card">
                  <div className="recipient-avatar">
                    {recipient.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="recipient-info">
                    <h3 className="recipient-name">{recipient.name}</h3>
                    <p className="recipient-email">{recipient.email}</p>
                    {recipient.relation && (
                      <span className="recipient-relation">{recipient.relation}</span>
                    )}
                  </div>
                  <div className="recipient-actions">
                    <button
                      className="btn btn-danger btn-small"
                      onClick={() => handleDelete(recipient.id, recipient.name)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Recipients;
