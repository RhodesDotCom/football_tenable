import os
from dotenv import load_dotenv
from aiohttp import ClientSession, CookieJar
from http.cookies import SimpleCookie, Morsel
import asyncio
from bs4 import BeautifulSoup
import requests
import urllib3

urllib3.disable_warnings()


load_dotenv()


### NORMAL
def requestslibrary():
    login_url = 'https://stathead.com/users/login.cgi'
    session = requests.Session()

    login_page = session.get(login_url, verify=False)
    for c in session.cookies:
        print(c)
    print('\n')

    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    payload = {
        'username': os.getenv('STATHEAD_EMAIL'),
        'password': os.getenv('STATHEAD_PSWD'),
        'csrf_token': csrf_token
    }

    r2 = session.post(login_url, data=payload, allow_redirects=False)
    print(r2.headers)
    for c in session.cookies:
        print(c)


async def aiohttplibrary():
    url = "https://stathead.com/users/login.cgi"
    proxy = "http://127.0.0.1:8888"
    session = ClientSession()
    
    r1 = await session.get(url, proxy=proxy)

    soup = BeautifulSoup(await r1.text(), 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    payload = {
        'username': os.getenv('STATHEAD_EMAIL'),
        'password': os.getenv('STATHEAD_PSWD'),
        'csrf_token': csrf_token
    }
   
    
    r2 = await session.post(url, data=payload, allow_redirects=False, proxy=proxy)

    set_cookie_headers = r2.headers.getall('Set-Cookie')
    cookie = SimpleCookie()
    for header in set_cookie_headers:
        cookie.load(header.split(';')[0] + '; path=/; secure')
    session.cookie_jar.update_cookies(cookie)



    url = "https://stathead.com/fbref/player-season-finder.cgi?request=1&height_type=height_meters&order_by_asc=1&force_min_year=1&phase_id=0&order_by=name_display_csk&per90min_val=5&comp_type=b5&match=player_season&comp_gender=m&per90_type=player&weight_type=kgs&offset=0"
    r3 = await session.get(url)
    soup = BeautifulSoup(await r3.text(), 'html.parser')
    table = soup.find('table', id='stats')
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        print([col.text.strip() for col in cols])

    await session.close()

    

loop = asyncio.get_event_loop()
loop.run_until_complete(aiohttplibrary())
# requestslibrary()
