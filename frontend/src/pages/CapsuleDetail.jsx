/**
 * Capsule Detail Page
 *
 * Changes from original:
 *  - Message rendered as sanitised HTML (DOMPurify) in read mode
 *  - RichTextEditor replaces plain <textarea> in edit mode
 *  - VideoRecorder lets user attach video messages to editable capsules
 *  - Guardian Verification section for EVENT capsules with requires_guardian=true
 */

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import DOMPurify from 'dompurify';
import {
  getCapsuleById,
  updateCapsule,
  deleteCapsule,
  getAttachments,
  uploadAttachment,
  deleteAttachment,
  downloadAttachmentFile,
  requestGuardianVerification,
  getGuardianVerifications,
} from '../api/capsulesApi';
import RichTextEditor from '../components/RichTextEditor.jsx';
import VideoRecorder from '../components/VideoRecorder.jsx';
import '../components/RichTextEditor.css';
import './CapsuleDetail.css';

// ─── helpers ───────────────────────────────────────────────────────────────

function StatusBadge({ status }) {
  const cls = { DRAFT: 'badge-secondary', SCHEDULED: 'badge-warning', SENT: 'badge-success', CANCELLED: 'badge-error' };
  return <span className={`badge ${cls[status] || ''}`}>{status}</span>;
}

function VerificationStatusBadge({ status }) {
  const map = { PENDING: ['badge-warning', '⏳'], CONFIRMED: ['badge-success', '✅'], DENIED: ['badge-error', '❌'], EXPIRED: ['badge-secondary', '⏰'] };
  const [cls, icon] = map[status] || ['badge-secondary', '?'];
  return <span className={`badge ${cls}`}>{icon} {status}</span>;
}

function formatDate(str) {
  if (!str) return 'Not set';
  const utc = str.endsWith('Z') ? str : str + 'Z';
  return new Date(utc).toLocaleString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function formatFileSize(bytes) {
  if (!bytes) return '—';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function isVideoAttachment(mimeType) {
  return typeof mimeType === 'string' && mimeType.startsWith('video/');
}

// ─── component ─────────────────────────────────────────────────────────────

function CapsuleDetail() {
  const { id }    = useParams();
  const navigate  = useNavigate();
  const fileInputRef = useRef(null);

  // ── capsule data ──
  const [capsule, setCapsule]         = useState(null);
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState('');

  // ── edit ──
  const [isEditing, setIsEditing]       = useState(false);
  const [editTitle, setEditTitle]       = useState('');
  const [editMessage, setEditMessage]   = useState('');  // HTML
  const [updating, setUpdating]         = useState(false);
  const [updateError, setUpdateError]   = useState('');

  // ── file upload ──
  const [uploading, setUploading]     = useState(false);
  const [uploadError, setUploadError] = useState('');

  // ── video recorder ──
  const [showVideoRecorder, setShowVideoRecorder] = useState(false);

  // ── delete ──
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [deleting, setDeleting]           = useState(false);

  // ── guardian verification ──
  const [verifications, setVerifications]       = useState([]);
  const [requestingVerif, setRequestingVerif]   = useState(false);
  const [verifError, setVerifError]             = useState('');
  const [verifSuccess, setVerifSuccess]         = useState('');

  // ── load ──
  useEffect(() => { fetchAll(); }, [id]);

  async function fetchAll() {
    setLoading(true); setError('');
    try {
      const [cap, atts] = await Promise.all([getCapsuleById(id), getAttachments(id)]);
      setCapsule(cap);
      setAttachments(atts);
      setEditTitle(cap.title);
      setEditMessage(cap.message);
      // Load guardian verifications if applicable
      if (cap.requires_guardian && cap.release_type === 'EVENT') {
        const vrs = await getGuardianVerifications(id);
        setVerifications(vrs);
      }
    } catch (err) {
      setError(err.response?.status === 404 ? 'Capsule not found.' : 'Failed to load capsule.');
    } finally {
      setLoading(false);
    }
  }

  // ── edit ──
  function handleEditToggle() {
    setIsEditing((v) => !v);
    setUpdateError('');
    if (!isEditing && capsule) {
      setEditTitle(capsule.title);
      setEditMessage(capsule.message);
    }
  }

  function isHtmlEmpty(html) {
    return html.replace(/<[^>]*>/g, '').trim() === '';
  }

  async function handleEditSubmit(e) {
    e.preventDefault();
    if (!editTitle.trim())       { setUpdateError('Title is required.'); return; }
    if (isHtmlEmpty(editMessage)) { setUpdateError('Message cannot be empty.'); return; }

    setUpdating(true); setUpdateError('');
    try {
      const updated = await updateCapsule(id, { title: editTitle.trim(), message: editMessage });
      setCapsule(updated);
      setIsEditing(false);
    } catch (err) {
      setUpdateError(err.response?.data?.message || 'Failed to update capsule.');
    } finally {
      setUpdating(false);
    }
  }

  // ── file upload ──
  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 16 * 1024 * 1024) { setUploadError('File size must be less than 16 MB.'); return; }

    setUploading(true); setUploadError('');
    try {
      await uploadAttachment(id, file);           // pass File directly (not FormData)
      const atts = await getAttachments(id);
      setAttachments(atts);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setUploadError(err.response?.data?.message || 'Failed to upload attachment.');
    } finally {
      setUploading(false);
    }
  }

  async function handleVideoReady(blob, filename) {
    const file = new File([blob], filename, { type: blob.type });
    setUploading(true); setUploadError(''); setShowVideoRecorder(false);
    try {
      await uploadAttachment(id, file);
      const atts = await getAttachments(id);
      setAttachments(atts);
    } catch (err) {
      setUploadError('Video upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  }

  async function handleViewAttachment(att) {
    setUploadError('');

    try {
      const blob = await downloadAttachmentFile(id, att.id);
      const blobUrl = URL.createObjectURL(blob);

      const newWindow = window.open(blobUrl, '_blank');
      if (!newWindow) {
        URL.revokeObjectURL(blobUrl);
        throw new Error('Unable to open attachment in a new tab. Please allow pop-ups for this site.');
      }

      setTimeout(() => URL.revokeObjectURL(blobUrl), 15000);
    } catch (err) {
      setUploadError(err.response?.data?.message || err.message || 'Failed to open attachment.');
    }
  }

  async function handleDeleteAttachment(attId) {
    if (!window.confirm('Delete this attachment?')) return;
    try {
      await deleteAttachment(id, attId);
      setAttachments((prev) => prev.filter((a) => a.id !== attId));
    } catch {
      alert('Failed to delete attachment.');
    }
  }

  // ── delete capsule ──
  async function handleDeleteCapsule() {
    setDeleting(true);
    try {
      await deleteCapsule(id);
      navigate('/dashboard');
    } catch {
      alert('Failed to delete capsule.');
      setDeleting(false); setDeleteConfirm(false);
    }
  }

  // ── guardian verification ──
  async function handleRequestVerification() {
    setRequestingVerif(true); setVerifError(''); setVerifSuccess('');
    try {
      const result = await requestGuardianVerification(id);
      setVerifSuccess(result.message);
      const vrs = await getGuardianVerifications(id);
      setVerifications(vrs);
    } catch (err) {
      setVerifError(err.response?.data?.message || 'Failed to send verification request.');
    } finally {
      setRequestingVerif(false);
    }
  }

  async function refreshVerifications() {
    try {
      const vrs = await getGuardianVerifications(id);
      setVerifications(vrs);
    } catch { /* silent */ }
  }

  // ────────────────────────────────────────────────────────────
  // Render
  // ────────────────────────────────────────────────────────────

  if (loading) return (
    <div className="capsule-detail-page">
      <div className="loading-container"><div className="loading-spinner" /><p>Loading capsule…</p></div>
    </div>
  );

  if (error) return (
    <div className="capsule-detail-page">
      <div className="error-container">
        <h2>Error</h2><p>{error}</p>
        <Link to="/dashboard" className="btn btn-primary">Back to Dashboard</Link>
      </div>
    </div>
  );

  if (!capsule) return null;

  const canEdit = capsule.status === 'DRAFT' || capsule.status === 'SCHEDULED';
  const showGuardianSection = capsule.requires_guardian && capsule.release_type === 'EVENT';

  return (
    <div className="capsule-detail-page">
      <div className="capsule-detail-container">

        {/* ── Header ── */}
        <header className="capsule-header">
          <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
          <div className="header-content">
            <div className="header-left">
              <h1>{capsule.title}</h1>
              <StatusBadge status={capsule.status} />
            </div>
            {canEdit && (
              <div className="header-actions">
                <button className="btn btn-secondary" onClick={handleEditToggle} disabled={updating}>
                  {isEditing ? 'Cancel Edit' : 'Edit'}
                </button>
                <button className="btn btn-danger" onClick={() => setDeleteConfirm(true)} disabled={deleting}>
                  Delete
                </button>
              </div>
            )}
          </div>
        </header>

        {/* ── Delete confirmation ── */}
        {deleteConfirm && (
          <div className="delete-confirmation">
            <p>Are you sure you want to delete this capsule? This cannot be undone.</p>
            <div className="confirmation-actions">
              <button className="btn btn-secondary" onClick={() => setDeleteConfirm(false)} disabled={deleting}>Cancel</button>
              <button className="btn btn-danger" onClick={handleDeleteCapsule} disabled={deleting}>
                {deleting ? 'Deleting…' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        )}

        {/* ── Info grid ── */}
        <section className="capsule-info">
          <div className="info-grid">
            <div className="info-item"><span className="info-label">Release Date</span><span className="info-value">{formatDate(capsule.release_at)}</span></div>
            <div className="info-item"><span className="info-label">Release Type</span><span className="info-value">{capsule.release_type}</span></div>
            <div className="info-item"><span className="info-label">Guardian Required</span><span className="info-value">{capsule.requires_guardian ? 'Yes' : 'No'}</span></div>
            <div className="info-item"><span className="info-label">Created</span><span className="info-value">{formatDate(capsule.created_at)}</span></div>
          </div>
        </section>

        {/* ── Recipients ── */}
        <section className="capsule-section">
          <h2>Recipients</h2>
          {capsule.recipients?.length > 0 ? (
            <div className="recipients-list">
              {capsule.recipients.map((r) => (
                <div key={r.id} className="recipient-item">
                  <span className="recipient-name">{r.name}</span>
                  <span className="recipient-email">{r.email}</span>
                </div>
              ))}
            </div>
          ) : <p className="empty-text">No recipients assigned.</p>}
        </section>

        {/* ── Message ── */}
        <section className="capsule-section">
          <h2>Message</h2>

          {isEditing ? (
            <form onSubmit={handleEditSubmit} className="edit-form">
              {updateError && <div className="alert alert-error">{updateError}</div>}

              <div className="form-group">
                <label htmlFor="edit-title">Title</label>
                <input
                  type="text"
                  id="edit-title"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  disabled={updating}
                />
              </div>

              <div className="form-group">
                <label>Message</label>
                <RichTextEditor
                  content={editMessage}
                  onChange={setEditMessage}
                  disabled={updating}
                  placeholder="Write your message…"
                />
              </div>

              <div className="edit-actions">
                <button type="button" className="btn btn-secondary" onClick={handleEditToggle} disabled={updating}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={updating}>
                  {updating ? 'Saving…' : 'Save Changes'}
                </button>
              </div>
            </form>
          ) : (
            <div className="message-content">
              <p className="encryption-badge">🔒 Securely encrypted</p>
              {/* Render HTML from TipTap, sanitised with DOMPurify */}
              <div
                className="message-text rich-message-display"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(capsule.message || '') }}
              />
            </div>
          )}
        </section>

        {/* ── Video / Attachments ── */}
        <section className="capsule-section">
          <div className="section-header">
            <h2>Attachments</h2>
            {canEdit && (
              <div className="section-header-actions">
                <button className="btn btn-secondary btn-small" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
                  {uploading ? 'Uploading…' : 'Add File'}
                </button>
                <button className="btn btn-secondary btn-small" onClick={() => setShowVideoRecorder((v) => !v)} disabled={uploading}>
                  🎥 {showVideoRecorder ? 'Hide Recorder' : 'Record Video'}
                </button>
              </div>
            )}
          </div>

          <input type="file" ref={fileInputRef} onChange={handleFileUpload} style={{ display: 'none' }} />

          {uploadError && <div className="alert alert-error">{uploadError}</div>}

          {canEdit && showVideoRecorder && (
            <div style={{ marginBottom: '16px' }}>
              <VideoRecorder onVideoReady={handleVideoReady} />
            </div>
          )}

          {attachments.length > 0 ? (
            <div className="attachments-list">
              {attachments.map((att) => (
                <div key={att.id} className="attachment-item">
                  <div className="attachment-info">
                    <span className="attachment-name">{att.original_filename}</span>
                    <span className="attachment-meta">
                      {formatFileSize(att.size_bytes)} &bull; {att.mime_type}
                    </span>
                    </div>
                  <div className="attachment-actions">
                    <button
                      className="btn btn-secondary btn-small"
                      type="button"
                      onClick={() => handleViewAttachment(att)}
                    >
                      View
                    </button>
                    {canEdit && (
                      <button className="btn btn-danger btn-icon" onClick={() => handleDeleteAttachment(att.id)} title="Delete">✕</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : <p className="empty-text">No attachments.</p>}

          <p className="helper-text">Allowed: Images, PDFs, Documents, Videos (max 16 MB each)</p>
        </section>

        {/* ── Guardian Verification ── */}
        {showGuardianSection && (
          <section className="capsule-section guardian-section">
            <div className="section-header">
              <h2>🛡️ Guardian Verification</h2>
              {canEdit && (
                <button
                  className="btn btn-secondary btn-small"
                  onClick={handleRequestVerification}
                  disabled={requestingVerif}
                >
                  {requestingVerif ? 'Sending…' : 'Request Verification'}
                </button>
              )}
              {verifications.length > 0 && (
                <button className="btn btn-secondary btn-small" onClick={refreshVerifications}>↻ Refresh</button>
              )}
            </div>

            {verifError   && <div className="alert alert-error">{verifError}</div>}
            {verifSuccess && <div className="alert alert-success">{verifSuccess}</div>}

            {/* Guardian list */}
            {capsule.guardians?.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <p className="helper-text" style={{ marginBottom: '8px' }}>Assigned guardians:</p>
                <div className="recipients-list">
                  {capsule.guardians.map((g) => (
                    <div key={g.id} className="recipient-item">
                      <span className="recipient-name">{g.name}</span>
                      <span className="recipient-email">{g.email} {g.relation ? `· ${g.relation}` : ''}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Audit log */}
            {verifications.length > 0 ? (
              <div className="guardian-audit">
                <p className="helper-text" style={{ marginBottom: '8px' }}>Verification history:</p>
                <div className="guardian-audit-table">
                  {verifications.map((vr) => (
                    <div key={vr.id} className="guardian-audit-row">
                      <div className="guardian-audit-info">
                        <span className="guardian-audit-name">{vr.guardian_name}</span>
                        <span className="guardian-audit-email">{vr.guardian_email}</span>
                        <span className="guardian-audit-date">Sent: {formatDate(vr.sent_at)}</span>
                        {vr.responded_at && (
                          <span className="guardian-audit-date">Responded: {formatDate(vr.responded_at)}</span>
                        )}
                        {vr.response_notes && (
                          <span className="guardian-audit-notes">"{vr.response_notes}"</span>
                        )}
                      </div>
                      <VerificationStatusBadge status={vr.status} />
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="empty-text">
                No verification requests sent yet.
                {canEdit && ' Use "Request Verification" to notify your guardians.'}
              </p>
            )}
          </section>
        )}

      </div>
    </div>
  );
}

export default CapsuleDetail;
