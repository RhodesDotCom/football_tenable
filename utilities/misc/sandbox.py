from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys

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


def load_page(driver, player_id, player):
    try:
        # Running driver.get() in a thread
        driver.get(FBREF + f"players/{player_id}/{player.replace(' ','-')}")

        # Wait for the first element
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'stats_standard_dom_lg')))
        
        # Wait for the second element
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'stats_playing_time_dom_lg')))
        
        page_source = driver.page_source

        return page_source
    except TimeoutException as e:
            print(f'Error finding table: {e}')
            sys.exit()
    except Exception as e:
            print(e)
            sys.exit()


def split_2_team_rows(driver, row):
    player = row[1]
    year = row[2]
    player_id = row[0]

    page_source = load_page(driver, player_id, player)
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
        player_data[0].extend([subs_data[0][13], subs_data[0][15]])
        player_data[1].extend([subs_data[1][13], subs_data[1][15]])
        return player_data
    else:
        print('Error getting data from table')
        print(f'Player: {player}, year: {year}')
        print(f'player_data: {bool(player_data)}, sub_data: {bool(subs_data)}')
        return []


row = ["fc6a1641","Yacine Abdessadki","2005-2006",24,"ma MAR","2 Teams","fr Ligue 1",22,"1,690",18.8,20,2,None,0,None,None,0,0,0,0,"MF"]
driver = init_driver()

player_data = split_2_team_rows(driver, row)