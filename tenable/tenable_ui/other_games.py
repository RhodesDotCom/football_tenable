from flask import render_template, request, session, current_app, jsonify
from tenable_ui.games_map import PL_games

from tenable_ui.routes import game_bp


@game_bp.route('/others', methods=['GET'])
def menu():

    return render_template(
        '/tenable_ui/other_games.html',
        games=PL_games.keys()
    )