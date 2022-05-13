# NLP-Webscraper

Update [10/05/22]
- Selenium framework
- [**get_sublinks.py**] extracts all sublinks up to a specified depth from the root node
- Plots the sublinks in a network graph (download **Network Graphs/\*.html** and run it on localhost)
- Generates csv with all graph edges for tracking of sublinks (**Edgelist/\*.csv**)
- [**company_website_searcher**] Finds company website based on company name. Requires manual checking though
- [**Companies/companies-sensor.xlsx**] - actual company websites for software
- [**Companies/companies-software.xlsx**] - actual company websites for sensors (missing for Paracosm)

Update [11/05/22]
- Added functions to cut down on amount of similar sites visited with the **same content** by comparing md5 hash value of self-generated 'html-id' <length of DOM><first 5 char><middle 9 char><last 5 char> for faster hashing
- Translates websites which are in other languages to english after scrapping the data

Update [12/05/22]
- [**pdf_reader.py**] Reads PDF text + extract text from PDF images
- [**reverse_search.py**] Exploring Google reverse image search on brand images to identify customers
