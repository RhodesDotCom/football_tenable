import os
import pandas as pd
import requests
import sys
import time
from datetime import datetime
from tqdm import tqdm
from bs4 import BeautifulSoup


HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
FBREF = 'https://fbref.com/en/'
WAIT_TIME = 4.5


class RateLimitRequester:
    def __init__(self):
        self.last_request = datetime.min

    def makeRequest(self, url):
        td = (datetime.now() - self.last_request).total_seconds()
        if td < WAIT_TIME:
            time.sleep(WAIT_TIME-td)
        self.last_request = datetime.now()
        
        r = requests.get(url)
        if r.status_code == 429:
            print("\nrate limit hit")
            print(r.headers.get('Retry-After'))
            r.close()
            sys.exit()
        else:
            # print(f' success {r.status_code}')
            r.close()
            return r.text


def main(players: pd.DataFrame = None) -> list:
    new_rows = get_two_teams(players)
    return new_rows


def get_two_teams(df: pd.DataFrame | None = None) -> list:
   
    if df is None:
        path = 'data/all_players.csv'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, path)
        df = pd.read_csv(csv_path, names=HEADERS)
    
    two_team_rows = df[(df.Team == '2 Teams') | (df.Team == '3 Teams')]

    requester = RateLimitRequester()

    new_rows = []
    errors = []
    blanks = []
    for row in tqdm(iterable=two_team_rows.values.tolist(), desc="Creating new rows", total=len(two_team_rows)):
        try:
            output = split_2_team_rows(requester, row)
            if not output:
                blanks.append(row)
            new_rows.append(output)
        except Exception as e:
            errors.append((e, row))
    
    new_rows.append([[],[]])

    return [row for rows in new_rows for row in rows if row], blanks, errors


def split_2_team_rows(requester: RateLimitRequester, original_row: list) -> list[list]:
    player_id = original_row[0]
    player = original_row[1]
    year = original_row[2]

    url = FBREF + f"players/{player_id}/{player.replace(' ','-')}"
    html = requester.makeRequest(url)
    soup = BeautifulSoup(html, 'html.parser')

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
            raise
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
        formatted_row[6] = row[3] # league
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

