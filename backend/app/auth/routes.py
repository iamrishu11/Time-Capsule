"""
Authentication Routes

Provides endpoints for user registration, login, and session management.
Uses JWT tokens for stateless authentication suitable for SPA clients.
"""

from flask import request, jsonify, g

from app.auth import auth_bp
from app.auth.utils import generate_token, token_required
from app.auth.schemas import validate_registration, validate_login
from app.extensions import db
from app.models import User


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Request Body:
        {
            "name": "User's Full Name",
            "email": "user@example.com",
            "password": "securepassword"
        }
    
    Returns:
        201: User registered successfully with access token
        400: Validation error
        409: Email already registered
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Bad request',
            'message': 'Request body must be JSON'
        }), 400
    
    # Validate request data
    is_valid, error_message = validate_registration(data)
    if not is_valid:
        return jsonify({
            'error': 'Validation error',
            'message': error_message
        }), 400
    
    name = data['name'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            'error': 'Conflict',
            'message': 'An account with this email already exists'
        }), 409
    
    # Create new user
    user = User(
        name=name,
        email=email,
        role='user'
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Generate token for immediate login after registration
        access_token = generate_token(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Server error',
            'message': 'An error occurred while creating the account'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token.
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "securepassword"
        }
    
    Returns:
        200: Login successful with access token and user info
        400: Validation error
        401: Invalid credentials
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Bad request',
            'message': 'Request body must be JSON'
        }), 400
    
    # Validate request data
    is_valid, error_message = validate_login(data)
    if not is_valid:
        return jsonify({
            'error': 'Validation error',
            'message': error_message
        }), 400
    
    email = data['email'].strip().lower()
    password = data['password']
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    # Verify password (using constant-time comparison in check_password)
    if not user or not user.check_password(password):
        return jsonify({
            'error': 'Authentication failed',
            'message': 'Invalid email or password'
        }), 401
    
    # Generate JWT token
    access_token = generate_token(user)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Get the current authenticated user's information.
    
    Requires: Authorization header with Bearer token
    
    Returns:
        200: Current user information
        401: Not authenticated or invalid token
    """
    user = g.current_user
    
    return jsonify({
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token():
    """
    Refresh the JWT access token.
    
    Requires: Authorization header with Bearer token
    
    Returns:
        200: New access token
        401: Not authenticated or invalid token
    """
    user = g.current_user
    
    # Generate new token
    access_token = generate_token(user)
    
    return jsonify({
        'message': 'Token refreshed successfully',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200
