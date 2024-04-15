import requests

from config import Config


config = Config()
url = config.DATA_API_URL


def get_all_players():
    response = requests.get(f'{url}/get_all_players')
    if response.status_code == 200:
        return response.json()


def get_golden_boot_winners():
    response = requests.get(f'{url}/get_golden_boot_winners')
    if response.status_code == 200:
        return response.json()
