import os.path
from downloadcompanylist import *
from extractdataxlsx import *
from ScreenerScrapper import *
import time
from math import ceil
from itertools import islice

def divide_chunks(l, n):
     
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def scrapForthelistoftickers(tickers, force):
    index =1;
    errorindex=1;
    maxretry=2
    for  ticker in tickers:
        retryCountIndex=1
        while retryCountIndex<maxretry:
            try:                
                msg = startScrap(ticker,force)
                print(msg)
            except Exception as e:
                print("Error while processing Retrying:", ticker, e)
                # time.sleep(5)
                errorindex =0;
                retryCountIndex = retryCountIndex +1
                continue 
            break
        if retryCountIndex==maxretry:
            print("Retry Failed for ", ticker, " index:", index)
        index = index +1 
        errorindex = errorindex +1
        # if(index%30==0):
        #     # time.sleep(5)
        #     errorindex = 0;


path = "./" + "nse_security_list.xlsx"

file_exists = os.path.isfile(path)

# if file_exists is False:
#     downloadNseSecurityListFile()

length_to_split = [50]

bseCompanies, nseCompanies = getCompanies();

nse_bse_companies = {**bseCompanies, **nseCompanies}

companies = list(nse_bse_companies.keys())
companies.sort()

print("-----NSE & BSE------")
for key, value in nse_bse_companies.items():
    print(key)

list_of_lists = list(divide_chunks(companies, 50))

for each_chunk_list in list_of_lists:
    scrapForthelistoftickers(each_chunk_list,False)

print("Finished") 
