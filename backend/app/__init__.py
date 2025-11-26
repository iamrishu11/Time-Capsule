"""
Time Capsule Backend Application Factory

This module creates and configures the Flask application using the
application factory pattern for better modularity and testing.
"""

import os
from flask import Flask
from flask_cors import CORS

from app.config import DevelopmentConfig
from app.extensions import db, migrate


def create_app(config_class=DevelopmentConfig):
    """
    Application factory function.
    
    Args:
        config_class: Configuration class to use (default: DevelopmentConfig)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure file uploads
    upload_folder = os.environ.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(app.root_path, '..', upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
    
    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS for frontend development servers
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.recipients import recipients_bp
    from app.capsules import capsules_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(recipients_bp, url_prefix='/api/recipients')
    app.register_blueprint(capsules_bp, url_prefix='/api/capsules')
    
    # Shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': __import__('app.models', fromlist=['User']).User,
        }
    
    return app
