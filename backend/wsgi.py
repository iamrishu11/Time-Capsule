"""
WSGI Entry Point

This module creates the Flask application instance for WSGI servers
(like Gunicorn or uWSGI) to use in production.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
