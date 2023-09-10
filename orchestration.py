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

def scrapForthelistoftickers(isin_nse_bse_codes_map, force):
    for index, (isin, nse_bse_codes) in enumerate(isin_nse_bse_codes_map.items()):
          nse_bse_codes_list = list(nse_bse_codes)
          try:
            msg = startScrap(nse_bse_codes_list[0], isin, force)
          except (WebPageNotAvailableException, MarketCapDataNotAvailableException, LatestDataNotAvailable):
            if(len(nse_bse_codes_list)>1):
              msg = startScrap(nse_bse_codes_list[1], isin, force)
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

isin_nse_bse_codes_map = getCompaniesv2()


scrapForthelistoftickers(isin_nse_bse_codes_map,False)

print("Finished") 

