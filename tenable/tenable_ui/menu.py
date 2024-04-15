from flask import render_template, request, session, current_app
from unidecode import unidecode

from tenable_ui.routes import game_bp


def index():
    