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
    failedList =[]
    now= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for index, (isin, exchanges) in enumerate(isin_nse_bse_codes_map.items()):
      for index,exchange in enumerate(exchanges):
        code = ''
        exchange_name =''
        try:
          code = exchange["code"]
          exchange_name = exchange["name"]
          print("start scrap:" , code, " exchange:", exchange_name)
          msg = startScrap(code, isin, exchange_name, force)
          break
        except (WebPageNotAvailableException, MarketCapDataNotAvailableException, LatestDataNotAvailable):
          print("Fail to scrap:" , code, " :exchange: " , exchange_name)
          if(index==len(exchanges)-1):
            failedList.append(code+":"+isin)
            with open('failed_'+now+'.txt', 'a') as file:
                file.write(code+":"+isin+'\n')
    print("Failed List:")
    print(failedList)
    




length_to_split = [50]

isin_nse_bse_codes_map = getCompaniesv2()

scrapForthelistoftickers(isin_nse_bse_codes_map,False)

print("Finished") 

