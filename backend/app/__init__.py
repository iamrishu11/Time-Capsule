"""
Time Capsule Backend Application Factory

This module creates and configures the Flask application using the
application factory pattern for better modularity and testing.
"""

import os
import atexit
from flask import Flask
from flask_cors import CORS

from app.config import DevelopmentConfig
from app.extensions import db, migrate, mail

# Global scheduler instance
scheduler = None


def create_app(config_class=DevelopmentConfig):
    """
    Application factory function.
    
    Args:
        config_class: Configuration class to use (default: DevelopmentConfig)
    
    Returns:
        Configured Flask application instance
    """
    global scheduler
    
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
    mail.init_app(app)
    
    # Get allowed origins from config
    frontend_urls = app.config.get('FRONTEND_URLS', 'http://localhost:3000,http://localhost:5173')
    allowed_origins = [url.strip() for url in frontend_urls.split(',')]
    
    # Enable CORS for frontend development and production servers
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
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
    from app.guardians import guardians_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(recipients_bp, url_prefix='/api/recipients')
    app.register_blueprint(capsules_bp, url_prefix='/api/capsules')
    app.register_blueprint(guardians_bp, url_prefix='/api/guardian')
    
    # Shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': __import__('app.models', fromlist=['User']).User,
        }
    
    # Initialize APScheduler for automatic capsule delivery
    if app.config.get('SCHEDULER_ENABLED', True) and os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            
            scheduler = BackgroundScheduler()
            
            def check_scheduled_capsules():
                """Background job to process due capsules."""
                with app.app_context():
                    from app.services.scheduler_service import process_scheduled_capsules
                    result = process_scheduled_capsules()
                    if result['processed'] > 0:
                        app.logger.info(f"Scheduler processed {result['processed']} capsules: {result['delivered']} delivered, {result['failed']} failed")
            
            # Run every minute
            scheduler.add_job(
                func=check_scheduled_capsules,
                trigger='interval',
                minutes=1,
                id='capsule_delivery_job',
                replace_existing=True
            )
            scheduler.start()
            app.logger.info("APScheduler started - checking for due capsules every minute")
            
            # Shutdown scheduler when app exits
            atexit.register(lambda: scheduler.shutdown())
            
        except ImportError:
            app.logger.warning("APScheduler not installed - automatic delivery disabled")
        except Exception as e:
            app.logger.error(f"Failed to start scheduler: {e}")
    
    return app
