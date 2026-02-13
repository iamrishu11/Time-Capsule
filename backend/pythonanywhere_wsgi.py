"""
PythonAnywhere WSGI Configuration File

This file is used by PythonAnywhere to serve the Flask application.
Replace 'YOUR_USERNAME' with your actual PythonAnywhere username.

Instructions:
1. Copy this content to your PythonAnywhere WSGI configuration file at:
   /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py
2. Update the paths to match your project location
3. Reload your web app from the PythonAnywhere dashboard
"""

import sys
import os

# Add your project directory to the sys.path
# Replace 'YOUR_USERNAME' with your actual username
project_home = '/home/YOUR_USERNAME/time-capsule/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
dotenv_path = os.path.join(project_home, '.env.production')
load_dotenv(dotenv_path)

# Import the Flask application factory and create the app
from app import create_app
from app.config import ProductionConfig

application = create_app(ProductionConfig)
