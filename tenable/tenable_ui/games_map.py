import tenable_ui.games as games


# Dict of available games
# key: value --> name: api function

PL_games = {
    'Premier League Golden Boot Winners': {
        'func': games.golden_boot_winners,
        'desc': '',
        },
    'Over 10 Goals and Assists in a Season': {
        'func': games.ten_goals_and_assists_in_a_season,
        'desc': '',
        },
    'Top 10 Highest Goalscorer by Player Nationality': {
        'func': games.total_goals_by_nation, 
        'desc': '',
        },
}