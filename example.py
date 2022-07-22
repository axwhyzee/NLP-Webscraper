from companycrawler.crawler import CompanyCrawler
from clientextraction.heuristic_extraction import clients_from_json, print_clients
import pandas as pd
import os

'''
+------------------+
| define variables |
+------------------+
'''
data_path = 'saved_data' # save scaped data here
max_depth = 2
client_output_path = 'clients.csv' # create client csv here

'''
+--------------+
| Web scraping |
+--------------+
'''
def scrape_company(company, url):
    CC.crawl_company(
        root=url,
        company=company, 
        save_dir=data_path,
        max_depth=max_depth
    )

'''
+-------------------+
| Client extraction |
+-------------------+
'''
def extract_clients(data_path, companies):
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

# setup webscraper
CC = CompanyCrawler(save_webtree=False, save_network_graph=True)

# scrape company
scrape_company('ViewAR', 'https://www.viewar.com/')

# convert scraped company data into client data
extract_clients(data_path, ['ViewAR'])
