# NLP-Webscraper

Update [10/05/22]
- Selenium framework
- [Added] **get_sublinks.py** extracts all sublinks up to a specified depth from the root node
- Plots the sublinks in a network graph (download **Network Graphs/\*.html** and run it on localhost)
- Generates csv with all graph edges for tracking of sublinks (**Edgelist/\*.csv**)
- [Added] **company_website_searcher** Finds company website based on company name. Requires manual checking though
- [Added] **Companies/companies-sensor.xlsx** - actual company websites for software
- [Added] **Companies/companies-software.xlsx** - actual company websites for sensors (missing for Paracosm)

Update [11/05/22]
- Added functions to cut down on amount of similar sites visited with the **same content** using html-id and md5 hash value
- Translates websites which are in other languages to english after scrapping the data
