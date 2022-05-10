#!pip install mechanicalsoup
from requests.sessions import HTTPAdapter
import mechanicalsoup
import pandas as pd
import os

df = pd.read_excel(os.listdir()[0])
df = pd.read_excel('ComList1.xlsx', 'SensorBased')
df.columns = ['Blank', 'Index', 'Company Name', 'Company Description', 'Type', 'URL']
df.drop(['Blank', 'Index'], inplace=True, axis=1)

browser = mechanicalsoup.StatefulBrowser()
actual_url = []

for i, row in df.iterrows():
    if 'members.luxresearchinc' not in row['URL'] and 'crunchbase.com' not in row['URL']:
        actual_url.append(row['URL'])
        continue
    browser.open('https://www.google.com')
    browser.select_form()
    browser['q'] = row['Company Name']
    browser.launch_browser()
    response = browser.submit_selected()

    page = browser.get_current_page()
    for a in page.find_all('a'):
        href = a.get('href')
        valid = True
        if href[:4]!='/url':
            continue
        for invalid in ['wikipedia.org', 'linkedin', 'twitter', 'crunchbase', 'members.luxresearchinc']:
            if invalid in href:
                valid = False
                break
        if valid:
            actual_url.append(href[7:href.index('&sa')])
            break

if len(actual_url) == df.shape[0]:
    df['actual_url'] = actual_url
    df.to_excel('modified.xlsx', index=False)
