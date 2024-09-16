import asyncio
from aiohttp import ClientSession
from http.cookies import SimpleCookie
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm
import pandas as pd
import sys


'''
This script scrapes all players from top 5 European leagues

main --> main function, calls player fetch and saves as CSV
get_all_players --> returns full list of player rows. This is the main function for retrieving dataset
login --> used to login to stathead and save login cookies to session
get_all_players_from_page --> returns list of player rows from a ssingle page (200)
manual_add_page --> returns list of player rows. Used to retrive pages by page number, used if main loop errors
'''

HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


load_dotenv()


def main(url: str, max_page: int) -> pd.DataFrame:
    players = asyncio.run(get_all_players(url, max_page))
    players = pd.DataFrame(players, columns=HEADERS)
    players.drop_duplicates(inplace=True)

    return players


async def get_all_players(url: str | None = None, max_page: int = 0) -> list: 
    try:
        async with ClientSession() as session:
            session = await login(session)
            
            if not url.endswith("&offset={offset}"):
                url += "&offset={offset}"

            tasks = [
                get_player_from_page(session, url.format(offset=offset))
                for offset in range(0, max_page, 200)
            ]
            results = await tqdm.gather(*tasks, desc="Scraping Progress", total=max_page//200)

            return [row for page in results if page for row in page if row]
        
    except SystemExit:
        print("Exiting...")
        sys.exit(1)
    except asyncio.TimeoutError:
        for task in asyncio.all_tasks():
            task.cancel()
        print("Asyncio Timeout Error occurred.")
        print("Exiting...")
        sys.exit(1)
    except asyncio.CancelledError:
        print("Task was cancelled. Exiting...")
        sys.exit(1)


async def login(session: ClientSession) -> ClientSession:
    login_url = 'https://stathead.com/users/login.cgi'

    login_page = await session.get(login_url)
    
    if login_page.status == 200:
        pass
    else:
        print("Login unsuccessful.")
        raise SystemExit

    soup = BeautifulSoup(await login_page.text(), 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    payload = {
        'username': os.getenv('STATHEAD_EMAIL'),
        'password': os.getenv('STATHEAD_PSWD'),
        'csrf_token': csrf_token
    }

    login_response = await session.post(login_url, data=payload, allow_redirects=False)

    set_cookie_headers = login_response.headers.getall('Set-Cookie')
    cookie = SimpleCookie()
    for header in set_cookie_headers:
        cookie.load(header.split(';')[0] + '; path=/; secure')
    session.cookie_jar.update_cookies(cookie)

    return session


async def get_player_from_page(session: ClientSession, url: str) -> list[list]:
    players = []
    try:
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
                            if any(cols_text):
                                player_id = cols[0].get('data-append-csv')
                                cols_text.insert(0, player_id)
                                players.append(cols_text)
                    else:
                        print("Table with id 'stats' not found.")
            else:
                print(f"Failed to fetch {url}: Status {response.status}")
        return players
    except Exception as e:
        print(f"ERROR: {e}")


async def manual_add_page(page_numbers: list[int]) -> list[list]:
    url = "https://stathead.com/fbref/player-season-finder.cgi?request=1&height_type=height_meters&order_by_asc=1&force_min_year=1&phase_id=0&order_by=name_display_csk&per90min_val=5&comp_type=b5&match=player_season&comp_gender=m&per90_type=player&weight_type=kgs&offset={offset}"
    async with ClientSession() as session:
        session = await login(session)
        tasks = [
            get_player_from_page(session, url.format(offset=offset))
            for offset in page_numbers
        ]
        results = await tqdm.gather(*tasks, desc="Scraping Progress", total=len(page_numbers))
    return [row for page in results for row in page]
