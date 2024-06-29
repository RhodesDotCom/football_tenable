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


def split_2_team_rows(player: str, year: str):
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument("--log-level=3")
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    driver = webdriver.Chrome(options=options)

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


def format_rows(original, rows):
    # original = ['Player','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
    # new = Season,Age,Squad,Country,Comp,LgRank,MP,Starts,Min,90s,Gls,Ast,G+A,G-PK,PK,PKatt,CrdY,CrdR,Gls,Ast,G+A,G-PK,G+A-PK,Matches
    # change = 3:2, 6:6, :7, 8, 
    # available_info = (TEAM, MP, Min, 90s, Starts, Subs-NA, unSub-NA, Gls, G+A, G-PK, PK, PKatt, PKm)
    
    new_rows = []
    for row in rows:
        new_row = original.copy()
        new_row[4] = row[2]  # team
        new_row[6] = row[6]  # MP
        new_row[7] = row[8]  # Min
        new_row[8] = row[9]  # 90s
        new_row[9] = row[7]  # Starts
        new_row[10] = None # Subs
        new_row[11] = None # unSub
        new_row[12] = row[10]  # Gls
        new_row[13] = row[11]  # Ast
        new_row[14] = row[12]  # G+A
        new_row[15] = row[13]  # G-PK
        new_row[16] = row[14]  # PK
        new_row[17] = row[15]  # PKatt

        if row[15]:
            PKatt = int(row[15])
        else:
            PKatt = 0
        if row[14]:
            PK = int(row[14])
        else:
            PK = 0
        new_row[18] = str(PKatt - PK)  # PK missed

        new_rows.append(new_row)
    
    return new_rows


# test = [
#     ["Patrick van Aanholt","2016-2017"],
#     ["Neil Adams","1993-1994"],
#     ["Yakubu Aiyegbeni","2007-2008"],
#     ["Nathan Aké","2016-2017"],
#     ["Paul Allen","1993-1994"],
#     ["Dele Alli","2021-2022"],
#     ["Nicolas Anelka","2007-2008"],
#     ["Victor Anichebe","2013-2014"],
#     ["Cameron Archer","2023-2024"],
#     ["Mikel Arteta","2011-2012"],
#     ["Harrison Ashby","2022-2023"],
#     ["André Ayew","2017-2018"],
#     ["Demba Ba","2012-2013"],
#     ["Celestine Babayaro","2004-2005"],
#     ["Phil Babb","1994-1995"],
#     ["Patrick Bamford","2015-2016"],
#     ["Patrick Bamford","2016-2017"],
#     ["Ross Barkley","2020-2021"],
#     ["Nick Barmby","1996-1997"],
#     ["John Barnes","1998-1999"]
# ]

# for player in test:
#     data = split_2_team_rows(player[0], player[1])
#     print(data)
