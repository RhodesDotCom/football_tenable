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

from two_teams import split_2_team_rows, format_rows

warnings.filterwarnings(action='ignore', category=DeprecationWarning)

load_dotenv()




def login():
    login_url = 'https://stathead.com/users/login.cgi'
    user = os.getenv('STATHEAD_EMAIL')
    pswd = os.getenv('STATHEAD_PSWD')

    session = requests.Session()
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
        raise SystemExit

    players = []
    for i in range(0,18200,200):
        print(f'{i}/18000', end='\r', flush=True)
        r = session.get(f"https://stathead.com/fbref/player-season-finder.cgi?request=1&height_type=height_meters&force_min_year=1&comp_type=c-9&order_by=name_display_csk&match=player_season&per90_type=player&order_by_asc=1&comp_gender=m&phase_id=0&per90min_val=5&weight_type=kgs&offset={i}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            table = soup.find('table', id='stats')

            if table:
                # Process the table data
                rows = table.find_all('tr')
                for index, row in enumerate(rows):
                    # print(f'{i+index+1}/18000', end='\r', flush=True)
                    cols = row.find_all('td')
                    cols = [col.text.strip() for col in cols] 
                    if any(cols):
                        if cols[3]:
                            cols[3] = cols[3].split()[-1]
                        if cols[5]:
                            cols[5] = ' '.join(cols[5].split()[1:])
                        if cols[7]:
                            cols[7] = int(cols[7].replace(',',''))
                        players.append(cols)
                        # if cols[4] == '2 Teams':
                        #     new_cols = split_2_team_rows(cols[0], cols[1])
                        #     new_cols = format_rows(cols, new_cols)
                        #     players.extend(new_cols)
                        # else:
                        #     players.append(cols)
            else:
                print("Table with id 'stats' not found.")
        else:
            print(f'error getting page {i}, status code: {r.status_code}')
            return players
        # if i % 1000 == 0:
        #     time.sleep(60)
    return players


def write_to_csv(output_csv, data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv_path = os.path.join(current_dir, output_csv)
    if not os.path.exists(os.path.dirname(output_csv_path)):
        os.makedirs(os.path.dirname(output_csv_path))

    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)


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



# headers = ['Player','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']

# players = get_players()
# # print(players)
# output_csv = '../stats-db/csv_data/players.csv'
# # output_csv = 'players.csv'
# write_to_csv(output_csv, players)

infile = '../stats-db/csv_data/players_formatted.csv'
outfile = '../stats-db/csv_data/players_formatted_int.csv'
float_to_int(infile, outfile)