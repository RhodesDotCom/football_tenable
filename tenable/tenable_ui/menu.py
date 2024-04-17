from flask import render_template, request, session, current_app
from unidecode import unidecode

from tenable_ui.routes import game_bp


@game_bp.route('/')
def main_menu():
    return render_template('tenable_ui/menu.html')