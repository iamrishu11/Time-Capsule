"""
Recipients Blueprint Initialization
"""

from flask import Blueprint

recipients_bp = Blueprint('recipients', __name__)

from app.recipients import routes  # noqa: F401, E402
