#############
## Imports ##
#############

from selenium import webdriver
import pandas as pd
import warnings
import hashlib
import urllib
import json
import sys
import os
import re

lib_dir = os.path.join(os.getcwd(), 'Lib')
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

from img_processing import *
from genpath import gen_path


#####################
## Modifiable Vars ##
#####################

PATH = 'C:\Program Files (x86)\chromedriver.exe'
MAX_DEPTH = 2

SITES = []
EDGES = {}
CLIENTS = {}
CHECKSUMS = {}

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
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument('--enable-javascript')
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(PATH, options=options)
    
    return driver

# Deletes trailing '/' and '#'
def url_rstrip(s):
    return s.rstrip('#').rstrip('/')


# Returns '' if invalid link
# Else, returns corrected link
def check_link(url, s):
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
    elems = driver.find_elements_by_tag_name('a')

    for elem in elems:
        try:
            href = check_link(driver.current_url, elem.get_attribute('href'))
            if href:
                hrefs.append(href)
        except:
            pass

    return hrefs
            

# Returns HTML title text
def get_title(driver):
    try:
        return driver.find_element_by_css_selector('title').text
    except:
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
def content_id(s):
    s = s.replace(' ', '').replace('\n', '')
    n = len(s)
    if n > 20:
        return '{}{}{}{}'.format(n, s[:5], s[(n//2)-4:(n//2)+4], s[-5:])
    return s

def is_pdf(url):
    if url.endswith('.pdf'):
        return True
    elif '.pdf' in url:
        for idx in [x.end() for x in re.finditer('.pdf', url)]:
            if idx < len(url) and not url[idx].isalnum():
                return True
    return False

def is_src(src):
    for ext in ['.jpg', '.jpeg', '.png']:
        if ext in src:
            return True
    return False

def get_src(elem):
    src = elem.get_attribute('src')
    alt = ''
    try:
        alt = elem.get_attribute('alt')
    except:
        print('No alt text')
        
    if not src or not is_src(src):
        src = elem.get_attribute('data-lazy-src')
    if not src or not is_src(src):
        src = elem.get_attribute('data-src')
    if is_src(src):
        return src
    return ''

done = []
def process_site(driver, url, company, depth, expand):
    if is_pdf(url):
        return
    
    try:
        driver.get(url)
    except:
        return

    html_text = get_title(driver) + ' ' + get_body(driver)
    md5_html = get_md5(content_id(html_text))

    if md5_html in CHECKSUMS:
        print('-- DUPLICATE:', CHECKSUMS[md5_html])
        return
    
    imgs = driver.find_elements_by_tag_name('img')
    for img in imgs:
        try:
            src = get_src(img)
            ext = find_ext(src)
            
            if ext and src not in done:
                done.append(src)
                path = gen_path(ext)
                download_url(src, path)
                print(src)
        except Exception as e:
            pass

    if expand:
        for href in get_hrefs(driver):
            if href in SITES or href in url:
                continue

            if check_img(depth+1, href):
                SITES.append(href)
    

def crawl_company(root, company, max_depth):
    box_width = max(len(company), len(root))
    box_str_fmt = '| {: <'+str(box_width)+'} |'
    
    print('+--' + box_width*'-' + '+')
    print(box_str_fmt.format(company))
    print(box_str_fmt.format(root))
    print('+--' + box_width*'-' + '+')
    print('')

    done.clear()
    driver = get_driver()
    CLIENTS.clear()
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
            print('[{}] {}'.format(n+1, SITES[n]))
            process_site(driver, SITES[n], company, d, d < max_depth-1)
            n += 1
        print()

    driver.quit()

def main():
    # ignore all warnings
    warnings.filterwarnings("ignore")
    
    df = pd.read_excel('companies-sensor.xlsx')
    df.dropna(axis=0, inplace=True, subset=['actual_url'])
    df.reset_index(drop=True, inplace=True)
    df['actual_url'] = df['actual_url'].apply(url_rstrip)

    for i, row in df.iterrows():
        crawl_company(row['actual_url'], row['Company Name'], MAX_DEPTH)


main()    
