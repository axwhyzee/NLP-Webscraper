import pandas as pd
import warnings
import time
import sys

# add local packages to system environment so they can be imported
lib_dir = os.path.join(os.getcwd(), 'Lib')
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

from company_crawler import CompanyCrawler
from functions import url_rstrip

def main(delay=3):
    CC = CompanyCrawler(dictionary='Lib/json/dictionary.json')

    # ignore all warnings
    warnings.filterwarnings('ignore')
    
    df = pd.read_excel('companies-software.xlsx')
    df.dropna(axis=0, inplace=True, subset=['actual_url'])
    df.reset_index(drop=True, inplace=True)
    df['actual_url'] = df['actual_url'].apply(url_rstrip)

    for i, row in df.iloc[29:49].iterrows():
        CC.crawl_company(root=row['actual_url'], company=row['Company Name'], max_depth=2)
        if delay:
            time.sleep(delay)

if __name__ == '__main__':
    main()