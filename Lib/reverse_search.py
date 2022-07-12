from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from functions import find_ext
import random
import time
import re


class ReverseSearch():
    def __init__(self):
        self.driver = None
        self.max_requests = 20
        self.curr_requests = 0
        self.processed_requests = 0
        self.results_min = 50
        self.results_max = 1000
        self.visited = []

    def start(self):
        self.driver = self.get_driver()

    def get_driver(self):
        options = webdriver.chrome.options.Options()
        options.add_argument("--no-sandbox")
        options.add_argument('--enable-javascript')
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        return driver

    def filter_search_value(self, search_value):
        invalid = ['vertical', 'horizontal', 'dot', 'language']
        if search_value in invalid:
            return False
        return True

    def filter_header(self, header):
        invalid = ['LinkedIn', 'Font Awesome', 'Definition', 'Meaning', 'Dictionary']
        for inv in invalid:
            if inv in header:
                return False
        return True

    def get_num_results(self, s):
        s = s.strip().replace(',', '')
        for part in s.split():
            if part.isdigit():
                return int(part)
            
        return 0

    def rear_strip(self, s):
        while s and not s[-1].isalnum():
            s = s[:-1]
        return s

    def clean_str(self, s):
        if s:
            s = s.lower()
            s = s.replace('%20', ' ') # %20 is space encoded in url 
            s = re.sub(r'[^.\w\s]|_', ' ', s)
            s = [w for w in s.split() if w.replace('.', '').isalpha()]

            return ' '.join(s)
        
        return ''            
    
    def search(self, url, company=''):
        result = {
            'url': url,
            'url_tail': '',
            'header': '',
            'body': '',
            'search_value': '',
            'results': 0
        }

        ext = find_ext(url)
        result['url_tail'] = self.clean_str(url.split(ext)[0].split('/')[-1])

        if self.curr_requests >= self.max_requests:
            self.curr_requests = 0
            self.driver.quit()
            self.driver = self.get_driver()

        # avoid bot detection by randomising frequency of requests
        # restart browser if self.max_requests reached
        self.random_wait()
        self.processed_requests += 1
        self.curr_requests += 1
        
        self.driver.get('https://www.google.com/searchbyimage?&image_url=' + url)
        
        # get value inside search bar
        search_value = self.driver.find_element(By.NAME, 'q').get_attribute('value')
        result['search_value'] = search_value
        
        # get number of results
        try:
            num_results = self.get_num_results(self.driver.find_element(By.ID, 'result-stats').text)
        except:
            return
        
        result['results'] = num_results

        if search_value in self.visited:
            return result
        else:
            self.visited.append(search_value)

        # ignore company products
        if company and company.lower() in search_value:
            return

        if not self.filter_search_value(search_value):
            return result

        if len(self.driver.find_elements(By.CLASS_NAME, 'xpdopen')) > 0:
            return result

##        # if number of results falls within (results_min, results_max), then results are probably irrelevant
##        if self.results_min < num_results < self.results_max:
##            return result

        # take first search results
        headers = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-header-feature="0"]')[:1]
        bodies = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-content-feature="1"]')[:1]
        
        for i in range(len(headers)):
            header = headers[i].find_elements(By.TAG_NAME, 'h3')[0].text
            header = self.rear_strip(header)

            # take 1st sentence of 1st search result 
            body = bodies[i].text.split('\n')[0]
            body = body.split(' ')

            if not self.filter_header(header):
                continue

            # removes:
            # 5 May 2022 — 
            # 300 x 500 · 
            result['header'] += self.clean_str(header)
            if '·' in body and body.index('·') < 5:
                body = body[body.index('·')+1:]
            if '—' in body and body.index('—') < 5:
                body = body[body.index('—')+1:]

            result['body'] += self.clean_str(' '.join(self.rear_strip(body)))
            
        return result

    # wait for a random duration between lower-upper
    def random_wait(self, lower=0.5, upper=2):
        return time.sleep(random.random() * (upper-lower) + lower)
        
    def reset(self):
        self.driver.quit()