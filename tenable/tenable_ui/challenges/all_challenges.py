import tenable_ui.games as games


challenges = {
    'Premier League Golden Boot Winners': {
        'category': 'player_name',
        'desc': '',
        'difficulty': 2,
        'func': games.golden_boot_winners,
        'league': 'Premier League',
        'name': 'Premier League Golden Boot Winners',
        },
    'Over 10 Goals and Assists in a Season': {
        'category': 'player_name',
        'desc': '',
        'difficulty': 3,
        'func': games.ten_goals_and_assists_in_a_season,
        'league': 'Premier League',
        'name': 'Over 10 Goals and Assists in a Season',
        },
    'Top 10 Most Goals by Country': {
        'category': 'country',
        'desc': 'Can you guess which counties have the most premier league goals by players from their country?',
        'difficulty': 3,
        'func': games.total_goals_by_nation,
        'league': 'Premier League',
        'name': 'Top 10 Most Goals by Country',
        },
    'Most Premier League Goals by Team': {
        'category': 'team',
        'desc': 'Can you guess which team has the most Premier League goals?',
        'difficulty': 1,
        'func': games.total_goals_by_team,
        'league': 'Premier League',
        'name': 'Most Premier League Goals by Team',
    },
    'Team Top Goalscorer Each Season': {
        'category': 'player_name',
        'desc': 'Can you guess which player finished the season as their teams highest goalscorer?',
        'difficulty': 1,
        'func': games.team_topscorers_by_season,
        'league': 'Premier League',
        'name': 'Team Top Goalscorer Each Season',
    },
    'Team''s Top Goalscorer Each Season But Not The Golden Boot': {
        'category': 'player_name',
        'desc': 'Can you guess which player finished the season as their teams highest goalscore but didn''t win the Golden Boot?',
        'difficulty': 2,
        'func': games.team_topscorers_without_golden_boot,
        'league': 'Premier League',
        'name': 'Team''s Top Goalscorer Each Season But Not The Golden Boot',
    },
}