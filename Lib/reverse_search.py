from selenium import webdriver
import requests
import random
import time


class ReverseSearch():
    def __init__(self):
        self.driver = self.get_driver()
        self.max_requests = 20
        self.curr_requests = 0
        self.processed_requests = 0

    def get_driver(self):
        return webdriver.Chrome('C:\Program Files (x86)\chromedriver.exe')

    def search(self, url):
        text = ''
        if self.curr_requests >= self.max_requests:
            self.curr_requests = 0
            self.driver.quit()
            self.driver = self.get_driver()
            
        self.random_wait()
        
        self.driver.get('https://www.google.com/searchbyimage?&image_url=' + url)
        search_div = self.driver.find_element_by_id('search')
        elems = search_div.find_elements_by_tag_name('span')
        for elem in elems:
            text += elem.text.strip() + '\n'

        self.processed_requests += 1
        self.curr_requests += 1

        # removes excessive '\n's
        return '\n'.join(text.split('\n')) + '\n'

    def random_wait(self, lower=0.5, upper=2):
        return random.random() * (upper-lower) + lower
        

    def quit(self):
        self.driver.quit()
        
#RS = ReverseSearch()
#print(RS.search('https://images.squarespace-cdn.com/content/v1/5ab393009f87708addd204e2/1523980229490-KB8R24FUGXC8X6DDZ7EC/colruyt_groupB.png?format=500w'))

