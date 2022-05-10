from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pyvis.network import Network
import matplotlib.pyplot as plt
from selenium import webdriver
import networkx as nx
import pandas as pd
import time

PATH = 'C:\Program Files (x86)\chromedriver.exe'
SITES = []
EDGES = []
MAX_DEPTH = 2
invalid = ['youtube.com',
           'chrome.google',
           'google.com',
           'facebook.com',
           'twitter.com',
           'instagram.com',
           'linkedin.com',
           'messenger.com',
           'bulletin.com',
           'cloudflare.com',
           'apps.apple',
           'rsci.app.link',
           'policy.medium',
           'help.medium',
           'medium.com/tag/',
           'https://medium.com/@',
           'https://medium.com/m/signin',
           'apple.com',
           'knowable.fyi'
           'camerapositioning.io',
           '/about',
           ]


def check_link(s):
    if 'http' not in s:
        return False
    
    for inv in invalid:
        if inv in s:
            return False
    return True


def get_sublinks(url):
    driver.get(url)
     
    try:
        elems = driver.find_elements_by_tag_name('a')
        for elem in elems:
            href = elem.get_attribute('href')
            print(href)
            if check_link(href) and href not in SITES:  
                SITES.append(href)
                EDGES.append((url, href))
    except:
        pass
    

urls = ['http://aisle411.com/', 
        'https://blog.fantasmo.io/',
        'https://www.fantasmo.io/',
        'https://www.artisense.ai/research',
        'https://averos.com/',
        'https://www.barikoi.com/'
       ]

driver = webdriver.Chrome(PATH)

options = webdriver.ChromeOptions()
options.add_argument('--enable-javascript')
options.add_argument('headless')

SITES.append(urls[1])
n = 0
for d in range(MAX_DEPTH):
    limit = len(SITES)
    while n < limit:
        print(SITES[n])
        get_sublinks(SITES[n])
        n += 1
        
#m = {}
#for i in range(len(SITES)):
#    m[SITES[i]] = i

df_network = {'Source':[],
              'Target':[],
              'Weight':[]}

for e in EDGES:
    df_network['Source'].append(e[0])
    df_network['Target'].append(e[1])
    #df_network['Source'].append(m[e[0]])
    #df_network['Target'].append(m[e[1]])
    df_network['Weight'].append(1)

df_network = pd.DataFrame(df_network[['Source', 'Target']])
df_network.to_csv('Network.csv', index=False)

G = nx.from_pandas_edgelist(df_network, source='Source', target='Target', edge_attr='Weight')
net = Network()
net.from_nx(G)
net.show("network.html")
