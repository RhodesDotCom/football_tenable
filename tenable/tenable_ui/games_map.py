from flask import current_app
from datetime import datetime, timezone
import json
import random

import tenable_ui.games as games

# Dict of available games
# key: value --> name: api function

# 'Game Name': {
#     'category': 'column_name_of_answers',
#     'desc': '',
#     'difficulty': 1-5,
#     'func': games.function,
#     'league': 'football league',
#     }


def get_daily_challenge():
    try:
        with open('tenable_ui/past_challenges.json', 'r') as f:
            past_challenges = json.load(f)
        
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if current_date in past_challenges:
            todays_challenge = past_challenges[current_date]
        else:
            todays_challenge = random.choice(list(challenges.keys()))
            past_challenges[current_date] = todays_challenge
            with open('tenable_ui/past_challenges.json', 'w') as f:
                json.dump(past_challenges, f)
        return todays_challenge
    except Exception as e:
        current_app.logger.error(f"Error getting daily challenge: {e}")


challenges = {
    'Premier League Golden Boot Winners': {
        'category': 'player_name',
        'desc': '',
        'difficulty': 2,
        'func': games.golden_boot_winners,
        'league': 'Premier League',
        },
    'Over 10 Goals and Assists in a Season': {
        'category': 'player_name',
        'desc': '',
        'difficulty': 3,
        'func': games.ten_goals_and_assists_in_a_season,
        'league': 'Premier League',
        },
    'Top 10 Most Goals by Country': {
        'category': 'country',
        'desc': 'Can you guess which counties have the most premier league goals by players from their country?',
        'difficulty': 3,
        'func': games.total_goals_by_nation,
        'league': 'Premier League',
        },
    'Most Premier League Goals by Team': {
        'category': 'team',
        'desc': 'Can you guess which team has the most Premier League goals?',
        'difficulty': 1,
        'func': games.total_goals_by_team,
        'league': 'Premier League',
    },
    'Team Top Goalscorer Each Season': {
        'category': 'player_name',
        'desc': 'Can you guess which player finished the season as their teams highest goalscorer?',
        'difficulty': 1,
        'func': games.team_topscorers_by_season,
        'league': 'Premier League',
    },
    'Team''s Top Goalscorer Each Season But Not The Golden Boot': {
        'category': 'player_name',
        'desc': 'Can you guess which player finished the season as their teams highest goalscore but didn''t win the Golden Boot?',
        'difficulty': 2,
        'func': games.team_topscorers_without_golden_boot,
        'league': 'Premier League',
    },
}