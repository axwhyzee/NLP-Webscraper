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
- [**reverse_search.py**] Exploring automated Google reverse image search on brand images to identify customers
