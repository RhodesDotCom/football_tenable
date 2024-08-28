from bs4 import BeautifulSoup
import requests


def get_country_codes():

    r = requests.get('https://en.wikipedia.org/wiki/List_of_FIFA_country_codes')
    soup = BeautifulSoup(r.text)
    tables = soup.find_all('table', class_='wikitable')


    data = []
    for i in tables[:4]:
        rows = i.find_all('tr')[1:]
        for row in rows:
            cells = row.find_all('td')

            link = cells[0].find('a')
            if link:
                c_name = link.get_text(strip=True)
            else:
                c_name = cells[0].get_text(strip=True)

            c_code = cells[1].get_text(strip=True)

            data.append([c_code, c_name])

    return data