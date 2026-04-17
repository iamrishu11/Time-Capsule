"""
JWT Authentication Utilities

Provides decorators and helper functions for JWT-based authentication.
"""

import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, current_app, g

from app.models import User


def generate_token(user):
    """
    Generate a JWT access token for the given user.
    
    Args:
        user: User model instance
        
    Returns:
        JWT token string
    """
    payload = {
        'sub': user.id,  # Subject (user ID)
        'email': user.email,
        'name': user.name,
        'role': user.role,
        'iat': datetime.utcnow(),  # Issued at
        'exp': datetime.utcnow() + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def decode_token(token):
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    payload = jwt.decode(
        token,
        current_app.config['JWT_SECRET_KEY'],
        algorithms=['HS256']
    )
    
    return payload


def generate_attachment_token(attachment_id, capsule_id, expires=None):
    """
    Generate a signed token for public attachment access.
    """
    if expires is None:
        expires = current_app.config.get('ATTACHMENT_TOKEN_EXPIRES', timedelta(days=7))

    payload = {
        'type': 'attachment',
        'attachment_id': attachment_id,
        'capsule_id': capsule_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expires,
    }

    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

    return token


def decode_attachment_token(token):
    """
    Decode and verify a signed attachment access token.
    """
    payload = decode_token(token)
    if payload.get('type') != 'attachment':
        raise jwt.InvalidTokenError('Invalid attachment token type')
    return payload


def token_required(f):
    """
    Decorator to protect routes with JWT authentication.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route():
            user = g.current_user
            return jsonify({'message': f'Hello, {user.name}'})
    
    The authenticated user is available via `g.current_user`.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            # Expected format: "Bearer <token>"
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Missing or invalid Authorization header'
            }), 401
        
        try:
            # Decode the token
            payload = decode_token(token)
            user_id = payload.get('sub')
            
            if not user_id:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'Token payload is missing user ID'
                }), 401
            
            # Load the user from database
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    'error': 'User not found',
                    'message': 'The user associated with this token no longer exists'
                }), 401
            
            # Attach user to Flask's g object for access in the view
            g.current_user = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token expired',
                'message': 'Your session has expired. Please log in again.'
            }), 401
        except jwt.InvalidTokenError as e:
            return jsonify({
                'error': 'Invalid token',
                'message': str(e)
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated
