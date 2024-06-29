'''
- find players with 2 teams
- saerch fbref
- find table
- take stats from table (MP, Min, 90s, Starts, Subs-NA, unSub-NA, Gls, G+A, G-PK, PK, PKatt, PKm)
- everything else filled from orig row
- create 2 rows
'''    

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys
import time
from unidecode import unidecode
import os
import csv
import pandas as pd

DRIVER_PATH = 'utilities/chromedriver-win64/chromedriver-win64/chromedriver.exe'
FBREF = 'https://fbref.com/en/'


def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode
    options.add_argument("--log-level=3")
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options)

    return driver


def split_2_team_rows(driver, player: str, year: str):
    
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode
    # options.add_argument("--log-level=3")
    # options.add_argument('--disable-gpu')  # Disable GPU acceleration
    # options.add_argument('--window-size=1920,1080')
    # options.add_argument('--blink-settings=imagesEnabled=false')
    # driver = webdriver.Chrome(options=options)

        try:
            driver.get(FBREF)
        except Exception as e:
            print(e)
            sys.exit

        try:
            search_box = WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.NAME, 'search'))
            )
        except TimeoutException as e:
            print(f'Error finding search box: {e}')
            sys.exit()


        search_box.send_keys(player)
        search_box.send_keys(Keys.RETURN)

        if driver.current_url.startswith("https://fbref.com/en/search"):
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            players = soup.find('div', {'id': 'players'})
            item_urls = players.find_all('div', {'class': "search-item-name"})
            urls = [a_tag['href'] for div in item_urls for a_tag in div.find_all('a')]
            page = None
            for url in urls:
                player_for_url = unidecode(player).replace(' ', '-')
                if player_for_url in url:
                    page = FBREF + url[4:]
                    break
            if page:
                driver.get(page)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'stats_standard_dom_lg'))
            )
        except TimeoutException as e:
            print(f'Error finding table: {e}')
            sys.exit()

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        table = soup.find('table', {'id': 'stats_standard_dom_lg'})

        if table:
            tbody = table.find('tbody')
            rows = tbody.find_all('tr')
            data = []
            for row in rows:
                year_th = row.find('th')
                if year_th and year_th.text.strip() == year:
                    cells = row.find_all('td')
                    a_tag = cells[3].find('a')
                    if a_tag and a_tag.text.strip() == 'Premier League':
                        data.append([cell.text.strip() for cell in cells])
            return data
        else:
            print('Table not found')
            sys.exit()
        

def format_rows(original, rows):
    # original = ['Player','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
    # new = Season,Age,Squad,Country,Comp,LgRank,MP,Starts,Min,90s,Gls,Ast,G+A,G-PK,PK,PKatt,CrdY,CrdR,Gls,Ast,G+A,G-PK,G+A-PK,Matches
    # change = 3:2, 6:6, :7, 8, 
    # available_info = (TEAM, MP, Min, 90s, Starts, Subs-NA, unSub-NA, Gls, G+A, G-PK, PK, PKatt, PKm)
    try:
        new_rows = []
        for row in rows:
            new_row = original.copy()
            new_row[4] = row[1]  # team
            new_row[6] = row[5]  # MP
            new_row[7] = row[7]  # Min
            new_row[8] = row[8]  # 90s
            new_row[9] = row[6]  # Starts
            new_row[10] = None # Subs
            new_row[11] = None # unSub
            new_row[12] = row[9]  # Gls
            new_row[13] = row[10]  # Ast
            new_row[14] = row[11]  # G+A
            new_row[15] = row[12]  # G-PK
            new_row[16] = row[13]  # PK
            new_row[17] = row[14]  # PKatt

            if row[14]:
                PKatt = int(row[14])
            else:
                PKatt = 0
            if row[13]:
                PK = int(row[13])
            else:
                PK = 0
            new_row[18] = str(PKatt - PK)  # PK missed

            new_rows.append(new_row)
        
        # print(new_rows)
        return new_rows
    except Exception as e:
        print(e)
        print(original)
        print(rows)
  

def replace_rows(players_csv, new_csv, errors_path, start):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    players_csv_path = os.path.join(current_dir, players_csv)
    players_formatted_csv_path = os.path.join(current_dir, new_csv)
    if not os.path.exists(os.path.dirname(players_formatted_csv_path)):
        os.makedirs(os.path.dirname(players_formatted_csv_path))
    
    errors_path = os.path.join(current_dir, errors_path)
    if not os.path.exists(os.path.dirname(errors_path)):
        os.makedirs(os.path.dirname(errors_path))
    


    df = pd.read_csv(players_csv_path)
    total = len(df)

    driver = init_driver()

    formatted_rows = []
    errors = []
    for i in range(start, total):
        print(f'{i}/{total}', end='\r', flush=True)

        row = df.iloc[i].to_list()
        try:
            if '2 Teams' in row[4]:
                new_rows = split_2_team_rows(driver, row[0], row[1])
                try:
                    row_1, row_2 = format_rows(row, new_rows)
                except ValueError:
                    errors.append(row)
                    formatted_rows.append(row)
                    continue
                formatted_rows.append(row_1)
                formatted_rows.append(row_2)
            else:
                formatted_rows.append(row)
        except Exception as e:
            print(f'Error processsing row {i}: {e}')
            break

        formatted_df = pd.DataFrame(formatted_rows)

        mode = 'a' if start > 0 else 'w'
        formatted_df.to_csv(players_formatted_csv_path, mode=mode, index=False, header=False)

    driver.quit()

    with open(errors_path, 'a', encoding='utf-8') as errors_file:
        writer = csv.writer(errors_file)
        writer.writerows(errors)

