# NLP-Webscraper

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
  - Merges 2 Convolutionary Neural Networks models
    - Model A: 
      - ~80% accuracy
      - Trains on images scraped from 120 company websites
    - Model B:  
      - xx% accuracy
      - Trains on Flick30k dataset
  - Evaluates the probability of each image cluster being the client logo cluster
