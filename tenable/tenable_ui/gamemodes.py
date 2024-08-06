from flask import render_template, request, session, current_app, jsonify

from tenable_ui.games_map import challenges, get_daily_challenge
from tenable_ui.routes import game_bp
from tenable_ui.game import game


@game_bp.route('/daily_challenge', methods=['GET'])
def daily_challenge():
    dc = get_daily_challenge()
    # go to game using dc as game_name


@game_bp.route('/past_challenges', methods=['GET'])
def past_challenges():

    premier_league = [name for name in challenges if challenges[name]['league'] == 'Premier League']

    return render_template(
        '/tenable_ui/other_games.html',
        premier_league=premier_league
    )