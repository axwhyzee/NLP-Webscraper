from pyvis.network import Network
from selenium import webdriver
import networkx as nx
import pandas as pd

PATH = 'C:\Program Files (x86)\chromedriver.exe'
SITES = []
EDGES = []
EDGE_LIST_DIR = 'Edgelists'
NETWORK_GRAPH_DIR = 'Network Graphs'
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
    

def process_df(df):
    df.columns = ['Blank', 'Index', 'Company Name', 'Company Description', 'Type', 'URL_1', 'URL_2']
    df.drop(['Blank', 'Index', 'Type', 'Company Description', 'URL_1'], axis=1, inplace=True)
    
    return df


driver = webdriver.Chrome(PATH)

options = webdriver.ChromeOptions()
options.add_argument('--enable-javascript')
options.add_argument('headless')

df = process_df(pd.read_excel('ComList1.xlsx'))

for i, row in df.iloc[:1].iterrows():
    url = row['URL_2']
    SITES.append(url)

    # iteratively add on the sublinks to our list
    n = 0
    for d in range(MAX_DEPTH):
        limit = len(SITES)
        while n < limit:
            print(SITES[n])
            get_sublinks(SITES[n])
            n += 1

    # create edgelist to plot network graph
    df_network = {'Source':[],
                  'Target':[]}
    
    for e in EDGES:
        df_network['Source'].append(e[0])
        df_network['Target'].append(e[1])

    df_network = pd.DataFrame(df_network)
    df_network.to_csv('{}/{}.csv'.format(EDGE_LIST_DIR,
                                         row['Company Name']), index=False)

    G = nx.from_pandas_edgelist(df_network, source='Source', target='Target')
    net = Network('100vh', '100vw')
    net.from_nx(G)
    net.show('{}/{}.html'.format(NETWORK_GRAPH_DIR,
                              row['Company Name']))

    SITES.clear()
    EDGES.clear()

