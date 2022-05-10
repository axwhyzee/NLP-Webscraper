from selenium import webdriver
import pandas as pd
import os

PATH = 'C:\Program Files (x86)\chromedriver.exe'
HTML_TEXT_DIR = 'HTML Text'
EDGE_LIST_DIR = 'Edgelists'

driver = webdriver.Chrome(PATH)
options = webdriver.ChromeOptions()
options.add_argument('--enable-javascript')
options.add_argument('headless')

for root in os.listdir(EDGE_LIST_DIR)[:1]:
    html_text = ''
    df = pd.read_csv(EDGE_LIST_DIR + '/' + root)
    urls = df['Target'].unique().tolist()

    for url in urls[:10]:
        driver.get(url)
        html_text += driver.find_element_by_css_selector('body').text + '\n'

    with open('{}/{}.txt'.format(HTML_TEXT_DIR,
                              root.split('.')[0]), 'w') as g:
        g.write(html_text)

driver.quit()

'''
1) extract data
2) process
3) train nlp using 2)
4) process


download pdfs
process - keyword matching


get crunchbase website programatically
'''
    
    
