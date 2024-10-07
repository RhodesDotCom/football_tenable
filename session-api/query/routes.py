from flask import Blueprint


session_bp = Blueprint(
    'session_bp', __name__,
)

from query import api