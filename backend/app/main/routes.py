"""
Main Routes

Provides general API endpoints including health checks, test routes,
and admin functionality.
"""

from flask import jsonify, g, request, current_app

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


@main_bp.route('/test-email', methods=['POST'])
@token_required
def test_email():
    """
    Send a test email to verify email configuration.
    
    Requires: Authorization header with Bearer token
    
    Request Body:
        {
            "email": "test@example.com"  (optional, defaults to current user's email)
        }
    
    Returns:
        200: Test email sent successfully
        500: Failed to send email
    """
    from app.services.email_service import send_test_email
    
    data = request.get_json() or {}
    recipient_email = data.get('email', g.current_user.email)
    
    try:
        success = send_test_email(recipient_email)
        
        if success:
            return jsonify({
                'message': 'Test email sent successfully',
                'recipient': recipient_email
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send email',
                'message': 'Check your email configuration'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Test email error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500


@main_bp.route('/delivery-stats', methods=['GET'])
@token_required
def delivery_stats():
    """
    Get capsule delivery statistics.
    
    Requires: Authorization header with Bearer token
    
    Returns:
        200: Delivery statistics
    """
    from app.services.scheduler_service import get_delivery_stats
    
    try:
        stats = get_delivery_stats()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Delivery stats error: {e}")
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500
