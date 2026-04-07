"""
Capsules API Routes

Provides CRUD endpoints for managing time capsules.
Capsule messages are encrypted before storage and decrypted on retrieval.
"""

import os
from datetime import datetime
from flask import request, jsonify, g, current_app
from werkzeug.utils import secure_filename

from app.capsules import capsules_bp
from app.auth.utils import token_required
from app.extensions import db
from app.models import Capsule, Recipient, CapsuleRecipient, Attachment
from app.security.encryption import encrypt_text, decrypt_text


# Allowed file extensions for attachments
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'mp4', 'mp3', 'wav'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@capsules_bp.route('', methods=['POST'])
@token_required
def create_capsule():
    """
    Create a new time capsule with encrypted message.
    
    Request Body:
        {
            "title": "For your 18th birthday",
            "message": "My dear child...",
            "recipient_ids": [1, 2],
            "release_type": "TIME",
            "release_at": "2035-05-21T00:00:00Z",
            "requires_guardian": false
        }
    
    Returns:
        201: Capsule created successfully
        400: Validation error
        403: Invalid recipients
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Bad request',
            'message': 'Request body must be JSON'
        }), 400
    
    # Validate required fields
    title = data.get('title', '').strip()
    message = data.get('message', '').strip()
    recipient_ids = data.get('recipient_ids', [])
    release_type = data.get('release_type', 'TIME').upper()
    release_at_str = data.get('release_at')
    requires_guardian = data.get('requires_guardian', False)
    
    errors = []
    
    if not title:
        errors.append('Title is required')
    
    if not message:
        errors.append('Message is required')
    
    if not recipient_ids:
        errors.append('At least one recipient is required')
    
    if release_type not in ['TIME', 'EVENT']:
        errors.append('Release type must be TIME or EVENT')
    
    # Parse release date for TIME-based capsules
    release_at = None
    if release_type == 'TIME':
        if not release_at_str:
            errors.append('Release date is required for TIME-based capsules')
        else:
            try:
                # Parse ISO format datetime
                release_at = datetime.fromisoformat(release_at_str.replace('Z', '+00:00'))
                
                # Check if date is in the future
                if release_at <= datetime.now(release_at.tzinfo):
                    errors.append('Release date must be in the future')
            except ValueError:
                errors.append('Invalid release date format. Use ISO format.')
    
    if errors:
        return jsonify({
            'error': 'Validation error',
            'message': errors[0],
            'errors': errors
        }), 400
    
    # Verify all recipients belong to current user
    valid_recipients = Recipient.query.filter(
        Recipient.id.in_(recipient_ids),
        Recipient.owner_id == g.current_user.id
    ).all()
    
    if len(valid_recipients) != len(recipient_ids):
        return jsonify({
            'error': 'Forbidden',
            'message': 'One or more recipients are invalid or do not belong to you'
        }), 403
    
    # ============================================================
    # ENCRYPTION: Encrypt the message before storing in database
    # This ensures the message is never stored in plaintext
    # ============================================================
    encrypted_message = encrypt_text(message)
    
    # Create capsule
    capsule = Capsule(
        owner_id=g.current_user.id,
        title=title,
        message_encrypted=encrypted_message,
        release_type=release_type,
        release_at=release_at,
        requires_guardian=requires_guardian,
        status='SCHEDULED' if release_at else 'DRAFT'
    )
    
    try:
        db.session.add(capsule)
        db.session.flush()  # Get capsule ID
        
        # Create CapsuleRecipient relationships
        for recipient in valid_recipients:
            capsule_recipient = CapsuleRecipient(
                capsule_id=capsule.id,
                recipient_id=recipient.id
            )
            db.session.add(capsule_recipient)
        
        db.session.commit()
        
        return jsonify({
            'id': capsule.id,
            'title': capsule.title,
            'release_type': capsule.release_type,
            'release_at': capsule.release_at.isoformat() if capsule.release_at else None,
            'status': capsule.status,
            'requires_guardian': capsule.requires_guardian,
            'recipient_ids': recipient_ids,
            'message': 'Capsule created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to create capsule: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to create capsule'
        }), 500


@capsules_bp.route('', methods=['GET'])
@token_required
def get_capsules():
    """
    Get all capsules for the current user (summary view).
    
    Messages are NOT decrypted in this endpoint for performance and security.
    
    Returns:
        200: List of capsules with recipients
    """
    capsules = Capsule.query.filter_by(
        owner_id=g.current_user.id
    ).order_by(Capsule.created_at.desc()).all()
    
    result = []
    for capsule in capsules:
        # Get recipients for this capsule
        recipients = []
        for cr in capsule.recipients:
            recipients.append({
                'id': cr.recipient.id,
                'name': cr.recipient.name,
                'email': cr.recipient.email
            })
        
        result.append({
            'id': capsule.id,
            'title': capsule.title,
            'status': capsule.status,
            'release_type': capsule.release_type,
            'release_at': capsule.release_at.isoformat() if capsule.release_at else None,
            'requires_guardian': capsule.requires_guardian,
            'recipients': recipients,
            'created_at': capsule.created_at.isoformat()
        })
    
    return jsonify(result), 200


@capsules_bp.route('/<int:capsule_id>', methods=['GET'])
@token_required
def get_capsule(capsule_id):
    """
    Get a single capsule with decrypted message.
    
    Returns:
        200: Capsule with decrypted message, recipients, and attachments
        403: Not authorized
        404: Capsule not found
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({
            'error': 'Not found',
            'message': 'Capsule not found'
        }), 404
    
    # Check ownership
    if capsule.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this capsule'
        }), 403
    
    # ============================================================
    # DECRYPTION: Decrypt the message for viewing
    # Only the capsule owner can see the decrypted content
    # ============================================================
    try:
        decrypted_message = decrypt_text(capsule.message_encrypted)
    except ValueError as e:
        decrypted_message = "[Error: Could not decrypt message]"
        current_app.logger.error(f"Decryption failed for capsule {capsule_id}: {e}")
    
    # Get recipients
    recipients = []
    for cr in capsule.recipients:
        recipients.append({
            'id': cr.recipient.id,
            'name': cr.recipient.name,
            'email': cr.recipient.email,
            'relation': cr.recipient.relation
        })
    
    # Get attachments
    attachments = []
    for att in capsule.attachments:
        attachments.append({
            'id': att.id,
            'original_filename': att.original_filename,
            'mime_type': att.mime_type,
            'size_bytes': att.size_bytes,
            'created_at': att.created_at.isoformat()
        })
    
    return jsonify({
        'id': capsule.id,
        'title': capsule.title,
        'message': decrypted_message,
        'status': capsule.status,
        'release_type': capsule.release_type,
        'release_at': capsule.release_at.isoformat() if capsule.release_at else None,
        'requires_guardian': capsule.requires_guardian,
        'recipients': recipients,
        'attachments': attachments,
        'created_at': capsule.created_at.isoformat(),
        'updated_at': capsule.updated_at.isoformat()
    }), 200


@capsules_bp.route('/<int:capsule_id>', methods=['PUT'])
@token_required
def update_capsule(capsule_id):
    """
    Update a capsule.
    
    Only DRAFT and SCHEDULED capsules can be updated.
    
    Returns:
        200: Capsule updated successfully
        400: Validation error
        403: Not authorized or capsule already sent
        404: Capsule not found
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({
            'error': 'Not found',
            'message': 'Capsule not found'
        }), 404
    
    # Check ownership
    if capsule.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this capsule'
        }), 403
    
    # Check if capsule can be edited
    if capsule.status in ['SENT', 'CANCELLED']:
        return jsonify({
            'error': 'Forbidden',
            'message': f'Cannot edit a capsule with status: {capsule.status}'
        }), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Bad request',
            'message': 'Request body must be JSON'
        }), 400
    
    # Update title if provided
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({
                'error': 'Validation error',
                'message': 'Title cannot be empty'
            }), 400
        capsule.title = title
    
    # Update message if provided (re-encrypt)
    if 'message' in data:
        message = data['message'].strip()
        if not message:
            return jsonify({
                'error': 'Validation error',
                'message': 'Message cannot be empty'
            }), 400
        # ============================================================
        # ENCRYPTION: Re-encrypt the updated message
        # ============================================================
        capsule.message_encrypted = encrypt_text(message)
    
    # Update release type and date
    if 'release_type' in data:
        release_type = data['release_type'].upper()
        if release_type not in ['TIME', 'EVENT']:
            return jsonify({
                'error': 'Validation error',
                'message': 'Release type must be TIME or EVENT'
            }), 400
        capsule.release_type = release_type
    
    if 'release_at' in data:
        release_at_str = data['release_at']
        if release_at_str:
            try:
                release_at = datetime.fromisoformat(release_at_str.replace('Z', '+00:00'))
                if release_at <= datetime.now(release_at.tzinfo):
                    return jsonify({
                        'error': 'Validation error',
                        'message': 'Release date must be in the future'
                    }), 400
                capsule.release_at = release_at
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid release date format'
                }), 400
        else:
            capsule.release_at = None
    
    if 'requires_guardian' in data:
        capsule.requires_guardian = bool(data['requires_guardian'])
    
    # Update recipients if provided
    if 'recipient_ids' in data:
        recipient_ids = data['recipient_ids']
        
        if not recipient_ids:
            return jsonify({
                'error': 'Validation error',
                'message': 'At least one recipient is required'
            }), 400
        
        # Verify recipients belong to current user
        valid_recipients = Recipient.query.filter(
            Recipient.id.in_(recipient_ids),
            Recipient.owner_id == g.current_user.id
        ).all()
        
        if len(valid_recipients) != len(recipient_ids):
            return jsonify({
                'error': 'Forbidden',
                'message': 'One or more recipients are invalid'
            }), 403
        
        # Remove existing relationships
        CapsuleRecipient.query.filter_by(capsule_id=capsule.id).delete()
        
        # Add new relationships
        for recipient in valid_recipients:
            capsule_recipient = CapsuleRecipient(
                capsule_id=capsule.id,
                recipient_id=recipient.id
            )
            db.session.add(capsule_recipient)
    
    # Update status based on release info
    if capsule.release_at and capsule.status == 'DRAFT':
        capsule.status = 'SCHEDULED'
    
    try:
        db.session.commit()
        
        # Get updated recipients
        recipients = []
        for cr in capsule.recipients:
            recipients.append({
                'id': cr.recipient.id,
                'name': cr.recipient.name,
                'email': cr.recipient.email
            })
        
        return jsonify({
            'id': capsule.id,
            'title': capsule.title,
            'status': capsule.status,
            'release_type': capsule.release_type,
            'release_at': capsule.release_at.isoformat() if capsule.release_at else None,
            'requires_guardian': capsule.requires_guardian,
            'recipients': recipients,
            'message': 'Capsule updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update capsule: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to update capsule'
        }), 500


@capsules_bp.route('/<int:capsule_id>', methods=['DELETE'])
@token_required
def delete_capsule(capsule_id):
    """
    Delete (cancel) a capsule.
    
    Uses soft delete by setting status to CANCELLED.
    
    Returns:
        200: Capsule cancelled successfully
        403: Not authorized
        404: Capsule not found
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({
            'error': 'Not found',
            'message': 'Capsule not found'
        }), 404
    
    # Check ownership
    if capsule.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this capsule'
        }), 403
    
    # Soft delete by changing status
    capsule.status = 'CANCELLED'
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Capsule cancelled successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to cancel capsule'
        }), 500


# ============================================================
# ATTACHMENTS ENDPOINTS
# ============================================================

@capsules_bp.route('/<int:capsule_id>/attachments', methods=['POST'])
@token_required
def upload_attachment(capsule_id):
    """
    Upload a file attachment to a capsule.
    
    Expects multipart/form-data with field name 'file'.
    
    Returns:
        201: Attachment uploaded successfully
        400: No file or invalid file
        403: Not authorized
        404: Capsule not found
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({
            'error': 'Not found',
            'message': 'Capsule not found'
        }), 404
    
    # Check ownership
    if capsule.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this capsule'
        }), 403
    
    # Check if capsule can be modified
    if capsule.status in ['SENT', 'CANCELLED']:
        return jsonify({
            'error': 'Forbidden',
            'message': 'Cannot add attachments to a sent or cancelled capsule'
        }), 403
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({
            'error': 'Bad request',
            'message': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'error': 'Bad request',
            'message': 'No file selected'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Bad request',
            'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    # Secure the filename
    original_filename = secure_filename(file.filename)
    
    # Build storage path: uploads/<user_id>/<capsule_id>/
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    user_folder = os.path.join(upload_folder, str(g.current_user.id), str(capsule_id))
    
    # Create directories if they don't exist
    os.makedirs(user_folder, exist_ok=True)
    
    # Add timestamp to filename to avoid conflicts
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{original_filename}"
    storage_path = os.path.join(user_folder, filename)
    
    try:
        # Save file to disk
        file.save(storage_path)
        
        # Get file info
        file_size = os.path.getsize(storage_path)
        mime_type = file.content_type or 'application/octet-stream'
        
        # Create attachment record
        attachment = Attachment(
            capsule_id=capsule_id,
            owner_id=g.current_user.id,
            original_filename=original_filename,
            storage_path=storage_path,
            mime_type=mime_type,
            size_bytes=file_size
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify({
            'id': attachment.id,
            'original_filename': attachment.original_filename,
            'mime_type': attachment.mime_type,
            'size_bytes': attachment.size_bytes,
            'created_at': attachment.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Clean up file if database save failed
        if os.path.exists(storage_path):
            os.remove(storage_path)
        current_app.logger.error(f"Failed to upload attachment: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to upload attachment'
        }), 500


@capsules_bp.route('/<int:capsule_id>/attachments', methods=['GET'])
@token_required
def get_attachments(capsule_id):
    """
    Get all attachments for a capsule.
    
    Returns:
        200: List of attachments
        403: Not authorized
        404: Capsule not found
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({
            'error': 'Not found',
            'message': 'Capsule not found'
        }), 404
    
    # Check ownership
    if capsule.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this capsule'
        }), 403
    
    attachments = []
    for att in capsule.attachments:
        attachments.append({
            'id': att.id,
            'original_filename': att.original_filename,
            'mime_type': att.mime_type,
            'size_bytes': att.size_bytes,
            'created_at': att.created_at.isoformat()
        })
    
    return jsonify(attachments), 200


@capsules_bp.route('/<int:capsule_id>/attachments/<int:attachment_id>', methods=['DELETE'])
@token_required
def delete_attachment(capsule_id, attachment_id):
    """
    Delete an attachment from a capsule.
    
    Returns:
        200: Attachment deleted successfully
        403: Not authorized
        404: Capsule or attachment not found
    """
    capsule = Capsule.query.get(capsule_id)
    
    if not capsule:
        return jsonify({
            'error': 'Not found',
            'message': 'Capsule not found'
        }), 404
    
    # Check ownership
    if capsule.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this capsule'
        }), 403
    
    attachment = Attachment.query.filter_by(
        id=attachment_id,
        capsule_id=capsule_id
    ).first()
    
    if not attachment:
        return jsonify({
            'error': 'Not found',
            'message': 'Attachment not found'
        }), 404
    
    try:
        # Delete file from disk
        if os.path.exists(attachment.storage_path):
            os.remove(attachment.storage_path)
        
        # Delete database record
        db.session.delete(attachment)
        db.session.commit()
        
        return jsonify({
            'message': 'Attachment deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete attachment: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to delete attachment'
        }), 500
