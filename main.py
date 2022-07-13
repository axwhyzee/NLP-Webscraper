from companycrawler.crawler import CompanyCrawler
import pandas as pd

# define variables
save_dir = 'saved_data'
max_depth = 2

CC = CompanyCrawler(save_webtree=False, save_network_graph=True)

# load excel data from 'companies-software.xlsx'
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
