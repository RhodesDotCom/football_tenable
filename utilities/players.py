import os
from dotenv import load_dotenv
import pandas as pd
import subprocess
from ftfy import fix_text
from bs4 import BeautifulSoup
import requests
import csv
import warnings
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unidecode import unidecode
import re
import asyncio
import aiohttp
from tqdm.asyncio import tqdm


warnings.filterwarnings(action='ignore', category=DeprecationWarning)

load_dotenv()


# MAX_PAGE = 18200 #91250 for top 5
# MAX_PAGE = 92000
MAX_PAGE = 5000
HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
FBREF = 'https://fbref.com/en/'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def login(session=requests.Session()):
    login_url = 'https://stathead.com/users/login.cgi'
    user = os.getenv('STATHEAD_EMAIL')
    pswd = os.getenv('STATHEAD_PSWD')

    # session = requests.Session()
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')

    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    login_data = {
        'username': user,
        'password': pswd,
        'csrf_token': csrf_token
    }

    login_response = session.post(login_url, data=login_data)

    if login_response.status_code == 200:
        return session
    else:
        print(login_response)


def get_players():

    session = login()
    if not session:
        sys.exit()

    players = []
    for i in range(0,MAX_PAGE,200):
        print(f'{i}/{MAX_PAGE}', end='\r', flush=True)
        r = session.get(f"https://stathead.com/fbref/player-season-finder.cgi?request=1&height_type=height_meters&force_min_year=1&comp_type=c-9&order_by=name_display_csk&match=player_season&per90_type=player&order_by_asc=1&comp_gender=m&phase_id=0&per90min_val=5&weight_type=kgs&offset={i}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            table = soup.find('table', id='stats')

            if table:
                rows = table.find_all('tr')
                for index, row in enumerate(rows):
                    cols = row.find_all('td')
                    if not cols:
                        continue

                    cols_text = [col.text.strip() for col in cols] 
                    if any(cols_text):
                        player_id = cols[0].get('data-append-csv')
                        cols_text.insert(0, player_id)
                        players.append(cols_text)
            else:
                print("Table with id 'stats' not found.")
        else:
            print(f'error getting page {i}, status code: {r.status_code}')
            return players
        # if i % 1000 == 0:
        #     time.sleep(60)
    return players


def write_to_csv(output_csv, df):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv_path = os.path.join(current_dir, output_csv)
    if not os.path.exists(os.path.dirname(output_csv_path)):
        os.makedirs(os.path.dirname(output_csv_path))

    # with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(data)
    
    df.to_csv(output_csv_path, index=False, header=False)


def float_to_int(ply, tmp):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, ply)
    tmp_path = os.path.join(current_dir, tmp)

    with open(csv_path, 'r', encoding='utf-8') as infile, open(tmp_path, 'w', encoding='utf-8', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            if row[2]:
                row[2] = int(float(row[2]))
            if row[7]:
                try:
                    row[7] = int(float(row[7]))
                except ValueError:
                    row[7] = int(row[7].replace(',',''))
            if row[9]:
                try:
                    row[9] = int(float(row[9]))
                except ValueError:
                    row[9] = int(row[9].replace(',',''))
            if row[10]:
                try:
                    row[10] = int(float(row[10]))
                except ValueError:
                    row[10] = int(row[10].replace(',',''))
            if row[12]:
                try:
                    row[12] = int(float(row[12]))
                except ValueError:
                    row[12] = int(row[12].replace(',',''))
            if row[13]:
                try:
                    row[13] = int(float(row[13]))
                except ValueError:
                    row[13] = int(row[13].replace(',',''))
            if row[14]:
                try:
                    row[14] = int(float(row[14]))
                except ValueError:
                    row[14] = int(row[14].replace(',',''))
            writer.writerow(row)


def col_format(df):
    unique_values = df.player_id.unique()
    value_to_int = {val: idx+1 for idx, val in enumerate(unique_values)}
    df.player_id = df.player_id.map(value_to_int)

    df.Age = df.Age.fillna(0)
    df.Age = df.Age.astype("int64")

    #split nation
    df.Nation = df.Nation.str.split().str[1]
    
    #split competition
    df.Comp = df.Comp.str.split().str[1:].str.join(' ')

    #int minutes
    df.Min = df.Min.str.replace(',','').replace('', 0)
    df.Min = df.Min.fillna(0)
    df.Min = df.Min.astype(int)


def main(getplayers=False, gettwoteams=False, twoteamsfix=False):
   
    if getplayers:
        players = get_players()
        players = pd.DataFrame(players, columns=HEADERS)
        # col_format(players)
        players.to_csv(os.path.join(CURRENT_DIR, 'data/all_players.csv'), index=False, header=False)
    else:
        players = pd.read_csv(os.path.join(CURRENT_DIR, 'data/all_players.csv'), names=HEADERS)
    
    if gettwoteams:
        indices, to_add = get_two_teams(df=players, headers=HEADERS)
        to_add.to_csv(os.path.join(CURRENT_DIR, 'data/two_teams.csv'), index=False, header=False)
        
        # to_add.to_csv(os.path.join(CURRENT_DIR, 'data/two_teams.csv'), index=False, header=False)
    else:
        to_add = pd.read_csv(os.path.join(CURRENT_DIR, 'data/two_teams.csv'), names=HEADERS)
        indices = players[players['Team'] == '2 Teams'].index.tolist()

    if twoteamsfix:
        players.drop(indices, axis=0, inplace=True)
        players = pd.concat([players, to_add], ignore_index=True)
        col_format(players)
        players.sort_values(by=['player_id', 'Age'], inplace=True)
    
        # SAVE TO CSV
        players_csv = 'data/players_formatted.csv'
        csv_path = os.path.join(CURRENT_DIR, players_csv)
        players.to_csv(csv_path, header=False, index=False)

    # PLAYERS TABLE TO CSV
    players = pd.read_csv(os.path.join(CURRENT_DIR, 'data/players_formatted.csv'), names=HEADERS)
    create_player_data(players)

    # STATS TABLE TO CSV
    create_player_stats_data(players)


def get_two_teams(df=None, headers=[]):

    driver = init_driver()

    if df is None:
        path = '../stats-db/csv_data/players_formatted.csv'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, path)
        df = pd.read_csv(csv_path, names=HEADERS)

    def process_row(row):
        return format_tt_rows(row.tolist(), split_2_team_rows(driver, row))

    data = df[df['Team'] == '2 Teams'].apply(process_row, axis=1).dropna().tolist()
    data = [item for sublist in data for item in sublist]
    indices = df[df['Team'] == '2 Teams'].index.tolist()
  
    df_tt = pd.DataFrame(data, columns=HEADERS)
    
    return indices, df_tt


def format_tt_rows(original_row, new_rows):
    output = []
    if new_rows:
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
            
            output.append(formatted_row)

        return output
    return [['']*len(original_row)]*2
        

def format_to_add(df):
    return df.astype(
        {
            'MP': 'int64',
            'Min': 'int64',
            '90s': 'float64',
            'Starts': 'int64',
            'Subs': 'int64',
            'unSub': 'float64',
            'Gls': 'float64',
            'Ast': 'float64',
            'G+A': 'float64',
            'G-PK': 'float64',
            'PK': 'float64',
            'PKatt': 'float64',
            'PKm': 'float64',
        }
    )


def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode
    options.add_argument("--log-level=3")
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options)

    return driver


def split_2_team_rows(driver, row):
        # try:
        #     driver.get(FBREF)
        # except Exception as e:
        #     print(e)
        #     sys.exit

        # try:
        #     search_box = WebDriverWait(driver,10).until(
        #         EC.presence_of_element_located((By.NAME, 'search'))
        #     )
        # except TimeoutException as e:
        #     print(f'Error finding search box: {e}')
        #     sys.exit()


        # search_box.send_keys(player)
        # search_box.send_keys(Keys.RETURN)

        # if driver.current_url.startswith("https://fbref.com/en/search"):
        #     print('HERE')
        #     page_source = driver.page_source
        #     soup = BeautifulSoup(page_source, 'html.parser')
        #     players = soup.find('div', {'id': 'players'})
        #     item_urls = players.find_all('div', {'class': "search-item-name"})
        #     urls = [a_tag['href'] for div in item_urls for a_tag in div.find_all('a')]
        #     page = None
        #     for url in urls:
        #         player_for_url = unidecode(player).replace(' ', '-')
        #         if player_for_url in url:
        #             page = FBREF + url[4:]
        #             break
        #     if page:
        #         driver.get(page)

        player = row['player_name']
        year = row['Season']
        player_id = row['player_id']

        try:
            print(f"{FBREF}players/{player_id}/{player.replace(' ','-')}")
            driver.get(FBREF + f"players/{player_id}/{player.replace(' ','-')}")
        except Exception as e:
            print(e)
            sys.exit()

        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'stats_standard_dom_lg'))
            )
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'stats_playing_time_dom_lg'))
            )
        except TimeoutException as e:
            print(f'Error finding table: {e}')
            sys.exit()

        page_source = driver.page_source
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
                    a_tag = cells[3].find('a')
                    if a_tag and a_tag.text.strip() == 'Premier League':
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
                    a_tag = cells[3].find('a')
                    if a_tag and a_tag.text.strip() == 'Premier League':
                        #13 and 15
                        subs_data.append([cell.text.strip() for cell in cells])
        else:
            print(f'{player}, {year} - stats_playing_time_dom_lg not found')
        
        if player_data and subs_data:
            player_data[0].extend([subs_data[0][13], subs_data[0][15]])
            player_data[1].extend([subs_data[1][13], subs_data[1][15]])
            return player_data
        else:
            print('Error getting data from table')
            print(f'Player: {player_data}, year: {year}')
            print(f'player_data: {bool(player_data)}, sub_data: {bool(subs_data)}')
            time.sleep(100)


def create_player_data(players: pd.DataFrame):
    all_players = players.groupby('player_id').first().reset_index()
    player_table = all_players[['player_id', 'player_name', 'Nation']].copy()

    player_table.to_csv(os.path.join(CURRENT_DIR, '../db-load/data/players.csv'), index=False, header=False)
    player_table.to_csv(os.path.join(CURRENT_DIR, 'data/players.csv'), index=False, header=False)


def create_player_stats_data(players: pd.DataFrame):
    stats_table = players.drop(['player_name', 'Nation'], axis=1)

    stats_table.to_csv(os.path.join(CURRENT_DIR, '../db-load/data/player_stats.csv'), index=False, header=False)
    stats_table.to_csv(os.path.join(CURRENT_DIR, 'data/player_stats.csv'), index=False, header=False)


# main(getplayers=False, gettwoteams=False, twoteamsfix=True)

