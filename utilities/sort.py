import os
import pandas as pd
import subprocess
from ftfy import fix_text
from bs4 import BeautifulSoup
import requests
import csv
import warnings


warnings.filterwarnings(action='ignore', category=DeprecationWarning)


def install_package(package_name):
    try:
        # Check if the package is installed
        subprocess.check_output(['pip', 'show', package_name])
        print(f"{package_name} is already installed.")
    except subprocess.CalledProcessError:
        # Package is not installed, install it
        subprocess.run(['pip', 'install', package_name])
        print(f"{package_name} has been installed.")


def combine_xls_to_csv(folder_path, output_csv):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, folder_path)

    xls_files = [file for file in os.listdir(path) if file.endswith('.xls') or file.endswith('.xlsx')]
    if not xls_files:
        print("No XLS files found in the specified folder.")
        return
    
    dfs = []
    for xls_file in xls_files:
        file_path = os.path.join(path, xls_file)
        df = pd.read_html(file_path)[0]
        df.columns = df.columns.droplevel(0)
        dfs.append(df)

    output_csv_path = os.path.join(current_dir, output_csv)
    if not os.path.exists(os.path.dirname(output_csv_path)):
        os.makedirs(os.path.dirname(output_csv_path))

    combined_data = pd.concat(dfs).set_index('Rk').sort_index().drop('Comp', axis=1)
    combined_data = combined_data.iloc[:, ~combined_data.columns.duplicated(keep='first')]
    combined_data['Player'] = combined_data['Player'].apply(fix_text)
    combined_data['Nation'] = combined_data['Nation'].str.split().str[-1]
    combined_data.to_csv(output_csv_path, index=False)

    # print(f"Combined data saved to {output_csv_path}.")


def login():
    login_url = 'https://stathead.com/users/login.cgi'
    user = 'email'
    pswd = 'password'

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


def get_players():

    session = login()

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
                for row in rows:
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
                
            else:
                print("Table with id 'stats' not found.")
        else:
            print(f'error getting page {i}, status code: {r.status_code}')
            return players
    return players
        

def write_to_csv(output_csv, data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv_path = os.path.join(current_dir, output_csv)
    if not os.path.exists(os.path.dirname(output_csv_path)):
        os.makedirs(os.path.dirname(output_csv_path))

    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)


# headers = ['Player','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']

# players = get_players()
# output_csv = '../stats-db/csv_data/players.csv'

# write_to_csv(output_csv, players)
