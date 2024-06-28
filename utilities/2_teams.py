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
from bs4 import BeautifulSoup



DRIVER_PATH = 'utilities/chromedriver-win64/chromedriver-win64/chromedriver.exe'
FBREF = 'https://fbref.com/en/'


def split_2_team_rows(player, year):
    
    # options = webdriver.ChromeOptions()
    # # options.add_argument('--headless')  # Run in headless mode
    # options.add_argument('--disable-gpu')  # Disable GPU acceleration
    driver = webdriver.Chrome()

    try:
        driver.get(FBREF)

        search_box = driver.find_element(By.NAME, 'search')
        search_box.send_keys(player)
        search_box.send_keys(Keys.RETURN)

        # time.sleep(3)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        table = soup.find('table', {'id': 'stats_standard_dom_lg'})

        data = []
        if table:
            tbody = table.find('tbody')
            rows = tbody.find_all('tr')
            for row in rows:
                year_th = row.find('th')
                if year_th and year_th.text.strip() == year:
                    cells = row.find_all('td')
                    data.append([cell.text.strip() for cell in cells])
        else:
            data = "ERROR"
    finally:
        driver.quit()
    
    return data



test = [
    ["Patrick van Aanholt","2016-2017"],
    ["Neil Adams","1993-1994"],
    ["Yakubu Aiyegbeni","2007-2008"],
    ["Nathan Aké","2016-2017"],
    ["Paul Allen","1993-1994"],
    ["Dele Alli","2021-2022"],
    ["Nicolas Anelka","2007-2008"],
    ["Victor Anichebe","2013-2014"],
    ["Cameron Archer","2023-2024"],
    ["Mikel Arteta","2011-2012"],
    ["Harrison Ashby","2022-2023"],
    ["André Ayew","2017-2018"],
    ["Demba Ba","2012-2013"],
    ["Celestine Babayaro","2004-2005"],
    ["Phil Babb","1994-1995"],
    ["Patrick Bamford","2015-2016"],
    ["Patrick Bamford","2016-2017"],
    ["Ross Barkley","2020-2021"],
    ["Nick Barmby","1996-1997"],
    ["John Barnes","1998-1999"]
]

for player in test:
    data = split_2_team_rows(player[0], player[1])
    print(data)
