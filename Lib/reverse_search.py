from selenium import webdriver
import requests
import random
import time


class ReverseSearch():
    def __init__(self, path):
        self.path = path 
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
        return webdriver.Chrome(self.path)

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

    def get_ext(self, s):
        s = s.lower()
        for ext in ['.jpg', '.png', '.jpeg']:
            if ext in s:
                return ext
        return ''

    def clean_str(self, s):
        if s:
            s = s.lower()
            for r in ['/', '-', '_', ':', '(', ')', '.svg', '.png', '.jpg', '.jpeg']:
                s = s.replace(r, ' ')

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

        ext = self.get_ext(url)
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
        search_value = self.driver.find_element_by_name('q').get_attribute('value')
        result['search_value'] = search_value
        
        # get number of results
        try:
            num_results = self.get_num_results(self.driver.find_element_by_id('result-stats').text)
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

        if len(self.driver.find_elements_by_class_name('xpdopen')) > 0:
            return result

        # if number of results falls within (results_min, results_max), then results are probably irrelevant
        if self.results_min < num_results < self.results_max:
            return result

        # take first search results
        headers = self.driver.find_elements_by_css_selector('div[data-header-feature="0"]')[:1]
        bodies = self.driver.find_elements_by_css_selector('div[data-content-feature="1"]')[:1]
        
        for i in range(len(headers)):
            header = headers[i].find_elements_by_tag_name('h3')[0].text
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

    def random_wait(self, lower=0.5, upper=2):
        return random.random() * (upper-lower) + lower
        
    def reset(self):
        self.driver.quit()
