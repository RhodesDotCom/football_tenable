import asyncio
import aiohttp
import os
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm
import pandas as pd
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FBREF = 'https://fbref.com/en/'
MAX_PAGE = 20000


async def async_login(session: aiohttp.ClientSession):
    login_url = 'https://stathead.com/users/login.cgi'
    user = os.getenv('STATHEAD_EMAIL')
    pswd = os.getenv('STATHEAD_PSWD')

    # session = requests.Session()
    async with session.get(login_url) as login_page:
        login_page_content = await login_page.text()

    soup = BeautifulSoup(login_page_content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    login_data = {
        'username': user,
        'password': pswd,
        'csrf_token': csrf_token
    }

    async with session.post(login_url, data=login_data) as login_response:
        if login_response.status == 200:
            return session
        else:
            print(login_response.status)
            return None


async def get_player_from_page(session, url):
    players = []
    async with session.get(url) as response:
        if response.status == 200:
                response_content = await response.text()
                soup = BeautifulSoup(response_content, 'html.parser')
                table = soup.find('table', id='stats')

                if table:
                    rows = table.find_all('tr')
                    for index, row in enumerate(rows):
                        cols = row.find_all('td')
                        if not cols:
                            continue

                        cols_text = [col.text.strip() for col in cols] 
                        print(cols_text)
                        if any(cols_text):
                            player_id = cols[0].get('data-append-csv')
                            cols_text.insert(0, player_id)
                            players.append(cols_text)
                else:
                    print("Table with id 'stats' not found.")
        else:
            print(f"Failed to fetch {url}: Status {response.status}")
    return players


async def get_all_players():
    url = "https://stathead.com/fbref/player-season-finder.cgi?request=1&height_type=height_meters&order_by_asc=1&force_min_year=1&phase_id=0&order_by=name_display_csk&per90min_val=5&comp_type=b5&match=player_season&comp_gender=m&per90_type=player&weight_type=kgs&offset={offset}"
    async with aiohttp.ClientSession() as session:
        session = await async_login(session)
        if not session:
            return []
        
        tasks = [
            get_player_from_page(session, url.format(offset=offset))
            for offset in range(0, MAX_PAGE, 200)
        ]

        results = await tqdm.gather(*tasks, desc="Scraping Progress", total=MAX_PAGE//200)
        return results
        # for player_data in results:
        #     if player_data:
        #         players.extend(player_data)
    


'''
async def init_driver():

def split_2_team_rows(driver, row):

async def 



'''


players = asyncio.run(get_all_players())
print(players)
# players = pd.DataFrame(players, columns=HEADERS)
# players.to_csv(os.path.join(CURRENT_DIR, 'data/all_players.csv'), index=False, header=False)