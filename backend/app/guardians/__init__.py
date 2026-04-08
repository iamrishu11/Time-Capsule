from flask import Blueprint

guardians_bp = Blueprint('guardians', __name__)

from app.guardians import routes  # noqa: F401, E402
