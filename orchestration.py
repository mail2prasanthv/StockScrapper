import os.path
from downloadcompanylist import *
from extractdataxlsx import *
from ScreenerScrapper import *
import time
from math import ceil
from itertools import islice
import threading

def divide_chunks(l, n):
     
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def scrapForthelistoftickers(tickers):
    index =1;
    errorindex=1;
    for ticker in each_chunk_list:
        retryCount=1;
        while retryCount<3:
            try:
                # if index<100:
                startScrap(ticker)
                print("Succesfully Processed ", ticker, " index:", index)
            except Exception as e:
                print("Error while processing Retrying:", ticker, e)
                time.sleep(5)
                errorindex =0;
                retryCount = retryCount +1
                continue 
            break
        if retryCount>=2:
            print("Retry Failed for ", ticker, " index:", index)
        index = index +1 
        errorindex = errorindex +1
        if(errorindex%40==0):
            time.sleep(5)
            errorindex = 0;


path = "./" + "nse_security_list.xlsx"

file_exists = os.path.isfile(path)

if file_exists is False:
    downloadNseSecurityListFile()

length_to_split = [50]

companyInfo = list(getCompanies().keys());

list_of_lists = list(divide_chunks(companyInfo, 50))


for each_chunk_list in list_of_lists:
    scrapForthelistoftickers(each_chunk_list)

print("Finished") 
