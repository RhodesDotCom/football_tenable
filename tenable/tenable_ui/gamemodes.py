from flask import render_template, request, url_for, current_app
from datetime import datetime, timezone
import json
import random

from tenable_ui.challenges.all_challenges import challenges
from tenable_ui.routes import game_bp
from tenable_ui.game import game_start, game_guess

def main():
    game_bp.add_url_rule('/daily_challenge', view_func=daily_challenge, methods=['GET', 'POST'])
    game_bp.add_url_rule('/past_challenges', view_func=past_challenges, methods=['GET'])


def daily_challenge():
    if request.method == 'GET':
        game_info = get_daily_challenge()
        return game_start(game_info=game_info, origin=url_for('game_bp.daily_challenge'))
    elif request.method == 'POST':
        guess = request.form.get('guess')
        return game_guess(guess, origin=url_for('game_bp.daily_challenge'))


def get_daily_challenge() -> dict:
    try:
        with open('tenable_ui/challenges/past_challenges.json', 'r') as f:
            past_challenges = json.load(f)
        
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if current_date in past_challenges:
            todays_challenge = past_challenges[current_date]
        else:
            todays_challenge = random.choice(list(challenges.keys()))
            past_challenges[current_date] = todays_challenge
            with open('tenable_ui/past_challenges.json', 'w') as f:
                json.dump(past_challenges, f)
        return challenges[todays_challenge]
    except Exception as e:
        current_app.logger.error(f"Error getting daily challenge: {e}")


def past_challenges():


    premier_league = [name for name in challenges if challenges[name]['league'] == 'Premier League']

    return render_template(
        '/tenable_ui/other_games.html',
        premier_league=premier_league
    )


