import requests
from bs4 import BeautifulSoup
import json
import csv
import sys
import pandas as pd


def get_stock_profile_data(ticker):
    print(f'Getting stock profile data for {ticker}...')
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    url = f'https://finance.yahoo.com/quote/{ticker}/profile'
    r = requests.get(url, headers=headers)
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        profile = {
            'stock_name': soup.find('div', {'class':'D(ib) Mt(-5px) Maw(38%)--tab768 Maw(38%) Mend(10px) Ov(h) smartphone_Maw(85%) smartphone_Mend(0px)'}).find_all('div')[0].text.strip(),
            'address': soup.find('div', {'class':'Mb(25px)'}).find('p', {'class':'D(ib) W(47.727%) Pend(40px)'}).get_text(separator='\n'),
            'key_executives': [name.text.strip() for name in soup.find('table', {'class':'W(100%)'}).find_all('td', {'class':'Ta(start)'})],
        }
        profile['key_executives'] = dict(zip(profile['key_executives'][::2], profile['key_executives'][1::2]))
    except requests.exceptions.RequestException as e:
        print(f'Could not connect to site, error: {e}')
    return profile

stocks = ['TSLA', 'AAPL', 'NFLX', 'AMZN', 'GOOGL', 'PYPL', 'DIS', 'NVDA', 'MSFT', 'META']
profile_data = list()
for stock in stocks:
    profile_data.append(get_stock_profile_data(stock))

with open('Lieberman_stock_profile_data.json', 'w', encoding='utf-8') as f:
    json.dump(profile_data, f, indent = 2)


CSV_FILE_PATH = 'Lieberman_stock_profile_data.csv'
with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = profile_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(profile_data)

EXCEL_FILE_PATH = 'Lieberman_stock_profile_data.xlsx'
df = pd.DataFrame(profile_data)
df.to_excel(EXCEL_FILE_PATH, index=False)