from flask import render_template, request, session, current_app, jsonify

from tenable_ui.routes import game_bp


@game_bp.route('/others', methods=['GET'])
def menu():

    games = ['test 1', 'test 2', 'test 3']


    return render_template(
        '/tenable_ui/other_games.html',
        games=games
    )