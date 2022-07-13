import warnings
import json
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import hashlib
from .google_translate import GoogleTranslate
from .reverse_search import ReverseSearch
from .logo_detector import LogoDetector
from .plot_network import plot_network
from .pdf_reader import PDFReader
from .webtree import WebTree
from .functions import *

# ignore all warnings
warnings.filterwarnings('ignore')

# Extract & clean the tail segment of URL (only keep alphanumeric chars)
# Mainly for extracting image filename
def url_tail_condensed(url):
    url = url.split('/')[-1].split('.')[0]
    reconstruct = ''
    for c in url:
        if c.isalnum():
            reconstruct += c
    return reconstruct

# MD5 hash
def get_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

# Generate a short hash value based on HTML content to tag each unique webpage with a unique ID
# Prevents visiting websites with different URLs but same content
# 1) Remove space
# 2) DOM length
# 3) Paste 3 diff segments from content
def content_id(s):
    s = s.replace(' ', '').replace('\n', '')
    n = len(s)
    if n > 20:
        return '{}{}{}{}'.format(n, s[:5], s[(n//2)-4:(n//2)+4], s[-5:])
    return s

class CompanyCrawler():
    def __init__(self, dictionary='companycrawler/json/dictionary.json', save_webtree=False, save_network_graph=True):
        self.save_network_graph = save_network_graph
        self.save_webtree = save_webtree
        self.driver = None
        self.checksums = {}
        self.clients = {}
        self.edges = {}
        self.sites = []
        self.reverse_search = ReverseSearch()
        self.translator = GoogleTranslate()
        self.logo_detector = LogoDetector()
        self.pdf_reader = PDFReader()
        self.web_tree = WebTree()

        with open(dictionary, 'r') as f:
            jsonData = json.load(f)

        self.invalid_seg_start = jsonData['invalid_seg_start']
        self.invalid_seg = jsonData['invalid_seg']
        self.invalid_mid = jsonData['invalid_mid']
        self.valid_img_url =jsonData['valid_img_url']
        self.invalid_ext = jsonData['invalid_ext']
    
    def get_driver(self):
        options = webdriver.chrome.options.Options()
        options.add_argument("--no-sandbox")
        options.add_argument('--enable-javascript')
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Returns '' if invalid URL
    # Else, returns corrected URL
    def check_link(self, url, base):
        if url:
            url = url_rstrip(url)
        else:
            return ''

        if 'http' not in url:
            # sometimes the href is meant to be appended to base URL
            # E.g., /data, #id=3
            if (url[0] == '/' or url[0] == '#') and len(url)>1:
                return base + url
            return ''

        # check for invalid components in URL
        for inv in self.invalid_mid:
            if inv in url:
                return ''
        for ext in self.invalid_ext:
            if url.endswith(ext):
                return ''
        for seg in url.split('/'):
            if seg and (seg in self.invalid_seg or seg[0] in self.invalid_seg_start):
                return ''
        return url

    # check if image is from root URL or in a valid web segment like /customers
    # return True only if valid because this is for client logo detection
    def check_img(self, depth, url):
        if depth == 0:
            return True
        for valid in self.valid_img_url:
            if valid in url:
                return True
        return False

    # Returns HREF attribute of all <a> in driver's current webpage
    def get_hrefs(self):
        hrefs = []
        elems = self.driver.find_elements(By.TAG_NAME, 'a')

        for elem in elems:
            href = self.check_link(elem.get_attribute('href'), self.driver.current_url)
            if href:
                hrefs.append(href)

        return hrefs

    def get_logos(self, company):
        generator = self.web_tree.run_all()
        company_condensed = company.lower().replace(' ', '')
        # for each image cluster ...
        for page, clusters in generator:
            # sort by decreasing length
            clusters.sort(key=len, reverse=True)
            print_header('({}) Image Clusters'.format(len(clusters)))

            for cluster in clusters:
                urls = []
                alts = []
                for img in cluster:
                    # separate alt text from url
                    img = (img + ' ').split(' ')
                    url = img[0]
                    # ignores images with url tail containing company's own name, like the company's own logo, own products etc
                    # however, occasionally the naming convention is like photoneo-toyota.jpg, photoneo-google.jpg, photoneo-siemens.jpg
                    # those clients will be ignored too
                    if company_condensed not in url_tail_condensed(url):
                        urls.append(url)
                        alts.append(img[1].replace('_', ' '))

                if len(urls) >= 2:
                    scores = self.logo_detector.predict(urls)
                    # only allow images with logo probability >0.5 to proceed to reverse search
                    if sum(scores) / len(cluster) > 0.5:
                        print('Reverse search ...')
                        for i in range(len(urls)):
                            md5 = get_md5(urls[i])
                            # check if image has been reverse searched before
                            if md5 not in self.checksums:
                                self.checksums[md5] = urls[i]
                                rs = self.reverse_search.search(urls[i], company)
                                if rs:
                                    # set parent page and alt text before adding to clients
                                    rs['page'] = page
                                    rs['alt'] = alts[i]
                                    self.clients[md5] = rs
                else:
                    for url in urls:
                        print('[X]', url)

    def process_pdfs(self):
        print_header('({}) PDFs'.format(len(self.pdf_reader.pdfs)))
        pdf_generator = self.pdf_reader.read_all_pdfs()
        pdf_json = {}
        count = 1
        for pdf_obj in pdf_generator:
            # translate pdfs
            if pdf_obj:
                pdf_obj['text'] = self.translator.translate(pdf_obj['text'])

                md5 = get_md5(content_id(pdf_obj['text']))
                if md5 not in self.checksums:
                    self.checksums[md5] = pdf_obj['url']
                    pdf_json[str(count)] = pdf_obj
                    count += 1
                else:
                    print('-- DUPLICATE:', self.checksums[md5])

        return pdf_json

    def crawl_site(self, url, depth, expand):
        if is_pdf(url):
            self.pdf_reader.add(url)
            return
        try:
            self.driver.get(url)
        except:
            return

        # extract title & body text to generate hash value for current URL
        html_text = ''
        try:
            html_text += self.driver.find_element(By.CSS_SELECTOR, 'title').text + ' '
        except:
            pass
        html_text += self.driver.find_element(By.CSS_SELECTOR, 'body').text 
        md5_html = get_md5(content_id(html_text))

        # hash value generated from HTML content indicates that current URL has been processed before 
        if md5_html in self.checksums:
            print('-- DUPLICATE:', self.checksums[md5_html])
            self.edges.pop(url, None)
            return
        else:
            self.checksums[md5_html] = url

        # If passes check_img, then there is substantial probability that image is client logo
        # Hence, store in webtree for image clustering, followed by logo detection
        if self.check_img(depth, url):
            self.web_tree.store(url)

        if expand:
            for href in self.get_hrefs():
                if href not in self.sites and href not in url:
                    self.sites.append(href)
                    self.edges[href] = url # Add edge (child : parent)
        return self.translator.translate(html_text) # translate webpage content

    def crawl_company(self, root, company, save_dir, max_depth):
        root = url_rstrip(root)
        print_header(root)
        self.get_driver()
        self.sites.clear()
        self.edges.clear()
        self.clients.clear()
        self.checksums.clear()
        self.sites.append(root)
        self.checksums[get_md5(root)] = root # add root webpage to CHECKSUMS to prevent re-processing root when re-visited

        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        if company not in os.listdir(save_dir):
            os.mkdir(os.path.join(save_dir, company))

        # iteratively add sublinks to our list up to max_depth
        n = 0
        for d in range(max_depth):
            size = len(self.sites)
            print('Size:', size-n)
            while n < size:
                print('[{}] {}'.format(n+1, self.sites[n]))
                html = self.crawl_site(self.sites[n], d, d < max_depth-1)
                if html:
                    # save webpage content into txt file
                    with open(os.path.join(save_dir, company, str(n) + '.txt'), 'w', encoding='utf-8') as g:
                        g.write(self.sites[n] + '\n' + html)
                n += 1

        # start up webdrivers for client detection
        self.web_tree.start()
        self.reverse_search.start()

        self.get_logos(company)

        # close webdrivers
        self.web_tree.reset()
        self.reverse_search.reset()
        
        # save PDF data if have
        if self.pdf_reader.pdfs:
            with open(os.path.join(save_dir, company, company.lower()+'-pdfs.json'), 'w') as g:
                g.write(json.dumps(self.process_pdfs()))

        # close webdrivers
        self.pdf_reader.reset()
        self.driver.quit()

        # save data from detected clients into JSON file
        with open(os.path.join(save_dir, company, company.lower()+'-clients.json'), 'w') as g:
            g.write(json.dumps(self.clients))

        # network graph
        if self.save_network_graph:
            plot_network(os.path.join(save_dir, company, company.lower()), self.edges)
