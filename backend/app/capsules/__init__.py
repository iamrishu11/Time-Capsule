"""
Capsules Blueprint Initialization
"""

from flask import Blueprint

capsules_bp = Blueprint('capsules', __name__)

from app.capsules import routes  # noqa: F401, E402
