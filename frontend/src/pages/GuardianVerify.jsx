/**
 * GuardianVerify — Public page for guardian verification portal.
 *
 * Accessed via the token link in a guardian's verification email:
 *   /guardian/verify/:token
 *
 * No authentication required. The token itself authenticates the request.
 *
 * Flow:
 *   1. Load  → fetch request details from GET /api/guardian/verify/:token
 *   2. Idle  → show capsule info + Confirm / Deny form
 *   3. Done  → show thank-you or already-responded message
 */

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/apiClient';
import './GuardianVerify.css';

export default function GuardianVerify() {
  const { token } = useParams();

  const [phase, setPhase]     = useState('loading'); // loading | pending | done | error | expired
  const [info, setInfo]       = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const [action, setAction]   = useState(''); // 'CONFIRM' | 'DENY'
  const [notes, setNotes]     = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [doneData, setDoneData]       = useState(null);

  // ── Fetch request details on mount ──
  useEffect(() => {
    if (!token) { setPhase('error'); setErrorMsg('No verification token found in the URL.'); return; }

    apiClient.get(`/api/guardian/verify/${token}`)
      .then(({ data }) => {
        if (data.already_responded) {
          setDoneData(data);
          setPhase('done');
        } else {
          setInfo(data);
          setPhase('pending');
        }
      })
      .catch((err) => {
        const status = err.response?.status;
        if (status === 410) { setPhase('expired'); }
        else if (status === 404) { setPhase('error'); setErrorMsg('This verification link is invalid or has already been used.'); }
        else { setPhase('error'); setErrorMsg('Unable to load verification details. Please try again later.'); }
      });
  }, [token]);

  // ── Submit decision ──
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!action) { setSubmitError('Please choose Confirm or Deny before submitting.'); return; }

    setSubmitting(true);
    setSubmitError('');

    try {
      const { data } = await apiClient.post(`/api/guardian/verify/${token}/respond`, { action, notes });
      setDoneData({ ...info, status: data.status, response_notes: notes });
      setPhase('done');
    } catch (err) {
      const msg = err.response?.data?.error || 'Failed to submit your response. Please try again.';
      setSubmitError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  // ────────────────────────────────────────────────────────────
  // Render helpers
  // ────────────────────────────────────────────────────────────

  if (phase === 'loading') {
    return (
      <div className="gv-page">
        <div className="gv-card">
          <div className="gv-spinner" />
          <p className="gv-sub">Loading verification details…</p>
        </div>
      </div>
    );
  }

  if (phase === 'expired') {
    return (
      <div className="gv-page">
        <div className="gv-card gv-card--warn">
          <div className="gv-icon">⏳</div>
          <h1 className="gv-title">Link Expired</h1>
          <p className="gv-sub">
            This verification link has expired. Please contact the capsule owner to request a new one.
          </p>
        </div>
      </div>
    );
  }

  if (phase === 'error') {
    return (
      <div className="gv-page">
        <div className="gv-card gv-card--error">
          <div className="gv-icon">❌</div>
          <h1 className="gv-title">Invalid Link</h1>
          <p className="gv-sub">{errorMsg}</p>
        </div>
      </div>
    );
  }

  if (phase === 'done') {
    const confirmed = doneData?.status === 'CONFIRMED';
    return (
      <div className="gv-page">
        <div className={`gv-card ${confirmed ? 'gv-card--confirm' : 'gv-card--deny'}`}>
          <div className="gv-icon">{confirmed ? '✅' : '❌'}</div>
          <h1 className="gv-title">
            {doneData?.already_responded ? 'Already Responded' : 'Response Recorded'}
          </h1>
          <p className="gv-sub">
            {doneData?.already_responded
              ? `You previously ${confirmed ? 'confirmed' : 'denied'} this request.`
              : `Thank you, ${doneData?.guardian_name}. Your decision has been recorded.`}
          </p>

          <div className="gv-summary">
            <div className="gv-summary-row">
              <span className="gv-label">Capsule</span>
              <span className="gv-value">{doneData?.capsule_title}</span>
            </div>
            <div className="gv-summary-row">
              <span className="gv-label">Decision</span>
              <span className={`gv-value gv-decision ${confirmed ? 'gv-decision--confirm' : 'gv-decision--deny'}`}>
                {doneData?.status}
              </span>
            </div>
            {doneData?.response_notes && (
              <div className="gv-summary-row">
                <span className="gv-label">Your notes</span>
                <span className="gv-value">{doneData.response_notes}</span>
              </div>
            )}
          </div>

          <p className="gv-footer-note">
            The capsule owner has been notified of your decision. You may close this window.
          </p>
        </div>
      </div>
    );
  }

  // phase === 'pending'
  return (
    <div className="gv-page">
      <div className="gv-card">
        {/* Header */}
        <div className="gv-brand">
          <span className="gv-brand-icon">🛡️</span>
          <span className="gv-brand-name">Time Capsule &mdash; Guardian Portal</span>
        </div>

        <h1 className="gv-title">Guardian Verification Request</h1>
        <p className="gv-sub">
          <strong>{info?.owner_name}</strong> has designated you as a trusted guardian and is
          requesting your decision on the following capsule release.
        </p>

        {/* Capsule info */}
        <div className="gv-info-box">
          <div className="gv-info-row">
            <span className="gv-label">Capsule</span>
            <span className="gv-value">{info?.capsule_title}</span>
          </div>
          <div className="gv-info-row">
            <span className="gv-label">Requested by</span>
            <span className="gv-value">{info?.owner_name}</span>
          </div>
          <div className="gv-info-row">
            <span className="gv-label">Your role</span>
            <span className="gv-value">{info?.guardian_relation || 'Guardian'}</span>
          </div>
          <div className="gv-info-row">
            <span className="gv-label">Sent on</span>
            <span className="gv-value">
              {info?.sent_at ? new Date(info.sent_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '—'}
            </span>
          </div>
        </div>

        {/* Decision form */}
        <form onSubmit={handleSubmit} className="gv-form">
          <p className="gv-form-label">Your decision *</p>

          <div className="gv-action-buttons">
            <button
              type="button"
              className={`gv-action-btn gv-action-btn--confirm${action === 'CONFIRM' ? ' selected' : ''}`}
              onClick={() => { setAction('CONFIRM'); setSubmitError(''); }}
              disabled={submitting}
            >
              ✅ Confirm Release
            </button>
            <button
              type="button"
              className={`gv-action-btn gv-action-btn--deny${action === 'DENY' ? ' selected' : ''}`}
              onClick={() => { setAction('DENY'); setSubmitError(''); }}
              disabled={submitting}
            >
              ❌ Deny Release
            </button>
          </div>

          <div className="gv-notes-group">
            <label htmlFor="gv-notes" className="gv-form-label">
              Notes <span className="gv-optional">(optional)</span>
            </label>
            <textarea
              id="gv-notes"
              className="gv-textarea"
              rows={4}
              placeholder="Add any context or explanation for your decision…"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={submitting}
            />
          </div>

          {submitError && <p className="gv-submit-error">{submitError}</p>}

          <button
            type="submit"
            className="gv-submit-btn"
            disabled={submitting || !action}
          >
            {submitting ? 'Submitting…' : 'Submit Decision'}
          </button>
        </form>

        <p className="gv-disclaimer">
          This link is unique to you. Your IP address is logged for audit purposes.
          If you did not expect this email, you can safely ignore this page.
        </p>
      </div>
    </div>
  );
}
