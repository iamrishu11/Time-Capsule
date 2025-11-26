"""
Main Routes

Provides general API endpoints including health checks and test routes.
"""

from flask import jsonify, g

from app.main import main_bp
from app.auth.utils import token_required


@main_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        200: Service is healthy
    """
    return jsonify({
        'status': 'ok',
        'message': 'Time Capsule API is running'
    }), 200


@main_bp.route('/protected-test', methods=['GET'])
@token_required
def protected_test():
    """
    Test endpoint for verifying JWT authentication.
    
    Requires: Authorization header with Bearer token
    
    Returns:
        200: Authentication successful
        401: Not authenticated
    """
    user = g.current_user
    
    return jsonify({
        'message': 'You are authorized',
        'user_id': user.id,
        'user_name': user.name
    }), 200
