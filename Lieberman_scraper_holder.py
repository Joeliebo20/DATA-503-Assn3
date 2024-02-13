import requests
from bs4 import BeautifulSoup
import json
import csv
import sys
import pandas as pd

def get_stock_holder_data(ticker):
    print(f'Getting stock holder data for {ticker}...')
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    url = f'https://finance.yahoo.com/quote/{ticker}/holders'
    r = requests.get(url, headers=headers)
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        stock = {
            # scraping the stock data from the price indicators
            'stock_name': soup.find('div', {'class':'D(ib) Mt(-5px) Maw(38%)--tab768 Maw(38%) Mend(10px) Ov(h) smartphone_Maw(85%) smartphone_Mend(0px)'}).find_all('div')[0].text.strip(),
            'holders': [hldr.text.strip() for hldr in soup.find('table', {'class':'W(100%) M(0) BdB Bdc($seperatorColor)'}).find_all('td', {'class':'Py(10px) Ta(start) Va(m)'})],
            'percents': [pct.text.strip() for pct in soup.find('table', {'class':'W(100%) M(0) BdB Bdc($seperatorColor)'}).find_all('td', {'class' : 'Py(10px) Va(m) Fw(600) W(15%)'})],
            'top_holders': [hldr_name.text.strip() for hldr_name in soup.find('table', {'class': 'W(100%) BdB Bdc($seperatorColor)'}).find_all('td', {'class':'Ta(start) Pend(10px)'})],
            'text_headers': [txt.text.strip() for txt in soup.find('table', {'class':'W(100%) BdB Bdc($seperatorColor)'}).find_all('th', {'class':'Ta(end) Fw(400) Py(6px) Pstart(15px)'})],
            'holder_data': [data.text.strip() for data in soup.find('table', {'class': 'W(100%) BdB Bdc($seperatorColor)'}).find_all('td', {'class':'Ta(end) Pstart(10px)'})],
            }
        fixed_stock = {}
        
        fixed_stock['stock_name'] = stock['stock_name']
        for hldr, pct in zip(stock['holders'], stock['percents']):
            fixed_stock[hldr] = pct
        
        split_data = [stock["holder_data"][i:i+4] for i in range(0, len(stock["holder_data"]), 4)]

        for index, top_hldr in enumerate(stock['top_holders']):
            holder_info = {}
            for i, header in enumerate(stock['text_headers']):
                holder_info[header] = split_data[index][i]
            fixed_stock[top_hldr] = holder_info
                
    except requests.exceptions.RequestException as e:
        print(f'Could not connect to site, error: {e}')
    return fixed_stock

stocks = ['TSLA', 'AAPL', 'NFLX', 'AMZN', 'GOOGL', 'PYPL', 'DIS', 'NVDA', 'MSFT', 'META']
holder_data = list()
for stock in stocks:
    holder_data.append(get_stock_holder_data(stock))

with open('Lieberman_stock_holder_data.json', 'w', encoding='utf-8') as f:
    json.dump(holder_data, f, indent = 2)

CSV_FILE_PATH = 'Lieberman_stock_holder_data.csv'
with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = holder_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(holder_data)

EXCEL_FILE_PATH = 'Lieberman_stock_holder_data.xlsx'
df = pd.DataFrame(holder_data)
df.to_excel(EXCEL_FILE_PATH, index=False)