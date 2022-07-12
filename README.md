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
- Return False if ```search_value``` contains an invalid word like "dictionary", "horizontal"
<!-- -->

```ReverseSearch.filter_header(str: header)``` 
- Return False if title of 1st search result contains invalid word (usually company names like "LinkedIn", "FontAwesome")
<!-- -->

```ReverseSearch.rear_strip(String: s)``` 
- Removes non-alphanumeric characters from the rear, like "..."
<!-- -->

```ReverseSearch.get_num_results(String: s)``` 
- Returns number of reverse search results based on text of DOM element #result-stats
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
- Wait for a random duration between ```lower``` & ```upper```
<!-- -->

```ReverseSearch.reset()```
- Close webdriver
<!-- -->

### Usage
```
RS = ReverseSearch()
RS.start()
results = RS.search('https://images.squarespace-cdn.com/content/v1/5ab393009f87708addd204e2/1523980229490-KB8R24FUGXC8X6DDZ7EC/colruyt_groupB.png?format=300w', 'Intermodalics')
print(results)
RS.reset()
```
### 2. webtree
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
- Generator that yields url, get_cluster(url) for each stored URL
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

### Usage
Map out the web tree of "https://www.intermodalics.eu/"
```
WT = WebTree(save=True)
WT.start()
clusters = WT.get_clusters('https://www.intermodalics.eu/')
print(clusters)
WT.reset()
```

Map out the web trees of https://www.intermodalics.eu/ and https://www.intermodalics.eu/visual-positioning-slam-navigation
```
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
### 3. logo_detector
```LogoDetector.prepare_img(String: src)```
- 1) Download image
- 2) Convert image to RGB
- 3) Resize according to self.dims (100,100,3)
- 4) Return image data, download path (so it can be deleted after detection model runs)
<!-- -->

```LogoDetector.predict(List: srcs)```
- Runs CNN logo detection model on each image in ```srcs```
- Returns 1D list of probabilities of each image being a logo
<!-- -->

### Usage
```
LD = LogoDetector()
predictions = LD.predict([
    'https://images.squarespace-cdn.com/content/v1/5ab393009f87708addd204e2/1523980229490-KB8R24FUGXC8X6DDZ7EC/colruyt_groupB.png?format=300w',
    'https://images.squarespace-cdn.com/content/v1/5ab393009f87708addd204e2/1522415419883-R8K5KQVMGX48TPWP58X0/b49602d4-9b0a-24f3-8260-933b31b8d160_COM_6calibrations_2018-01-24-13-55-00+-+dev+room.png?format=500w'\
])
print(predictions) # [0.8967107, 0.07239765]
```

### 4. google_translate

```GoogleTranslate.get_chunk()```
- Return chunk of string of length self.max_char
<!-- -->

```GoogleTranslate.load_lines(String: text)```
- Store ```text``` as sentences in self.lines
<!-- -->

```GoogleTranslate.translate(String: text)```
- Detect language. If not EN, translate chunk by chunk using gooogletrans API
<!-- -->

### Usage
```
GT = GoogleTranslate()
f = open(text_file, 'r', encoding='utf-8')
text = f.read()
f.close()
translation = GT.translate(text)
print(translation)
```

### 5. plot_network
```plot_network(String: filename, Object: edges)```
- ```filename```: Save as network graph as ```filename```.html & edge list as ```filename```.csv
- ```edges```: \<target\>:\<source\> key pairs where \<target\> = sublink found on \<source\> page
<!-- -->

### Usage
```
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

### 6. genpath
```gen_path(String: ext="")```
- Takes in extension ```ext``` (E.g., ".jpg") and outputs a random vacant filename of type ```ext```
<!-- -->

### Usage
```
vacant_path = gen_path('.txt') # generated '7309853189508131.txt'
g = open(vacant_path, 'w')
g.write("Some text")
g.close()
```

### 7. pdf_reader
```PDFReader.add(String: url)```
- Adds PDF URL to ```self.pdfs```
<!-- -->

```PDFReader.cleanText(String: url)```
- Adds PDF URL to ```self.pdfs```
- Cleans text
- 1) Lowercase
- 2) Remove non-alphanumeric & underscore chars 
- 3) Remove consecutive newlines & lines with only 1 character
<!-- -->


```PDFReader.extract_text(String: path)```
- Converts PDF file at ```path``` to text
- For every page, read all text + append image_to_text at end
- Images should be pre-downloaded in ```self.pdf_dir```
- Once completed, delete PDF
<!-- -->

```PDFReader.save_imgs(String: path)```
- Downloads all images from PDF file at ```path``` into ```self.pdf_dir```
<!-- -->

```PDFReader.read_all_pdfs()```
- For each url in ```self.pdfs```, downloads PDF at url and saves PDF images in ```self.pdf_dir```
- Generator. Yields: {\
      &nbsp;&nbsp;&nbsp;&nbsp;'url': //PDF url\
      &nbsp;&nbsp;&nbsp;&nbsp;'text': //PDF text (including image_to_text)\
  }
<!-- -->

```PDFReader.reset()```
- Empties ```self.pdfs```
<!-- -->

### Usage
```
PR = PDFReader()
PR.add('https://www.memoori.com/wp-content/uploads/2017/10/The-Future-Workplace-2017-Synopsis.pdf')
generator = PR.read_all_pdfs()
for obj in generator:
    print(obj['url'])
    print(obj['text'])
PR.reset()
```

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
