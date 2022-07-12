from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import warnings
import hashlib
import urllib
import json
import time
import sys
import os
import re

lib_dir = os.path.join(os.getcwd(), 'Lib')
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

from functions import *
from webtree import WebTree
from pdf_reader import PDFReader
from logo_detector import LogoDetector
from reverse_search import ReverseSearch
from google_translate import GoogleTranslate
from plot_network import plot_network


#####################
## Modifiable Vars ##
#####################

MAX_DEPTH = 2

SITES = []
EDGES = {}
CLIENTS = {}
CHECKSUMS = {}

REVERSE_SEARCH = ReverseSearch()
WEB_TREE = WebTree()

TRANSLATOR = GoogleTranslate()
LOGO_DETECTOR = LogoDetector()
PDF_READER = PDFReader()

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
    '.jpg', '.jpeg', '.svg', '.png', '.mp4', '.gif', '.zip',
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
    '/home',
    '/clients'
]

def get_driver():
    options = webdriver.chrome.options.Options()
    options.add_argument("--no-sandbox")
    options.add_argument('--enable-javascript')
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    #driver.implicitly_wait(10)
    
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
    elif 'http' not in s:
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

    #########################
    ## more url filtering? ##
    #########################
        
    return s


def check_img(depth, url):
    if depth == 0:
        return True
    for valid in valid_img_url:
        if valid in url:
            return True
    return False

# Returns all href attribute of all anchor elements
def get_hrefs(driver):
    hrefs = []
    elems = driver.find_elements(By.TAG_NAME, 'a')

    for elem in elems:
        try:
            href = check_link(elem.get_attribute('href'))
            if href:
                hrefs.append(href)
        except:
            pass

    return hrefs

def url_tail_condensed(url):
    url = url.split('/')[-1].split('.')[0]
    reconstruct = ''
    for c in url:
        if c.isalnum():
            reconstruct += c
    return reconstruct

def get_logos(web_tree, company):
    generator = web_tree.run_all()
    company_condensed = company.lower().replace(' ', '')
    for page, clusters in generator:
        # sort by decreasing length
        clusters.sort(key=len, reverse=True)
        print('({}) Image Clusters'.format(len(clusters)))

        count = 1
        for cluster in clusters:
            print('Cluster (' + str(count) + ')')
            count += 1
            printed = False
            
            # separate alt text from url
            urls = []
            alts = []
            for img in cluster:
                if ' ' in img:
                    idx = img.index(' ')
                    urls.append(img[:idx])
                    alts.append(img[idx+1:])
                else:
                    urls.append(img)
                    alts.append('')
                    
            # ignores images with url tail containing company's own name, like the company's own logo, own products etc
            # however, occasionally the naming convention is like photoneo-toyota.jpg, photoneo-google.jpg, photoneo-siemens.jpg
            # those clients will be ignored too
            for i in range(len(urls)-1, -1, -1):
                if company_condensed in url_tail_condensed(urls[i]):
                    urls = urls[:i] + urls[i+1:]
                    alts = alts[:i] + alts[i+1:]

            if len(urls) >= 2:
                scores = LOGO_DETECTOR.predict(urls)
                if sum(scores) / len(cluster) > 0.5:
                    print('Reverse search ...')
                    printed = True
                    for i in range(len(urls)):
                        md5 = get_md5(urls[i])
                        
                        if md5 not in CHECKSUMS:
                            CHECKSUMS[md5] = urls[i]
                            rs = REVERSE_SEARCH.search(urls[i], company)
                            if rs:
                                rs['page'] = page
                                rs['alt'] = alts[i]
                                CLIENTS[md5] = rs
                        else:
                            print('-- DUPLICATE:', CHECKSUMS[md5])

            else:
                for url in cluster:
                    print('>', url)
            print()
            

# Returns HTML title text
def get_title(driver):
    try:
        return driver.find_element(By.CSS_SELECTOR, 'title').text
    except:
        return ''


# Returns HTML body text
def get_body(driver):
    return driver.find_element(By.CSS_SELECTOR, 'body').text 


# Generate MD5 hash value to prevent visiting websites with different URLs but same content
def get_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


# Remove space
# DOM length
# 3 diff segments
def content_id(s):
    s = s.replace(' ', '').replace('\n', '')
    n = len(s)
    if n > 20:
        return '{}{}{}{}'.format(n, s[:5], s[(n//2)-4:(n//2)+4], s[-5:])
    return s

def process_pdfs():
    print('({}) PDFs'.format(len(PDF_READER.pdfs)))
    pdf_generator = PDF_READER.read_all_pdfs()
    pdf_json = {}
    count = 1
    for pdf_obj in pdf_generator:
        # translate pdfs
        if pdf_obj:
            pdf_obj['text'] = TRANSLATOR.translate(pdf_obj['text'])

            md5 = get_md5(content_id(pdf_obj['text']))
            if md5 not in CHECKSUMS:
                CHECKSUMS[md5] = pdf_obj['url']
                pdf_json[str(count)] = pdf_obj
                count += 1
            else:
                print('-- DUPLICATE:', CHECKSUMS[md5])

    print()
    
    return pdf_json

def is_pdf(url):
    if url.endswith('.pdf'):
        return True
    elif '.pdf' in url:
        for idx in [x.end() for x in re.finditer('.pdf', url)]:
            if idx < len(url) and not url[idx].isalnum():
                return True
    return False
            

def process_site(driver, web_tree, url, company, depth, expand):
    if is_pdf(url):
        PDF_READER.add(url)
        return
    
    try:
        driver.get(url)
    except:
        return

    html_text = get_title(driver) + ' ' + get_body(driver)
    md5_html = get_md5(content_id(html_text))

    if md5_html in CHECKSUMS:
        print('-- DUPLICATE:', CHECKSUMS[md5_html])
        EDGES.pop(url, None)
        return

    if check_img(depth, url):
        web_tree.store(url)

    CHECKSUMS[md5_html] = url

    if expand:
        for href in get_hrefs(driver):
            if href in SITES or href in url:
                continue
            
            SITES.append(href)
            EDGES[href] = url

    return TRANSLATOR.translate(html_text)
            

def crawl_company(root, company, max_depth):
    box_width = max(len(company), len(root))
    box_str_fmt = '| {: <'+str(box_width)+'} |'
    
    print('+--' + box_width*'-' + '+')
    print(box_str_fmt.format(company))
    print(box_str_fmt.format(root))
    print('+--' + box_width*'-' + '+')
    print('')

    driver = get_driver()
    CLIENTS.clear()
    SITES.clear()
    EDGES.clear()
    CHECKSUMS.clear()
    SITES.append(root)
    CHECKSUMS[get_md5(root)] = root

    if company not in os.listdir(HTML_TEXT_DIR):
        os.mkdir(os.path.join(HTML_TEXT_DIR, company))

    # iteratively add on the sublinks to our list
    n = 0
    for d in range(max_depth):
        size = len(SITES)
        print('Size:', size-n)
        while n < size:
            print('[{}] {}'.format(n+1, SITES[n]))
            html = process_site(driver, WEB_TREE, SITES[n], company, d, d < max_depth-1)
            if html:
                with open(os.path.join(HTML_TEXT_DIR, company, str(n) + '.txt'), 'w', encoding='utf-8') as g:
                    g.write(SITES[n] + '\n' + html)
            n += 1
        print()

    # start up webdrivers
    WEB_TREE.start()
    REVERSE_SEARCH.start()

    get_logos(WEB_TREE, company)

    # close webdrivers
    WEB_TREE.reset()
    REVERSE_SEARCH.reset()

    # clients
    with open(os.path.join(HTML_TEXT_DIR, company, company.lower()+'-clients.json'), 'w') as g:
        g.write(json.dumps(CLIENTS))
        
##    # PDFs
##    with open(os.path.join(HTML_TEXT_DIR, company, company.lower()+'-pdfs.json'), 'w') as g:
##        g.write(json.dumps(process_pdfs()))
##
##    PDF_READER.reset()

    # network graph
    plot_network(company, EDGES)
##    # create edgelist to plot network graph
##    df_network = {'Source':[],
##                  'Target':[]}
##    
##    for tgt in list(EDGES.keys()):
##        df_network['Source'].append(EDGES[tgt])
##        df_network['Target'].append(tgt)
##
##    df_network = pd.DataFrame(df_network)
##    df_network.to_csv('{}/{}.csv'.format(EDGE_LIST_DIR, company), index=False)
##
##    G = nx.from_pandas_edgelist(df_network, source='Source', target='Target')
##    net = Network('100vh', '100vw')
##    net.from_nx(G)
##    net.show('{}/{}.html'.format(NETWORK_GRAPH_DIR, company))


    driver.quit()

def main():
    # ignore all warnings
    warnings.filterwarnings("ignore")
    
##    df = pd.read_excel('companies-software.xlsx')
##    df.dropna(axis=0, inplace=True, subset=['actual_url'])
##    df.reset_index(drop=True, inplace=True)
##    df['actual_url'] = df['actual_url'].apply(url_rstrip)
##
##    for i, row in df.iloc[29:49].iterrows():
##        crawl_company(row['actual_url'], row['Company Name'], MAX_DEPTH)
##        time.sleep(3)

    crawl_company('https://www.intermodalics.eu/', 'Intermodalics', 2)


#main()    
