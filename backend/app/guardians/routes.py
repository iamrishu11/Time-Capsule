"""
Guardian Verification Portal Routes

Public, token-authenticated endpoints that allow guardians to confirm or deny
event-based capsule releases. No user login is required — guardians authenticate
solely via the unique token embedded in their verification email link.

Endpoints:
    GET  /api/guardian/verify/<token>         — Fetch request details (guardian landing page)
    POST /api/guardian/verify/<token>/respond — Submit confirm/deny decision
"""

from datetime import datetime

from flask import request, jsonify, current_app

from app.guardians import guardians_bp
from app.extensions import db
from app.models import GuardianVerificationRequest


@guardians_bp.route('/verify/<string:token>', methods=['GET'])
def get_verification_request(token):
    """
    Return the verification request associated with a token.

    Used by the frontend GuardianVerify page to render the appropriate
    capsule information before the guardian submits a decision.

    Returns:
        200 — request details (guardian name, owner name, capsule title, status)
        404 — token not found
        410 — token has expired
    """
    req = GuardianVerificationRequest.query.filter_by(token=token).first()

    if not req:
        return jsonify({'error': 'Invalid or expired verification link'}), 404

    if req.status == 'EXPIRED':
        return jsonify({
            'error': 'This verification link has expired.',
            'status': 'EXPIRED'
        }), 410

    # If already responded, show the recorded decision
    if req.status in ('CONFIRMED', 'DENIED'):
        return jsonify({
            'status': req.status,
            'already_responded': True,
            'responded_at': req.responded_at.isoformat() if req.responded_at else None,
            'response_notes': req.response_notes,
            'guardian_name': req.guardian.name,
            'owner_name': req.capsule.owner.name,
            'capsule_title': req.capsule.title,
        }), 200

    return jsonify({
        'status': req.status,
        'already_responded': False,
        'guardian_name': req.guardian.name,
        'guardian_relation': req.guardian.relation,
        'owner_name': req.capsule.owner.name,
        'capsule_title': req.capsule.title,
        'sent_at': req.sent_at.isoformat(),
    }), 200


@guardians_bp.route('/verify/<string:token>/respond', methods=['POST'])
def respond_to_verification(token):
    """
    Submit a guardian's confirm or deny decision.

    Request Body:
        {
            "action": "CONFIRM" | "DENY",
            "notes": "Optional free-text explanation"
        }

    Returns:
        200 — decision recorded successfully
        400 — missing or invalid action
        404 — token not found
        409 — already responded
    """
    req = GuardianVerificationRequest.query.filter_by(token=token).first()

    if not req:
        return jsonify({'error': 'Invalid or expired verification link'}), 404

    if req.status != 'PENDING':
        return jsonify({
            'error': f'This request has already been {req.status.lower()}.',
            'status': req.status
        }), 409

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    action = data.get('action', '').strip().upper()
    notes = data.get('notes', '').strip()

    if action not in ('CONFIRM', 'DENY'):
        return jsonify({'error': 'action must be CONFIRM or DENY'}), 400

    req.status = 'CONFIRMED' if action == 'CONFIRM' else 'DENIED'
    req.responded_at = datetime.utcnow()
    req.response_notes = notes or None
    req.ip_address = request.remote_addr

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to record guardian response for token {token}: {e}")
        return jsonify({'error': 'Failed to record your response. Please try again.'}), 500

    # Notify the capsule owner asynchronously
    try:
        from app.services.email_service import send_guardian_response_notification
        send_guardian_response_notification(req.capsule, req.guardian, req.status, notes)
    except Exception as e:
        current_app.logger.warning(f"Could not send owner notification for guardian response: {e}")

    # If confirmed, check whether all guardians have now confirmed → trigger delivery
    if req.status == 'CONFIRMED':
        try:
            _trigger_if_all_confirmed(req.capsule)
        except Exception as e:
            current_app.logger.error(
                f"Error checking all-confirmed trigger for capsule {req.capsule_id}: {e}"
            )

    return jsonify({
        'message': f'Thank you, {req.guardian.name}. Your response has been recorded.',
        'status': req.status,
    }), 200


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _trigger_if_all_confirmed(capsule):
    """
    If every GuardianVerificationRequest for this capsule is CONFIRMED,
    immediately trigger capsule delivery via the scheduler service.
    """
    all_requests = GuardianVerificationRequest.query.filter_by(
        capsule_id=capsule.id
    ).all()

    if not all_requests:
        return

    if all(r.status == 'CONFIRMED' for r in all_requests):
        current_app.logger.info(
            f"All guardians confirmed for capsule {capsule.id} — triggering delivery."
        )
        from app.services.scheduler_service import deliver_capsule_now
        deliver_capsule_now(capsule.id)
