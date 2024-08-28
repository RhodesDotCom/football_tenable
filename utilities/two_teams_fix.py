import os
import pandas as pd
import asyncio
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

def main(players: pd.DataFrame = None, cookie=None) -> list:
    df, *two_teams = asyncio.run(get_two_teams(players, cookie))
    # print(two_teams)
    formatted_rows = format_tt_rows(*two_teams)

    return formatted_rows


async def get_two_teams(df=None, cookie=None):

    # loop = asyncio.get_event_loop()
    driver = await init_driver()#loop.run_in_executor(None, init_driver, cookie)

    if df is None:
        path = 'data/all_players.csv'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, path)
        df = pd.read_csv(csv_path, names=HEADERS)

    two_team_rows = df[(df.Team == '2 Teams')]
    # print(two_team_rows)

    tasks = [split_2_team_rows(driver, row) for row in two_team_rows.itertuples(index=False)]
    new_rows = await tqdm.gather(*tasks, desc="Creating new rows", total=len(two_team_rows))
    
    return df, two_team_rows.values.tolist(), new_rows


async def split_2_team_rows(driver, row):
    player = row.player_name
    year = row.Season
    player_id = row.player_id

    page_source = await load_page(driver, player_id, player)
    soup = BeautifulSoup(page_source, 'html.parser')

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
                if span_tag and span_tag.text.strip() != 'Jr':
                    player_data.append([cell.text.strip() for cell in cells])
    else:
        print(f'{player}, {year} - stats_standard_dom_lg not found')

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
                if span_tag and span_tag.text.strip() != 'Jr':
                    #13 and 15
                    subs_data.append([cell.text.strip() for cell in cells])
    else:
        print(f'{player}, {year} - stats_playing_time_dom_lg not found')
    
    if player_data and subs_data:
        try:
            player_data[0].extend([subs_data[0][13], subs_data[0][15]])
            player_data[1].extend([subs_data[1][13], subs_data[1][15]])
            return player_data
        except IndexError:
            print(player)
            print(player_data)
    else:
        print('Error getting data from table')
        print(f'Player: {player}, year: {year}')
        print(f'player_data: {bool(player_data)}, sub_data: {bool(subs_data)}')
        return []


def format_tt_rows(original_row, new_rows):
    output = []

    for pair in zip(original_row, new_rows):
        for row in pair[1]:
            # print(row)
            formatted_row = pair[0].copy()
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
            
            output.append(formatted_row)

        return output
    return [['']*len(original_row)]*2


async def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode
    options.add_argument("--log-level=3")
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options)
    # driver.add_cookie(cookie)
    return driver


async def load_page(driver, player_id, player):
    try:
        loop = asyncio.get_event_loop()
        # Running driver.get() in a thread
        await loop.run_in_executor(None, driver.get, FBREF + f"players/{player_id}/{player.replace(' ','-')}")

        # Wait for the first element
        await loop.run_in_executor(None, WebDriverWait(driver, 10).until, EC.visibility_of_element_located((By.ID, 'stats_standard_dom_lg')))
        
        # Wait for the second element
        await loop.run_in_executor(None, WebDriverWait(driver, 10).until, EC.visibility_of_element_located((By.ID, 'stats_playing_time_dom_lg')))
        
        page_source = driver.page_source

        return page_source
    
    except TimeoutException as e:
            print(f'Error finding table: {e}')
            sys.exit()
    except Exception as e:
            print(e)
            sys.exit()


rows = main()
print(rows)


#NOTE
# SEEMS TO WORK ONE AT A TIME (with one two teams row)
# breaks when multiple, maybe dues to async