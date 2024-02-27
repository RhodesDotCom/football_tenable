from flask import Blueprint


query_bp = Blueprint(
    'query_bp', __name__,
)

from query import api