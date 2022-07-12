# NLP-Webscraper

## Packages & Methods
### 1. reverse_search
```ReverseSearch.get_driver()```
- Set Selenium webdriver options & returns webdriver object
<!-- -->

```ReverseSearch.start()```
- Start Selenium webdriver
<!-- -->

```ReverseSearch.filter_search_value(str: search_value)``` 
- Return False if search_value contains an invalid word like "dictionary", "horizontal"
<!-- -->

```ReverseSearch.filter_header(str: header)``` 
- Return False if header contains invalid word (usually company names like "LinkedIn", "FontAwesome")
<!-- -->

```ReverseSearch.rear_strip(String: s)``` 
- Removes non-alphanumeric characters from the rear, like "..."
<!-- -->

```ReverseSearch.get_num_results(String: s)``` 
- Returns number of reverse search results based on DOM element #result-stats
<!-- -->

```ReverseSearch.clean_str(String: s)```
- Lowercase
- Replaces escape character "%20" commonly found in URLs
- Remove non-alphanumeric & underscore characters
- Removes numerals & floats
<!-- -->

```ReverseSearch.search(String: url, String: company="")```
- Returns {\
    &nbsp;&nbsp;&nbsp;&nbsp;'url': //image url\
    &nbsp;&nbsp;&nbsp;&nbsp;'url_tail': //cleaned image filename\
    &nbsp;&nbsp;&nbsp;&nbsp;'header': //title of first search result\
    &nbsp;&nbsp;&nbsp;&nbsp;'body': //body text of 1st search result\
    &nbsp;&nbsp;&nbsp;&nbsp;'search_value': //value in search box as interpreted by Google\
    &nbsp;&nbsp;&nbsp;&nbsp;'results': //number of search results\
  }
<!-- -->

```ReverseSearch.random_wait(Float: lower=0.5, Float: upper=2)```
- Wait for a random duration between lower & upper
<!-- -->

```ReverseSearch.reset()```
- Close webdriver
<!-- -->

### 2) webtree
```WebTree(Boolean: save=False)```
- Save file as <gen_link()>.json if save is True
<!-- -->

```WebTree.start()```
- Start Selenium webdriver
<!-- -->

```WebTree.store(String: url)```
- Store URL in list to crawl all at once
<!-- -->

```WebTree.run_all()```
- Generator that yields get_cluster() results for each stored URL
<!-- -->

```WebTree.is_src(String: src)```
- Returns if src is image
<!-- -->

```WebTree.get_src(Object: elem)```
- Return ```"<image_url> <image_alt>"```
<!-- -->

```WebTree.get_clusters(String: url)```
- Detect & return image clusters (list of list of image URLs) from a web page
<!-- -->

```WebTree.build_tree(String: url)```
- Map out web tree of a web page
- If self.save, save web tree as JSON file
<!-- -->

```WebTree.reset()```
- Close webdriver
<!-- -->

## Updates
Update [10/05/22]
- Selenium framework
- [**get_sublinks.py**] extracts all sublinks up to a specified depth from the root node
- [**Network Graphs/\*.html**] Plots the sublinks in a network graph (download **Network Graphs/\*.html** and run it on localhost)
- [**Edgelist/\*.csv**] Generates csv with all graph edges for tracking of sublinks
- [**company_website_searcher**] Finds company website based on company name. Requires manual checking though
- [**Companies/companies-sensor.xlsx**] - actual company websites for software
- [**Companies/companies-software.xlsx**] - actual company websites for sensors (missing for Paracosm)

Update [11/05/22]
- Added functions to cut down on amount of similar sites visited with the **same content** by comparing md5 hash value of self-generated html-id ```<length of DOM><first 5 char><middle 9 char><last 5 char>```
for quicker hashing
- Translates websites which are in other languages to english after scrapping the data

Update [12/05/22]
- [**pdf_reader.py**] Reads PDF text + extract text from PDF images using Tesseract OCR
- [**reverse_search.py**] Exploring automated Google reverse image search on brand images to identify customers which are represented in image form

Update [18/05/22]
- Revamped **reverse search** algorithm
  - Filters results based on number of reverse search hits
  - Filters out false positives
- Improved **entity detection system**
  - 3 Tiers of detection
    - Tier 1: Alt text (img meta data) > Header (reverse search) > Body (reverse search)
    - Tier 2: Identify common words from image file name & reverse search value
    - Tier 3: Purely file name

Update [20/05/22]
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

Update [23/05/22]
- Get surrounding text of keywords
- Experimenting with Python NLP library gensim to filter text as well
- Tested client extraction pipeline on all sensor companies

Update [12/07/22]
- Replaced deprecated Selenium code with updated versions
