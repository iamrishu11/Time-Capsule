/**
 * Create Capsule Page
 *
 * Uses RichTextEditor (TipTap) for the message body and VideoRecorder for
 * optional in-browser video recording. A recorded video is uploaded as an
 * attachment immediately after the capsule is created.
 */

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRecipients } from '../api/recipientsApi';
import { createCapsule, uploadAttachment } from '../api/capsulesApi';
import RichTextEditor from '../components/RichTextEditor.jsx';
import VideoRecorder from '../components/VideoRecorder.jsx';
import './CreateCapsule.css';

function CreateCapsule() {
  const navigate = useNavigate();

  const [recipients, setRecipients]               = useState([]);
  const [loadingRecipients, setLoadingRecipients] = useState(true);

  const [title, setTitle]                           = useState('');
  const [message, setMessage]                       = useState('');  // HTML from TipTap
  const [recipientIds, setRecipientIds]             = useState([]);
  const [releaseType, setReleaseType]               = useState('TIME');
  const [releaseDate, setReleaseDate]               = useState('');
  const [releaseTime, setReleaseTime]               = useState('');
  const [requiresGuardian, setRequiresGuardian]     = useState(false);
  const [showVideoRecorder, setShowVideoRecorder]   = useState(false);

  // Pending video blob (uploaded after capsule creation)
  const pendingVideoRef = useRef(null); // { blob, filename }

  const [error, setError]         = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getRecipients()
      .then(setRecipients)
      .catch(() => setError('Failed to load recipients. Please refresh.'))
      .finally(() => setLoadingRecipients(false));
  }, []);

  const toggleRecipient = (id) => {
    setRecipientIds((prev) =>
      prev.includes(id) ? prev.filter((r) => r !== id) : [...prev, id]
    );
    setError('');
  };

  const handleVideoReady = (blob, filename) => {
    pendingVideoRef.current = { blob, filename };
    setShowVideoRecorder(false);
  };

  // Strip HTML tags to check if TipTap content is truly empty
  const isMessageEmpty = (html) => {
    const text = html.replace(/<[^>]*>/g, '').trim();
    return text === '';
  };

  const validate = () => {
    if (!title.trim())                  return 'Title is required.';
    if (isMessageEmpty(message))        return 'Message is required.';
    if (recipientIds.length === 0)      return 'Please select at least one recipient.';
    if (releaseType === 'TIME') {
      if (!releaseDate)                 return 'Release date is required.';
      if (!releaseTime)                 return 'Release time is required.';
      const dt = new Date(`${releaseDate}T${releaseTime}`);
      if (dt <= new Date())             return 'Release date must be in the future.';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const validationError = validate();
    if (validationError) { setError(validationError); return; }

    setSubmitting(true);

    try {
      const releaseAt =
        releaseType === 'TIME'
          ? new Date(`${releaseDate}T${releaseTime}`).toISOString()
          : null;

      const result = await createCapsule({
        title: title.trim(),
        message,                // HTML string — encrypted server-side
        recipient_ids: recipientIds,
        release_type: releaseType,
        release_at: releaseAt,
        requires_guardian: requiresGuardian,
      });

      // Upload pending video if the user recorded one
      if (pendingVideoRef.current) {
        const { blob, filename } = pendingVideoRef.current;
        const file = new File([blob], filename, { type: blob.type });
        try {
          await uploadAttachment(result.id, file);
        } catch (uploadErr) {
          console.error('Video upload failed (capsule still created):', uploadErr);
        }
      }

      navigate(`/capsules/${result.id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create capsule. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getMinDate = () => new Date().toISOString().split('T')[0];

  return (
    <div className="create-capsule-page">
      <div className="create-capsule-container">
        <header className="page-header">
          <h1>Create Time Capsule</h1>
          <p className="subtitle">
            Write a message that will be delivered to your loved ones at a future date.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="capsule-form">
          {error && <div className="alert alert-error">{error}</div>}

          {/* ── Title ── */}
          <div className="form-section">
            <div className="form-group">
              <label htmlFor="title">Capsule Title *</label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => { setTitle(e.target.value); setError(''); }}
                placeholder="e.g., For your 18th birthday"
                disabled={submitting}
              />
            </div>
          </div>

          {/* ── Recipients ── */}
          <div className="form-section">
            <label className="section-label">Select Recipients *</label>
            {loadingRecipients ? (
              <div className="loading-inline">Loading recipients…</div>
            ) : recipients.length === 0 ? (
              <div className="no-recipients">
                <p>No recipients found.</p>
                <button type="button" className="btn btn-secondary btn-small" onClick={() => navigate('/recipients')}>
                  Add Recipients First
                </button>
              </div>
            ) : (
              <div className="recipients-selection">
                {recipients.map((r) => (
                  <label
                    key={r.id}
                    className={`recipient-checkbox ${recipientIds.includes(r.id) ? 'selected' : ''}`}
                  >
                    <input
                      type="checkbox"
                      checked={recipientIds.includes(r.id)}
                      onChange={() => toggleRecipient(r.id)}
                      disabled={submitting}
                    />
                    <span className="recipient-info">
                      <span className="name">{r.name}</span>
                      <span className="email">{r.email}</span>
                    </span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* ── Message (RichTextEditor) ── */}
          <div className="form-section">
            <div className="form-group">
              <label>Your Message *</label>
              <RichTextEditor
                content={message}
                onChange={(html) => { setMessage(html); setError(''); }}
                disabled={submitting}
                placeholder="Write your heartfelt message here… This will be encrypted and securely stored."
              />
              <p className="helper-text">
                🔒 Your message will be encrypted before being stored.
              </p>
            </div>
          </div>

          {/* ── Video Recorder ── */}
          <div className="form-section">
            <label className="section-label">Video Message (optional)</label>
            {pendingVideoRef.current && !showVideoRecorder ? (
              <div className="video-ready-notice">
                <span>🎥 Video recording ready to attach</span>
                <button
                  type="button"
                  className="btn btn-secondary btn-small"
                  onClick={() => { pendingVideoRef.current = null; setShowVideoRecorder(true); }}
                >
                  Re-record
                </button>
              </div>
            ) : showVideoRecorder ? (
              <VideoRecorder onVideoReady={handleVideoReady} disabled={submitting} />
            ) : (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowVideoRecorder(true)}
                disabled={submitting}
              >
                🎥 Record a Video Message
              </button>
            )}
          </div>

          {/* ── Delivery Settings ── */}
          <div className="form-section">
            <label className="section-label">Delivery Settings</label>

            <div className="form-group">
              <label htmlFor="release_type">Release Type</label>
              <select
                id="release_type"
                value={releaseType}
                onChange={(e) => setReleaseType(e.target.value)}
                disabled={submitting}
              >
                <option value="TIME">Time-based (specific date)</option>
                <option value="EVENT">Event-based (inactivity trigger)</option>
              </select>
            </div>

            {releaseType === 'TIME' && (
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="release_date">Release Date *</label>
                  <input
                    type="date"
                    id="release_date"
                    value={releaseDate}
                    onChange={(e) => setReleaseDate(e.target.value)}
                    min={getMinDate()}
                    disabled={submitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="release_time">Release Time *</label>
                  <input
                    type="time"
                    id="release_time"
                    value={releaseTime}
                    onChange={(e) => setReleaseTime(e.target.value)}
                    disabled={submitting}
                  />
                </div>
              </div>
            )}

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={requiresGuardian}
                  onChange={(e) => setRequiresGuardian(e.target.checked)}
                  disabled={submitting}
                />
                <span>Require guardian confirmation before delivery</span>
              </label>
              <p className="helper-text">
                If enabled, designated guardians must confirm before the capsule is released.
              </p>
            </div>
          </div>

          {/* ── Actions ── */}
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/dashboard')} disabled={submitting}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting || loadingRecipients}>
              {submitting ? 'Creating Capsule…' : 'Create Capsule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateCapsule;
