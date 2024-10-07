from flask import current_app
import requests
import json

from config import Config


url = Config.SESSION_API_URL


def add_session_variable(data):
    body = {
        'session_data': json.dumps(data)
    }

    response = requests.post(f'{url}/add_session_variable', json=body)
    
    response_json = response.json()   
    
    if response.status_code == 201 and response_json.get('session_id', False):
        return response_json.get('session_id')
    else:
        current_app.logger.error(f'add_session_variable returned status_code: {response.status_code}')
        return None

def read_session_variable(session_id):
    params = {
        'session_id': session_id
    }
    response = requests.get(f'{url}/read_session_variable', params=params)

    if response.status_code == 200:
        return response.json()
    else:
        current_app.logger.error(f'read_session_variable returned status_code: {response.status_code}')