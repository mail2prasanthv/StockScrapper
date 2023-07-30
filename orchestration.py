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

def sort_dictionary(dictionary_list):
  """Sorts a dictionary list by the value of the `name` key.

  Args:
    dictionary_list: A list of dictionaries.

  Returns:
    A sorted list of dictionaries.
  """

  sorted_dictionary_list = sorted(dictionary_list, key=lambda dictionary: dictionary['symbol'])
  return sorted_dictionary_list

def getUniqueDictionary(list_of_dicts, field):
    unique_list = []
    seen_names = set()

    for d in list_of_dicts:
        if d[field] not in seen_names:
            unique_list.append(d)
            seen_names.add(d[field])
    return unique_list

def scrapForthelistoftickers(companies, force):
    for  company in companies:
        msg = startScrap(company["bseCode"], company["symbol"],force)
    # index =1;
    # errorindex=1;
    # maxretry=2
    # for  ticker in tickers:
    #     retryCountIndex=1
    #     while retryCountIndex<maxretry:
    #         try:                
    #             msg = startScrap(ticker["bseCode"], ticker["symbol"],force)
    #             print(msg)
    #         except Exception as e:
    #             print("Error while processing Retrying:", ticker, e)
    #             # time.sleep(5)
    #             errorindex =0;
    #             retryCountIndex = retryCountIndex +1
    #             continue 
    #         break
    #     if retryCountIndex==maxretry:
    #         print("Retry Failed for ", ticker, " index:", index)
    #     index = index +1 
    #     errorindex = errorindex +1
        # if(index%30==0):
        #     # time.sleep(5)
        #     errorindex = 0;


path = "./" + "nse_security_list.xlsx"

file_exists = os.path.isfile(path)

# if file_exists is False:
#     downloadNseSecurityListFile()

length_to_split = [50]

bseCompanies, nseCompanies = getCompanies();

companies = bseCompanies + nseCompanies


unque_companies =  getUniqueDictionary(companies, "symbol")
sorted_companies = sort_dictionary(unque_companies)

list_of_lists = list(divide_chunks(sorted_companies, 50))

for index, each_chunk_list in enumerate(list_of_lists):
    print("----------------", "Chunk Count:", index,"----------------")
    scrapForthelistoftickers(each_chunk_list,False)

print("Finished") 

