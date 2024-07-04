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

from two_teams import split_2_team_rows, init_driver

# from two_teams import split_2_team_rows, format_rows

warnings.filterwarnings(action='ignore', category=DeprecationWarning)

load_dotenv()


MAX_PAGE = 18200


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

    #split nation
    df.Nation = df.Nation.str.split().str[1]
    
    #split competition
    df.Comp = df.Comp.str.split().str[1:].str.join(' ')

    #int minutes
    df.Min = df.Min.str.replace(',','').replace('', 0)
    df.Min = df.Min.astype(int)


def main():
    headers = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
    players = get_players()
    players = pd.DataFrame(players, columns=headers)
    col_format(players)
    
    csv_path = '../stats-db/csv_data/players_formatted.csv'
    write_to_csv(csv_path, players)



def remove_two_teams():

    driver = init_driver()

    path = '../stats-db/csv_data/players_formatted.csv'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, path)
    df = pd.read_csv(csv_path)
    total = len(df)

    data = []
    for i in range(0, 10):
        print(f'{i}/{total}', end='\r', flush=True)

        row = df.iloc[i].to_list()
        try:
            if '2 Teams' in row[5]:
                new_rows = split_2_team_rows(driver, row[1], row[2])
                new_rows = format_tt_rows(row, new_rows)
                data.extend(new_rows)
        except Exception as e:
            print(e)
            sys.exit()
    
    df_tt = pd.DataFrame(data)
    tt_path = '../stats-db/csv_data/two_teams.csv'
    write_to_csv(tt_path, df_tt)


def format_tt_rows(original_row, new_rows):
    print(original_row)
    print(new_rows[0])

    output = []
    for row in new_rows:
        formatted_row = original_row.copy()
        formatted_row[5] = row[1] # team
        formatted_row[7] = row[5]  # MP
        formatted_row[8] = row[7] # Min
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
        

# main()
remove_two_teams()
