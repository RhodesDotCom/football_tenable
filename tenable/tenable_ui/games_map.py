import tenable_ui.games as games


# Dict of available games
# key: value --> name: api function


daily_challenge = {
    'placeholder': {

    }
}


PL_games = {
    'Premier League Golden Boot Winners': {
        'func': games.golden_boot_winners,
        'category': 'player_name',
        'desc': '',
        },
    'Over 10 Goals and Assists in a Season': {
        'func': games.ten_goals_and_assists_in_a_season,
        'category': 'player_name',
        'desc': '',
        },
    'Top 10 Most Goals by Country': {
        'func': games.total_goals_by_nation,
        'category': 'country',
        'desc': 'Can you guess which counties have the most premier league goals by players from their country',
        },
    'Youngest Premier League Goalscorers': {},
    'Most Premier League Goals by Team': {},
}