from flask import current_app
import requests

from config import Config


config = Config()
url = config.DATA_API_URL


def get_input_list(category='player_names'):
    params = {'category': category}
    response = requests.get(f'{url}/get_inputs', params=params)
    if response.status_code == 200:
        return response.json()
    else:
        current_app.logger.error(f'get_inputs return status code: {response.status_code}')
    

def get_golden_boot_winners():
    response = requests.get(f'{url}/get_golden_boot_winners')
    if response.status_code == 200:
        return response.json()
    else:
        current_app.logger.error(f'get_golden_boot_winners return status code: {response.status_code}')


def get_goals_and_assists(goals=0, assists=0):
    params = {'goals': goals, 'assists': assists}
    response = requests.get(f'{url}/get_goals_and_assists', params = params)
    if response.status_code == 200:
        return response.json()
    else:
        current_app.logger.error(f'get_goals_and_assists return status code: {response.status_code}')


def get_goals_by_nation():
    response = requests.get(f'{url}/get_goals_by_nation')
    if response.status_code == 200:
        return response.json()
    else:
        current_app.logger.error(f'get_goals_by_nation return status code: {response.status_code}')
   

def get_goals_by_team():
    response = requests.get(f'{url}/get_goals_by_team')
    if response.status_code == 200:
        return response.json()
    else:
        current_app.logger.error(f'get_goals_by_team return status code: {response.status_code}')


def get_team_topscorers_by_season():
    response = requests.get(f'{url}/get_team_topscorers_by_season')
    if response.status_code == 200:
        return response.json()
    else:
        current_app.logger.error(f'get_team_topscorers_by_season return status code: {response.status_code}')
    

def get_team_topscorers_without_golden_boot():
    response = requests.get(f'{url}/get_team_topscorers_without_golden_boot')
    if response.status_code == 200:
        return response.json()
    else:
        current_app.logger.error(f'get_team_topscorers_without_golden_boot return status code: {response.status_code}')

