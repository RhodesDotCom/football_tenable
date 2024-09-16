from bs4 import BeautifulSoup
import requests
import argparse
import sys
import os
import csv


def main():
    parser = argparse.ArgumentParser(description="Get FIFA country codes")
    parser.add_argument('-o', '--output', type=str, required=False, help='output path')
    args = parser.parse_args()

    if args.output:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(current_dir, args.output)
        *dirs, _ = output_path.split('/')
        os.makedirs('/'.join(dirs), exist_ok=True)
    else:
        print("Output path required")
        print("Exiting...")
        sys.exit(1)

    data = get_country_codes()

    with open(output_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print(f"country codes csv saved to {output_path}")


def get_country_codes() -> list[list]:

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


if __name__ == '__main__':
    main()