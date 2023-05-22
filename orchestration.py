import os.path
from downloadcompanylist import *
from extractdataxlsx import *
from ScreenerScrapper import *
import time

path = "./" + "nse_security_list.xlsx"

file_exists = os.path.isfile(path)

if file_exists is False:
    downloadNseSecurityListFile()

companyInfo = getCompanies();

index =1;
errorindex=1;
for key in companyInfo:
    retryCount=1;
    while retryCount<4:
        try:
            # if index<100:
            startScrap(key)
            print("Succesfully Processed ", key, " index:", index)
        except Exception as e:
            print("Error while processing Retrying:", key, e)
            time.sleep(10)
            errorindex =0;
            retryCount = retryCount +1
            continue 
        break
    if retryCount>=4:
        print("Retry Failed for ", key, " index:", index)
    index = index +1 
    errorindex = errorindex +1
    if(errorindex%40==0):
        time.sleep(10)
        errorindex = 0;


print("Finished") 
