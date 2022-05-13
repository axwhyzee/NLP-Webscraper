#############
## Imports ##
#############

from pyvis.network import Network
from selenium import webdriver
import networkx as nx
import pandas as pd
import hashlib
import urllib
import sys
import os

lib_dir = os.path.join(os.getcwd(), 'Lib')
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

from img_processing import *
from pdf_reader import PDFReader
from gen_unused_path import gen_path
from reverse_search import ReverseSearch
from google_translate import GoogleTranslate

#####################
## Modifiable Vars ##
#####################

PATH = 'C:\Program Files (x86)\chromedriver.exe'
MAX_DEPTH = 3

HTML = ''
SITES = []
EDGES = {}
CHECKSUMS = {}
PDF_READER = PDFReader()
REVERSE_SEARCH = ReverseSearch()
TRANSLATOR = GoogleTranslate()

EDGE_LIST_DIR = 'Edgelists'
HTML_TEXT_DIR = 'HTML Text'
NETWORK_GRAPH_DIR = 'Network Graphs'

invalid_mid = [
    'youtube.com',
    'youtu.be',
    'vimeo.com',
    'github.com',
    'chrome.google',
    'goo.gl',
    'google.com',
    'facebook.com',
    'twitter.com',
    'instagram.com',
    'linkedin.com',
    'messenger.com',
    'wevolver',
    'reddit',
    'bulletin.com',
    'cloudflare.com',
    'apps.apple',
    'rsci.app.link',
    'policy.medium',
    'help.medium',
    'medium.com',
    'apple.com',
    'knowable.fyi',
    'un.org',
    'camerapositioning.io',
]

invalid_seg = [
    'ch', 'jp', 'es', 'de', 'ko', 'fr', 'ru', 'zh', 'zh-hant',
    'about', 'about-us', 'team', 'join-us', 'jobs', 'careers', 'career',
    'contact', 'contact-us', 'support', 'warranty', 'shipment', 'payment-methods', 'downloads', 'help',
    'terms', 'privacy', 'privacy-policy', 'copyright', 'company', 'terms-conditions', 'cookies',
    'login', 'log-in', 'signin', 'sign-in', 'signup', 'sign-up',
    'tag', 'news', 'testimonials', 'use-cases',
]

invalid_seg_start = ['@']

invalid_ext = [
    '.jpg', '.jpeg', '.svg', '.png', '.mp4', '.gif',
    '.ch', '=ch',
    '.jp', '=jp',
    '.es', '=es',
    '.de', '=de',
    '.ko', '=ko',
    '.fr', '=fr',
    '.ru', '=ru',
    '.zh', '=zh',
    '.zh-hant', '=zh-hant',
]


valid_img_url = [
    '/customers',
    '/partners',
    '/home'
]

def get_driver():
    driver = webdriver.Chrome(PATH)

    options = webdriver.ChromeOptions()
    options.add_argument('--enable-javascript')

    return driver


# Deletes trailing '/' and '#'
def url_rstrip(s):
    return s.rstrip('#').rstrip('/')


# Returns '' if invalid link
# Else, returns corrected link
def check_link(s):
    s = url_rstrip(s)
    
    if not s:
        return ''

    if 'http' not in s:
        if (s[0] == '/' or s[0] == '#') and len(s)>1:
            return url + s
        return ''
    
    for inv in invalid_mid:
        if inv in s:
            return ''

    for ext in invalid_ext:
        if s.endswith(ext):
            return ''

    for seg in s.split('/'):
        if seg and (seg in invalid_seg or seg[0] in invalid_seg_start):
            return ''

    ########################################
    ## (WIP) Advanced url filtering algos ##
    ########################################
        
    return s


def check_img(root, url):
    if root == url:
        return True
    for inv in valid_img_url:
        if inv in url:
            return True
    return False


# Placeholder until we can read PDFs successfully
def get_pdf(url):
    return PDF_READER.read_pdf(url)


# Returns all href attribute of all anchor elements
def get_hrefs(driver):
    hrefs = []
    elems = driver.find_elements_by_tag_name('a')

    for elem in elems:
        try:
            href = check_link(elem.get_attribute('href'))
            if href:
                hrefs.append(href)
        except:
            pass

    return hrefs


def get_web_imgs(driver):
    html = ''
    elems = driver.find_elements_by_tag_name('img')
    for elem in elems:
        src = elem.get_attribute('src')
        if src:        
            md5 = get_md5(src)
            if md5 not in CHECKSUMS:
                CHECKSUMS[md5] = src
                try:
                    html += REVERSE_SEARCH.search(src) + '\n'
                    print('[IMG]', src)
                except Exception as e:
                    print(e)

    return html


# Returns HTML title text
def get_title(driver):
    try:
        if driver.find_elements_by_tag_name('title'):
            return driver.find_element_by_css_selector('title').text + ' '
    except:
        pass
    return ''


# Returns HTML body text
def get_body(driver):
    return driver.find_element_by_css_selector('body').text    


# Generate MD5 hash value to prevent visiting websites with different URLs but same content
def get_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


# Remove space
# DOM length
# 3 diff segments
def html_id(s):
    s = s.replace(' ', '').replace('\n', '')
    n = len(s)
    if n > 20:
        return '{}{}{}{}'.format(n, s[:5], s[(n//2)-4:(n//2)+4], s[-5:])
    return s


def process_site(driver, root, url, expand):
    global HTML

    html_text = ''
    
    try:
        driver.get(url)
    except:
        pass
    
    if url.endswith('.pdf'):
        html_text += get_pdf(url)
    else:
        html_text += get_title(driver) + ' ' + get_body(driver)

    md5_html = get_md5(html_id(html_text))

    if md5_html in CHECKSUMS:
        print('[-]', url, '<--->', CHECKSUMS[md5_html])
        EDGES.pop(url, None)
        return

    if check_img(root, url):
        html_text += get_web_imgs(driver)

    CHECKSUMS[md5_html] = url
    HTML += TRANSLATOR.translate(html_text) + '\n'

    if expand:
        for href in get_hrefs(driver):
            if href in SITES or href in url:
                continue
            
            SITES.append(href)
            EDGES[href] = url
            

def crawl_company(driver, root, company, max_depth):
    print('##############################')
    print('Company:', company)
    print('Root   :', root)
    print('##############################\n')

    global HTML

    driver.get(root)

    HTML = ''
    SITES.clear()
    EDGES.clear()
    CHECKSUMS.clear()
    
    SITES.append(root)
    CHECKSUMS[get_md5(root)] = root

    # iteratively add on the sublinks to our list
    n = 0
    for d in range(max_depth):
        size = len(SITES)
        print('Size:', size-n)
        while n < size:
            print('[+]', SITES[n])
            process_site(driver, root, SITES[n], d<max_depth-1)
            n += 1

    # create edgelist to plot network graph
    df_network = {'Source':[],
                  'Target':[]}
    
    for tgt in list(EDGES.keys()):
        df_network['Source'].append(EDGES[tgt])
        df_network['Target'].append(tgt)

    df_network = pd.DataFrame(df_network)
    df_network.to_csv('{}/{}.csv'.format(EDGE_LIST_DIR, company), index=False)

    G = nx.from_pandas_edgelist(df_network, source='Source', target='Target')
    net = Network('100vh', '100vw')
    net.from_nx(G)
    net.show('{}/{}.html'.format(NETWORK_GRAPH_DIR, company))

    #########################
    ## Translate HTML here ##
    #########################

    with open('{}/{}.txt'.format(HTML_TEXT_DIR, company), 'w', encoding='utf-8') as g:
        g.write(HTML)
        g.close()

    print('Crawled:', len(SITES))
    print()


def main():
    df = pd.read_excel('companies-sensor.xlsx')
    df.dropna(axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['actual_url'] = df['actual_url'].apply(url_rstrip)

    driver = get_driver()
    
    for i, row in df.iloc[1:].iterrows():
        crawl_company(driver, row['actual_url'], row['Company Name'], MAX_DEPTH)
        break
    
    driver.quit()
    REVERSE_SEARCH.quit()

main()    
