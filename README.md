# NLP-Webscraper
Python 3.9

### Dependencies
```text
selenium==4.3.0
webdriver-manager==3.8.0
googletrans==4.0.0rc1
langdetect==1.0.9
pandas==1.3.1
pytesseract==0.3.9
requests==2.27.1
Pillow==9.1.0
numpy==1.19.5
opencv-python==4.5.3
tensorflow==2.6.0
PyPDF2==1.27.12
fitz
pyvis==0.2.0
networkx==2.8
```

### Windows
```console
pip install -r requirements.txt
```

### Pytesseract setup
- Download [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)
- Run installer to install Tesseract-OCR executable
- Modify `"pytesseract-path"` in [companycrawler/json/functions-config.json](https://github.com/axwhyzee/NLP-Webscraper/blob/main/companycrawler/json/functions-config.json)
<!-- -->

# Company Crawler 

## Usage
Crawl single company
```python
from companycrawler.crawler import CompanyCrawler
    
CC = CompanyCrawler(save_webtree=False, save_network_graph=True)
CC.crawl_company(
    root='https://www.intermodalics.eu/', 
    company='intermodalics', 
    save_dir='saved_data',
    max_depth=2
)
```

Crawl list of companies in excel
```python
from companycrawler.crawler import CompanyCrawler
import pandas as pd

# define variables
save_dir = 'saved_data'
max_depth = 2

CC = CompanyCrawler(save_webtree=False, save_network_graph=True)

# load & clean excel data from 'companies-software.xlsx'
df = pd.read_excel('companies-software.xlsx')
df.dropna(axis=0, inplace=True, subset=['actual_url'])
df.reset_index(drop=True, inplace=True)

# enumerate rows in excel
for i, row in df.iterrows():
    CC.crawl_company(
        root=row['actual_url'], 
        company=row['Company Name'], 
        save_dir=save_dir,
        max_depth=max_depth
    )
```

## Company Crawler submodules
### companycrawler.reverse_search
`ReverseSearch.get_driver()`
- Set Selenium webdriver options & returns webdriver object
<!-- -->

`ReverseSearch.start()`
- Start Selenium webdriver
<!-- -->

`ReverseSearch.filter_search_value(str: search_value)`
- Return False if `search_value` contains an invalid word like "dictionary", "horizontal"
<!-- -->

`ReverseSearch.filter_header(str: header)` 
- Return False if title of 1st search result contains invalid word (usually company names like "LinkedIn", "FontAwesome")
<!-- -->

`ReverseSearch.rear_strip(String: s)`
- Removes non-alphanumeric characters from the rear, like "..."
<!-- -->

`ReverseSearch.get_num_results(String: s)` 
- Returns number of reverse search results based on text of DOM element #result-stats
<!-- -->

`ReverseSearch.clean_str(String: s)`
- Lowercase
- Replaces escape character "%20" commonly found in URLs
- Remove non-alphanumeric & underscore characters
- Removes numerals & floats
<!-- -->

`ReverseSearch.search(String: url, String: company="")`
- Returns {\
    &nbsp;&nbsp;&nbsp;&nbsp;'url': //image url\
    &nbsp;&nbsp;&nbsp;&nbsp;'url_tail': //cleaned image filename\
    &nbsp;&nbsp;&nbsp;&nbsp;'header': //title of first search result\
    &nbsp;&nbsp;&nbsp;&nbsp;'body': //body text of 1st search result\
    &nbsp;&nbsp;&nbsp;&nbsp;'search_value': //value in search box as interpreted by Google\
    &nbsp;&nbsp;&nbsp;&nbsp;'results': //number of search results\
  }
<!-- -->

`ReverseSearch.random_wait(Float: lower=0.5, Float: upper=2)`
- Wait for a random duration between `lower` & `upper`
<!-- -->

`ReverseSearch.reset()`
- Close webdriver
<!-- -->

### Usage
```python
RS = ReverseSearch()
RS.start()
results = RS.search('https://images.squarespace-cdn.com/content/v1/5ab393009f87708addd204e2/1523980229490-KB8R24FUGXC8X6DDZ7EC/colruyt_groupB.png?format=300w', 'Intermodalics')
print(results)
RS.reset()
```
### companycrawler.webtree
`WebTree(Boolean: save=False)`
- Save file as <gen_link()>.json if save is True
<!-- -->

`WebTree.start()`
- Start Selenium webdriver
<!-- -->

`WebTree.store(String: url)`
- Store URL in list to crawl all at once
<!-- -->

`WebTree.run_all()`
- Generator that yields url, get_cluster(url) for each stored URL
<!-- -->

`WebTree.is_src(String: src)`
- Returns if src is image
<!-- -->

`WebTree.get_src(Object: elem)`
- Return `"<image_url> <image_alt>"`
<!-- -->

`WebTree.get_clusters(String: url)`
- Detect & return image clusters (list of list of image URLs) from a web page
<!-- -->

`WebTree.build_tree(String: url)`
- Map out web tree of a web page
- If self.save, save web tree as JSON file
<!-- -->

`WebTree.reset()`
- Close webdriver
<!-- -->

### Usage
Map out the web tree of https://www.intermodalics.eu/
```python
WT = WebTree(save=True)
WT.start()
clusters = WT.get_clusters('https://www.intermodalics.eu/')
print(clusters)
WT.reset()
```

Map out the web trees of https://www.intermodalics.eu/ and https://www.intermodalics.eu/visual-positioning-slam-navigation
```python
WT = WebTree(save=True)
WT.start()
WT.store('https://www.intermodalics.eu/')
WT.store('https://www.intermodalics.eu/visual-positioning-slam-navigation')

generator = WT.run_all()
for page, clusters in generator:
    print('Image clusters of', page)
    for image_url in clusters:
        print(image_url)
        
WT.reset()
```
### companycrawler.logo_detector
`LogoDetector(String: saved_model)`
- `saved_model`: path to saved CNN model relative to where this object is being called from
<!-- -->

`LogoDetector.prepare_img(String: src)`
- 1) Download image
- 2) Convert image to RGB
- 3) Resize according to self.dims (100,100,3)
- 4) Return image data, download path (so it can be deleted after detection model runs)
<!-- -->

`LogoDetector.predict(List: srcs, Boolean: verbose)`
- Runs CNN logo detection model on each image in `srcs`
- Returns 1D list of probabilities of each image being a logo
- Print scores if verbose
<!-- -->

### Usage
```python
LD = LogoDetector()
predictions = LD.predict([
    'https://images.squarespace-cdn.com/content/v1/5ab393009f87708addd204e2/1523980229490-KB8R24FUGXC8X6DDZ7EC/colruyt_groupB.png?format=300w',
    'https://images.squarespace-cdn.com/content/v1/5ab393009f87708addd204e2/1522415419883-R8K5KQVMGX48TPWP58X0/b49602d4-9b0a-24f3-8260-933b31b8d160_COM_6calibrations_2018-01-24-13-55-00+-+dev+room.png?format=500w'\
])
print(predictions) # [0.8967107, 0.07239765]
```

### companycrawler.google_translate

`GoogleTranslate.get_chunk()`
- Return chunk of string of length self.max_char
<!-- -->

`GoogleTranslate.load_lines(String: text)`
- Store `text` as sentences in self.lines
<!-- -->

`GoogleTranslate.translate(String: text)`
- Detect language. If not EN, translate chunk by chunk using gooogletrans API
<!-- -->

### Usage
```python
GT = GoogleTranslate()
f = open(text_file, 'r', encoding='utf-8')
text = f.read()
f.close()
translation = GT.translate(text)
print(translation)
```

### 5. companycrawler.plot_network
`plot_network(String: filename, Object: edges)`
- `filename`: Save as network graph as `filename`.html & edge list as `filename`.csv
- `edges`: \<target\>:\<source\> key pairs where \<target\> = sublink found on \<source\> page
<!-- -->

### Usage
```python
# target:source
edges = {
    'https://www.intermodalics.eu/what-we-do': 'https://www.intermodalics.eu/',
    'https://www.intermodalics.eu/join-us': 'https://www.intermodalics.eu/',
    'https://www.intermodalics.eu/team': 'https://www.intermodalics.eu/',
    'https://www.intermodalics.eu/senior-software-developer-robotics': 'https://www.intermodalics.eu/join-us'
}
plot_network('my_network_graph', edges)
```
<img width="446" alt="image" src="https://user-images.githubusercontent.com/34325457/178471141-cbf18006-67ff-47b0-a100-daba8daf9bdf.png">

### 6. companycrawler.pdf_reader
`PDFReader.add(String: url)`
- Adds PDF URL to `self.pdfs`
<!-- -->

`PDFReader.cleanText(String: url)`
- Adds PDF URL to `self.pdfs`
- Cleans text
- 1) Lowercase
- 2) Remove non-alphanumeric & underscore chars 
- 3) Remove consecutive newlines & lines with only 1 character
<!-- -->


`PDFReader.extract_text(String: path)`
- Converts PDF file at `path` to text
- For every page, read all text + append image_to_text at end
- Images should be pre-downloaded in `self.pdf_dir`
- Once completed, delete PDF
<!-- -->

`PDFReader.save_imgs(String: path)`
- Downloads all images from PDF file at `path` into `self.pdf_dir`
<!-- -->

`PDFReader.read_all_pdfs()`
- For each url in `self.pdfs`, downloads PDF at url and saves PDF images in `self.pdf_dir`
- Generator. Yields: {\
      &nbsp;&nbsp;&nbsp;&nbsp;'url': //PDF url\
      &nbsp;&nbsp;&nbsp;&nbsp;'text': //PDF text (including image_to_text)\
  }
<!-- -->

`PDFReader.reset()`
- Empties `self.pdfs`
<!-- -->

### Usage
```python
PR = PDFReader()
PR.add('https://www.memoori.com/wp-content/uploads/2017/10/The-Future-Workplace-2017-Synopsis.pdf')
generator = PR.read_all_pdfs()
for obj in generator:
    print(obj['url'])
    print(obj['text'])
PR.reset()
```

### 7. companycrawler.crawler
`CompanyCrawler(String:  dictionary="companycrawler/json/dictionary.json", 
                Boolean: save_webtree=False, 
                Boolean: save_network_graph=True)`
- `dictionary`:         file path of dictionary.json, a keyword store, relative to where this object is being called from
- `save_webtree`:       save webtree data as JSON if True
- `save_network_graph`: save network graph as <company_name>.HTML & <company_name>.csv if True
<!-- -->

`CompanyCrawler.get_driver()`
- Start Selenium webdriver
<!-- -->

`CompanyCrawler.check_link(String: url, String: base)`
- `url`: an `<a>` element's href
- `base`: URL of web page from which the `<a>` is taken from
<!-- -->

`CompanyCrawler.check_img(Integer: depth, String: url)`
- Check if image is from root URL or in a valid web segment like /customers
- Return True only if valid because this is for client logo detection
<!-- -->

`CompanyCrawler.get_hrefs()`
- Return HREF attribute of all <a> in driver's current webpage
<!-- -->

`CompanyCrawler.get_logos(String: company)`
- Get image clusters from WebTree's stored URLs for a particular `company`
- Run logo detection model & identify image clusters with average logo probability > 0.5
- Reverse search on filtered images and append results to `self.clients`
<!-- -->

`CompanyCrawler.process_pdfs()`
 - Run `read_all_pdfs()` on stored PDF urls in PDFReader() to extract all PDF data
<!-- -->
    
`CompanyCrawler.crawl_site(String: url, Integer: depth, Boolean: expand)`
- `url`: URL to crawl
- `depth`: Current web depth from root
- `expand`: Whether max crawling depth has been reached. If not reached, continue adding sublinks `self.sites` to crawl
- Crawls `url` to:
  1. add itself to `self.pdf_reader` if self is PDF
  2. extract HTML content (translate if applicable)
  3. store images in `self.web_tree` if they pass `self.check_link()`
  4. add sublinks to `self.sites` & `self.edges` if expand=True
   
`CompanyCrawler.crawl_company(String: root, String: company, String: save_dir, Integer: max_depth)`
- `root`: Base URL
- `company`: Name of company being crawled
- `save_dir`: Directory path to save all crawled data at
- `max_depth`: Max crawling depth from `root`
- Process:
  1. Clear cache
  2. Collate & crawl all sublinks up to max depth. In the process: 
     1. Add potential client logos to `self.web_tree` 
     2. Add PDFs to `self.pdf_reader`
     3. Save HTML data of all crawled pages as .txt files
  3. Run `self.get_logos()` to get client data:
     1. `WebTree.run_all()` to build web trees, solve image clusters
     2. Pass image clusters to `self.logo_detector` to filter clusters with average logo probability > 0.5
     3. Conduct reverse search using `self.reverse_search.search()` to acquire client data from image URLs
<!-- -->
    
### Usage
```python
CC = CompanyCrawler(dictionary='/json/dictionary.json') # Adjust filepath depending on relative location of parent process
CC.crawl_company(root='http://aisle411.com/', company='Aisle411', save_dir='../', max_depth=2)
```
    
### 8. companycrawler.functions

`img_to_text(string: path)`
- Converts image to text of image at local `path` using PyTesseract
<!-- -->

`gen_path(String: ext="")`
- Takes in extension `ext` (E.g., ".jpg") and outputs a random vacant filename of type `ext`
<!-- -->

`download_url(String: url, String: save_path)`
- Download file at `url` to `save_path`
- PDFs, images...
<!-- -->

`find_ext(String: path)`
- Returns extension if file at path is an image
<!-- -->

`is_pdf(String: url)`
- Returns whether file at `url` is PDF
<!-- -->

`url_rstrip(String: s)`
- Deletes trailing '/' and '#' from `s`
<!-- -->

`print_header(String: header)`
- Displays `header` with styling
<!-- -->

# Client Extraction

## Usage
```python
from clientextraction.json_extraction import clients_from_json, print_clients
import pandas as pd # for saving client data to csv
import os

# set variables
data_path = 'saved_data' # directory containing all scraped client data
companies = os.listdir(data_path) # list of companies to extract clients from. Requires existing <data_path>/<company>/clients.json
client_output_path = 'clients.csv' # output file

results = {
    'url': [],
    'page': [],
    'alt': [],
    'url_tail': [],
    'common': []
}

# for each company data folder found in data_path, 
# extract client data from each company's clients.json
for company in companies:
    clients = clients_from_json(os.path.join(data_path, company, 'clients.json'), company)
    results['url'].extend(clients['url'])
    results['page'].extend(clients['page'])
    results['alt'].extend(clients['alt'])
    results['url_tail'].extend(clients['url_tail'])
    results['common'].extend(clients['common'])
    #print_clients(clients)

# save client data to csv at client_output_path
client_df = pd.DataFrame(results)
client_df.to_csv(client_output_path, index=False, encoding='utf-8-sig')
```

## Client Extraction submodules
### clientextraction/json_extraction.py
`clean(String: s)`
- 1) Lowercase
- 2) Remove chars that are (non-alphanumeric && not spaces && not periods) OR (underscores) // r'[^.\w\s]|_'
- 3) Remove excess spaces
<!-- -->
    
`form_sentences(String: s, Integer: min_tokens=3, Integer: min_token_len=1)`
- Split `s` by \n
- Remove sentences where number of words < `min_tokens`
- Remove words where length of word < `min_token_len`
<!-- -->
    
`find_ext(String: path)`
- Return extension if file at `path` is image, else ""
<!-- -->
    
`get_url_tail(String: s)`    
- Return cleaned, tail segment of a URL
- Mainly for getting image filename from a URL
<!-- -->
    
`exclude_words(String: words, List: exclude_list)`    
- Remove words from a list that are found inside exclude_list
<!-- -->

`print_header(String: header)`
- Displays header with styling
<!-- -->

`print_clients(Object: results)`
- Displays list of clients with styling
<!-- -->
    
`clients_from_json(String: file, String: company)`
- Extracts clients based on client data at `file` based on:
  1. Reverse search results
  2. Reverse search value
  3. Alt text
  4. Image filename (or URL tail)
  5. Frequency list of keywords (including bigrams & trigrams)
<!-- -->
    
# Updates
### Update [10/05/22]
- Selenium framework
- [**get_sublinks.py**] extracts all sublinks up to a specified depth from the root node
- [**Network Graphs/\*.html**] Plots the sublinks in a network graph (download **Network Graphs/\*.html** and run it on localhost)
- [**Edgelist/\*.csv**] Generates csv with all graph edges for tracking of sublinks
- [**company_website_searcher**] Finds company website based on company name. Requires manual checking though
- [**Companies/companies-sensor.xlsx**] - actual company websites for software
- [**Companies/companies-software.xlsx**] - actual company websites for sensors (missing for Paracosm)

### Update [11/05/22]
- Added functions to cut down on amount of similar sites visited with the **same content** by comparing md5 hash value of self-generated html-id `<length of DOM><first 5 char><middle 9 char><last 5 char>`
for quicker hashing
- Translates websites which are in other languages to english after scrapping the data

### Update [12/05/22]
- [**pdf_reader.py**] Reads PDF text + extract text from PDF images using Tesseract OCR
- [**reverse_search.py**] Exploring automated Google reverse image search on brand images to identify customers which are represented in image form

### Update [18/05/22]
- Revamped **reverse search** algorithm
  - Filters results based on number of reverse search hits
  - Filters out false positives
- Improved **entity detection system**
  - 3 Tiers of detection
    - Tier 1: Alt text (img meta data) > Header (reverse search) > Body (reverse search)
    - Tier 2: Identify common words from image file name & reverse search value
    - Tier 3: Purely file name

### Update [20/05/22]
- **Web tree**
  - Map out web elements in a tree to identify image clusters with a breadth-first approach
  - Motivation: Images, especially brand logos, come in clusters. By pruning irrelevant image clusters, we can sharply improve our client extraction accuracy
  - Used in conjunction with our CNN logo detection models
- **Logo detection**
  - Filters out irrelevant image clusters so we can reduce false positives during client extraction
  - Convolutionary Neural Network model
  - ~80% accuracy
  - Trained on images scraped from the given 120 company websites
  - Evaluates the probability of each image cluster being the client logo cluster

### Update [23/05/22]
- Get surrounding text of keywords
- Experimenting with Python NLP library gensim to filter text as well
- Tested client extraction pipeline on all sensor companies

### Update [12/07/22]
- Replaced deprecated Selenium code with updated versions
