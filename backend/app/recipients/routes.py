"""
Recipients API Routes

Provides CRUD endpoints for managing recipients.
Recipients are people who will receive capsules from the current user.
"""

from flask import request, jsonify, g

from app.recipients import recipients_bp
from app.auth.utils import token_required
from app.extensions import db
from app.models import Recipient


@recipients_bp.route('', methods=['POST'])
@token_required
def create_recipient():
    """
    Create a new recipient for the current user.
    
    Request Body:
        {
            "name": "Alice",
            "email": "alice@example.com",
            "relation": "daughter"  (optional)
        }
    
    Returns:
        201: Recipient created successfully
        400: Validation error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Bad request',
            'message': 'Request body must be JSON'
        }), 400
    
    # Validate required fields
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    relation = data.get('relation', '').strip() or None
    
    if not name:
        return jsonify({
            'error': 'Validation error',
            'message': 'Name is required'
        }), 400
    
    if not email:
        return jsonify({
            'error': 'Validation error',
            'message': 'Email is required'
        }), 400
    
    # Create recipient
    recipient = Recipient(
        owner_id=g.current_user.id,
        name=name,
        email=email,
        relation=relation
    )
    
    try:
        db.session.add(recipient)
        db.session.commit()
        
        return jsonify(recipient.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to create recipient'
        }), 500


@recipients_bp.route('', methods=['GET'])
@token_required
def get_recipients():
    """
    Get all recipients for the current user.
    
    Returns:
        200: List of recipients
    """
    recipients = Recipient.query.filter_by(
        owner_id=g.current_user.id
    ).order_by(Recipient.created_at.desc()).all()
    
    return jsonify([r.to_dict() for r in recipients]), 200


@recipients_bp.route('/<int:recipient_id>', methods=['GET'])
@token_required
def get_recipient(recipient_id):
    """
    Get a specific recipient by ID.
    
    Returns:
        200: Recipient data
        403: Not authorized
        404: Recipient not found
    """
    recipient = Recipient.query.get(recipient_id)
    
    if not recipient:
        return jsonify({
            'error': 'Not found',
            'message': 'Recipient not found'
        }), 404
    
    # Check ownership
    if recipient.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this recipient'
        }), 403
    
    return jsonify(recipient.to_dict()), 200


@recipients_bp.route('/<int:recipient_id>', methods=['PUT'])
@token_required
def update_recipient(recipient_id):
    """
    Update a recipient.
    
    Request Body:
        {
            "name": "Alice Smith",
            "email": "alice.smith@example.com",
            "relation": "daughter"
        }
    
    Returns:
        200: Recipient updated successfully
        400: Validation error
        403: Not authorized
        404: Recipient not found
    """
    recipient = Recipient.query.get(recipient_id)
    
    if not recipient:
        return jsonify({
            'error': 'Not found',
            'message': 'Recipient not found'
        }), 404
    
    # Check ownership
    if recipient.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this recipient'
        }), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Bad request',
            'message': 'Request body must be JSON'
        }), 400
    
    # Update fields if provided
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return jsonify({
                'error': 'Validation error',
                'message': 'Name cannot be empty'
            }), 400
        recipient.name = name
    
    if 'email' in data:
        email = data['email'].strip().lower()
        if not email:
            return jsonify({
                'error': 'Validation error',
                'message': 'Email cannot be empty'
            }), 400
        recipient.email = email
    
    if 'relation' in data:
        recipient.relation = data['relation'].strip() or None
    
    try:
        db.session.commit()
        return jsonify(recipient.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to update recipient'
        }), 500


@recipients_bp.route('/<int:recipient_id>', methods=['DELETE'])
@token_required
def delete_recipient(recipient_id):
    """
    Delete a recipient.
    
    Returns:
        200: Recipient deleted successfully
        403: Not authorized
        404: Recipient not found
    """
    recipient = Recipient.query.get(recipient_id)
    
    if not recipient:
        return jsonify({
            'error': 'Not found',
            'message': 'Recipient not found'
        }), 404
    
    # Check ownership
    if recipient.owner_id != g.current_user.id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have access to this recipient'
        }), 403
    
    try:
        db.session.delete(recipient)
        db.session.commit()
        
        return jsonify({
            'message': 'Recipient deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to delete recipient'
        }), 500
