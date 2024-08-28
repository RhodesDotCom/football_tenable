import os
import pandas as pd
import asyncio
from aiohttp import ClientSession
import sys
import time
from tqdm.asyncio import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
FBREF = 'https://fbref.com/en/'
MAX_POOL_SIZE = 10


def main(players: pd.DataFrame = None) -> list:
    new_rows = asyncio.run(get_two_teams(players))

    return new_rows


async def get_two_teams(df=None):

    if df is None:
        path = 'data/all_players.csv'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, path)
        df = pd.read_csv(csv_path, names=HEADERS)

    two_team_rows = df[(df.Team == '2 Teams')]

    tasks = [split_2_team_rows(row) for row in two_team_rows.values.tolist()]
    new_rows = await tqdm.gather(*tasks, desc="Creating new rows", total=len(two_team_rows))
        
    return [row for rows in new_rows for row in rows]


async def split_2_team_rows(original_row):
    player_id = original_row[0]
    player = original_row[1]
    year = original_row[2]
    
    async with ClientSession() as client:
        url = FBREF + f"players/{player_id}/{player.replace(' ','-')}"
        async with client.get(url) as response:
            if response.status == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                print(f"Rate limited. Retrying after {retry_after} seconds...")
                await asyncio.sleep(retry_after)
            else:
                html = await response.text()
    soup = BeautifulSoup(html, 'html.parser')
    # print(html)

    table = soup.find('table', {'id': 'stats_standard_dom_lg'})
    player_data = []
    if table:
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        player_data = []
        for row in rows:
            year_th = row.find('th')
            if year_th and year_th.text.strip() == year:
                cells = row.find_all('td')
                span_tag = cells[3].find('span')
                if span_tag and span_tag.text.strip() != 'Jr.':
                    player_data.append([cell.text.strip() for cell in cells])
    else:
        print(f'ERROR: {player}, {year} - stats_standard_dom_lg not found')

    table = soup.find('table', {'id': 'stats_playing_time_dom_lg'})
    subs_data = []
    if table:
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            year_th = row.find('th')
            if year_th and year_th.text.strip() == year:
                cells = row.find_all('td')
                span_tag = cells[3].find('span')
                if span_tag and span_tag.text.strip() != 'Jr.':
                    #13 and 15
                    subs_data.append([cell.text.strip() for cell in cells])
    else:
        print(f'ERROR: {player}, {year} - stats_playing_time_dom_lg not found')
    
    if player_data and subs_data:
        try:
            player_data[0].extend([subs_data[0][13], subs_data[0][15]])
            player_data[1].extend([subs_data[1][13], subs_data[1][15]])
            
            return format_tt_row(original_row, player_data)

        except IndexError:
            print(f'IndexError getting player or subs data, line 94. player_data: {player_data}, subs_data: {subs_data} ')
            return []
    else:
        print('Error getting data from table')
        print(f'Player: {player}, year: {year}')
        print(f'player_data: {bool(player_data)}, sub_data: {bool(subs_data)}')
        return []


def format_tt_row(original_row, new_rows):
    
    formatted_rows = []
    for row in new_rows:
        formatted_row = original_row.copy()
        formatted_row[5] = row[1] # team
        formatted_row[7] = row[5]  # MP
        formatted_row[8] = row[7].replace(',', '') # Min
        formatted_row[9] = row[8] # 90s
        formatted_row[10] = row[6] # starts

        formatted_row[11] = row[-2] # subs
        formatted_row[12] = row[-1] # unsubs

        formatted_row[13] = row[9]  # Gls
        formatted_row[14] = row[10]  # Ast
        formatted_row[15] = row[11]  # G+A
        formatted_row[16] = row[12]  # G-PK
        formatted_row[17] = row[13]  # PK
        formatted_row[18] = row[14]  # PKatt

        formatted_rows.append(formatted_row)
    return formatted_rows


rows = main()
# print(rows)
