import tenable_ui.client as q


def golden_boot_winners():
    response = q.get_golden_boot_winners()
    answers = [d['player_name'] for d in response]

    return response, answers


def ten_goals_and_assists_in_a_season():
    response = q.get_goals_and_assists(10, 10)
    answers = [d['player_name'] for d in response]

    return response, answers


def total_goals_by_nation():
    response = q.get_goals_by_nation()
    answers = [d['country'] for d in response[:10]]

    return response, answers


def total_goals_by_team():
    response = q.get_goals_by_team()
    answers = [d['team'] for d in response[:10]]
    return response, answers
