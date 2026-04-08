/**
 * VideoRecorder — in-browser video message recorder.
 *
 * Uses the MediaRecorder API to record from the user's camera + mic.
 * Three states: idle → recording → preview.
 *
 * Props:
 *   onVideoReady {function(blob, filename)} — called when user accepts a recording
 *   disabled     {boolean}                 — hides the component when true
 */

import { useState, useRef, useEffect } from 'react';
import './VideoRecorder.css';

const MIME_TYPES = ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm'];

function getSupportedMimeType() {
  return MIME_TYPES.find((t) => MediaRecorder.isTypeSupported(t)) || 'video/webm';
}

export default function VideoRecorder({ onVideoReady, disabled = false }) {
  const [phase, setPhase]         = useState('idle'); // idle | requesting | recording | preview
  const [error, setError]         = useState('');
  const [elapsed, setElapsed]     = useState(0); // seconds
  const [previewUrl, setPreviewUrl] = useState('');

  // Both video elements stay mounted at all times so refs are always valid
  const liveVideoRef = useRef(null);
  const streamRef    = useRef(null);
  const recorderRef  = useRef(null);
  const chunksRef    = useRef([]);
  const timerRef     = useRef(null);
  const blobRef      = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStream();
      clearInterval(timerRef.current);
    };
  }, []);

  function stopStream() {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }

  async function startRecording() {
    setError('');
    setPhase('requesting');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      streamRef.current = stream;

      // liveVideoRef is always mounted, so this is safe to call immediately
      const lv = liveVideoRef.current;
      lv.srcObject = stream;
      lv.muted = true;
      await lv.play().catch(() => {}); // ignore autoplay errors

      const mimeType = getSupportedMimeType();
      const recorder = new MediaRecorder(stream, { mimeType });
      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        blobRef.current = blob;
        // Use state so the preview <video src={}> gets the URL after React re-renders
        const url = URL.createObjectURL(blob);
        setPreviewUrl(url);
        stopStream();
        setPhase('preview');
      };

      recorder.start(250); // collect chunks every 250 ms
      setPhase('recording');
      setElapsed(0);
      timerRef.current = setInterval(() => setElapsed((s) => s + 1), 1000);
    } catch (err) {
      setPhase('idle');
      if (err.name === 'NotAllowedError') {
        setError('Camera/microphone access was denied. Please allow access and try again.');
      } else if (err.name === 'NotFoundError') {
        setError('No camera or microphone found on this device.');
      } else {
        setError(`Could not start recording: ${err.message}`);
      }
    }
  }

  function stopRecording() {
    clearInterval(timerRef.current);
    recorderRef.current?.stop();
    // phase → 'preview' set in onstop
  }

  function discardRecording() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl('');
    }
    blobRef.current = null;
    setElapsed(0);
    setError('');
    setPhase('idle');
  }

  function acceptRecording() {
    if (!blobRef.current) return;
    const ext = blobRef.current.type.includes('mp4') ? 'mp4' : 'webm';
    const filename = `video-message-${Date.now()}.${ext}`;
    onVideoReady(blobRef.current, filename);
    discardRecording();
  }

  function formatTime(s) {
    const m = String(Math.floor(s / 60)).padStart(2, '0');
    const sec = String(s % 60).padStart(2, '0');
    return `${m}:${sec}`;
  }

  if (disabled) return null;

  return (
    <div className="vr-wrapper">
      <div className="vr-header">
        <span className="vr-icon">🎥</span>
        <span className="vr-title">Video Message</span>
      </div>

      {error && <p className="vr-error">{error}</p>}

      {/* ── IDLE ── */}
      {phase === 'idle' && (
        <div className="vr-idle">
          <p className="vr-hint">Record a personal video message to attach to this capsule.</p>
          <button type="button" className="vr-btn vr-btn--start" onClick={startRecording}>
            Start Recording
          </button>
        </div>
      )}

      {/* ── REQUESTING ── */}
      {phase === 'requesting' && (
        <div className="vr-idle">
          <p className="vr-hint">Requesting camera access…</p>
        </div>
      )}

      {/*
        Live video — always in the DOM so liveVideoRef is never null.
        Hidden unless we are actively recording.
      */}
      <div className="vr-recording" style={{ display: phase === 'recording' ? 'flex' : 'none' }}>
        <div className="vr-live-container">
          <video ref={liveVideoRef} className="vr-video" playsInline muted />
          <div className="vr-rec-badge">
            <span className="vr-dot" /> REC {formatTime(elapsed)}
          </div>
        </div>
        <button type="button" className="vr-btn vr-btn--stop" onClick={stopRecording}>
          Stop Recording
        </button>
      </div>

      {/* ── PREVIEW ── */}
      {phase === 'preview' && (
        <div className="vr-preview">
          {/* src driven by state — valid by the time this renders */}
          <video src={previewUrl} className="vr-video" controls playsInline />
          <p className="vr-hint vr-hint--center">
            Duration: {formatTime(elapsed)} &nbsp;|&nbsp; Review your recording above.
          </p>
          <div className="vr-preview-actions">
            <button type="button" className="vr-btn vr-btn--discard" onClick={discardRecording}>
              Record Again
            </button>
            <button type="button" className="vr-btn vr-btn--accept" onClick={acceptRecording}>
              Attach This Recording
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
