"""
Configuration classes for the Time Capsule application.

Uses python-dotenv to load environment variables from .env file.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseConfig:
    """Base configuration with common settings."""
    
    # Flask secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Token expires in 24 hours
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql+psycopg2://postgres:password@localhost:5432/timecapsule_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SSL Mode for Azure PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'sslmode': 'require'
        }
    } if 'azure' in os.environ.get('DATABASE_URL', '').lower() else {}
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'
    FRONTEND_URLS = os.environ.get('FRONTEND_URLS', 'http://localhost:3000,http://localhost:5173')
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_USERNAME'))
    MAIL_SENDER_NAME = os.environ.get('MAIL_SENDER_NAME', 'Time Capsule')


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries in development


class ProductionConfig(BaseConfig):
    """Production configuration."""
    
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # In production, ensure these are set via environment variables
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY must be set in production")
        return key
    
    @property
    def JWT_SECRET_KEY(self):
        key = os.environ.get('JWT_SECRET_KEY')
        if not key:
            raise ValueError("JWT_SECRET_KEY must be set in production")
        return key


class TestingConfig(BaseConfig):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
