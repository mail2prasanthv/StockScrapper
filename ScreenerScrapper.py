import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import string
import json
from pymongo import MongoClient
import time
import datetime
import calendar
from datetime import datetime

HOST = 'localhost'
PORT = 27017
DB_NAME = 'stock-market'
TABLE_NAME = 'companies'

WEBPAGE_NOTFOUND = "Webpage Not Available:"
DATA_ALREADY_AVAILABLE = "Data already Available in DB:"
PROCESSED = "Processed Successfully:"

client = MongoClient(HOST, PORT)
mongodatabase = client[DB_NAME]
companiesCollection = mongodatabase[TABLE_NAME]

def getWebsiteBseNseCodes(soup):
  div = getClassData(soup, "company-links")
  children = div.find_all("span" , recursive=True)
  website = removeunwantedChars(children[0].text)
  bsecode = removeunwantedChars(children[1].text).replace('BSE:', '')
  try:
    nsecode = removeunwantedChars(children[2].text).replace('NSE:', '')
  except:
    nsecode = "NOT AVAILABLE"
  basic_dict = {}
  basic_dict['website'] = website
  basic_dict['bseCode'] = bsecode
  basic_dict['nseCode'] = nsecode
  return basic_dict

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
    
def month_abbreviation_to_number(abbreviation):
    months = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }

    return months.get(abbreviation.capitalize())

def removeunwantedCharsInNumber(str):
    return removeunwantedChars(str).replace(',', '').replace('%', '')

def removeunwantedChars(str):
    return str.strip().replace('\n', '').replace(' ', '').replace('\xa0', '').replace('+','').replace('/','')
    

def removeunwantedCharsRetainSpace(str):
    return str.strip().replace('\n', '').replace('\xa0', '').replace('+','').replace('/','')

def convertToDate(str):
    list = str.split()# Sep 2021
    year=  int(list[1])
    month = month_abbreviation_to_number(list[0])
    day = calendar.monthrange(year, month)[1]
    # end_date = datetime.datetime(year, month, day)
    return   f"{year}-{month:02d}-{day:02d}"
    # return end_date.strftime("%Y-%m-%d")

def convertToYear(str):
    return removeunwantedChars(str).replace('Mar', 'Year-')

def camelCase(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]

def convert_first_letter_to_lowercase(s):
    return ''.join([s[0].lower(), s[1:]])

    converted_sentence = "".join([word[0].lower() + word[1:] for word in words])
    return converted_sentence

def getTimePerioddata(years, cashflow_operating_activity):
    cashflow_operating_activity_tds = cashflow_operating_activity.find_all("td", {"class": ""})
    dict= {}
    index =0
    for cashflow_operating_activities in cashflow_operating_activity_tds:
        cashflow_operating_activities_text = removeunwantedCharsInNumber(cashflow_operating_activities.text)
        dict[years[index]] = cashflow_operating_activities_text
        index = index+1
    return dict

def getbasicInfo(soup):
    companyratio = getClassData(soup, "company-ratios")
    basic_dict = {}
    li_children = companyratio.find_all("li" , recursive=True)
    for li_child in li_children:
        metric_full_name = li_child.find("span" , {"class": "name"}).text
        metric_value = li_child.find("span" , {"class": "number"}).text
        metric_name =camelCase(metric_full_name)
        if(metric_name=='currentPrice'):
            metric_name ='asOfDatePrice'
        raw_val = removeunwantedCharsInNumber(metric_value)
        if metric_name=='marketCap' and raw_val=='':
            print("FAILED : MarketCap Not Found:" )
            raise MarketCapDataNotAvailableException
            
        if  raw_val.isdigit() or isfloat(raw_val):
            metric_value = float(raw_val)
        else:
            metric_value = raw_val
        basic_dict[metric_name] = metric_value
    return basic_dict

def getSectorAndIndustry(soup):
    basic_dict = {}
    section_children = soup.find("section", {"id": "peers"})
    sector_and_industries = section_children.find_all("a")
    sector = removeunwantedCharsRetainSpace(sector_and_industries[0].text)
    industries = removeunwantedCharsRetainSpace(sector_and_industries[1].text)
    basic_dict['sector'] = sector
    basic_dict['industries'] = industries
    return basic_dict

def getHeaderInQuarters(section_children):
    quarters = []
    for quarter_head in getHeaders(section_children, None):
        if(quarter_head!= "TTM"):
          quarter_head = convertToDate(quarter_head)
        quarters.append(quarter_head)
    return quarters

def getHeaderInYears(section_children):
    years = []
    for year_head in getHeaders(section_children, {"class": ""}):
        year_format = convertToYear(year_head)
        years.append(year_format)
    return years

def getHeaders(section_children,style):
    quarter_all = section_children.find("thead")
    quarter_heads= quarter_all.find_all("th", style)
    quarters = []
    for quarter_head in quarter_heads:
        quarter_head_text = quarter_head.text;
        if quarter_head_text == "":
            continue
        quarter_format = removeunwantedCharsRetainSpace(quarter_head_text)
        quarters.append(quarter_format)
    return quarters

def getClassData(soup, classname):
    return soup.find(class_=classname)

def getSecurityDescription(soup):
  return getClassDataText(soup, "margin-0 show-from-tablet-landscape")

def getClassDataText(soup, classname):
    return getClassData(soup,classname).text

def getClassData(soup, classname):
    return soup.find(class_=classname)

def getShareHoldingPattern(soup):
    body = soup.find("section", {"id": "shareholding"})
    return getGeneralData(body,"Quarterly")

def getQuarterlyResults(soup):
    body = soup.find("section", {"id": "quarters"})
    return getGeneralData(body,"Quarterly")

def getRatios(soup):
    body = soup.find("section", {"id": "ratios"})
    return getGeneralData(body,"Yearly")

def getProfitAndLoss(soup):
    body = soup.find("section", {"id": "profit-loss"})
    return getGeneralData(body,"Yearly")

def getBalanceSheet(soup):
    body = soup.find("section", {"id": "balance-sheet"})
    return getGeneralData(body,"Yearly")

def getCashFlows(soup):
    body = soup.find("section", {"id": "cash-flow"})
    return getGeneralData(body, "Yearly")

def getGeneralData(body, period_frequency):
    period=None
    # if(period_frequency=='Quarterly'):
    #     period = getHeaderInQuarters(body)
    # elif(period_frequency=='Yearly'):
    period = getHeaderInQuarters(body)

    table_body = body.find("tbody")
    rows= table_body.find_all("tr")
    superdict ={}
    for row in rows:
        elements= row.find_all("td")
        key=""
        index=0
        dict= {}
        for element in elements:
            button= element.find("button")
            if button:
                value = removeunwantedChars(button.text)
            else:
                value = removeunwantedCharsInNumber(element.text)
            if index==0:
                key= value.replace('.','');
                index = index+1
                continue
            if(key=="RawPDF") or value=='':
                continue
            value = float(value)
            dict[period[index-1]] = value
            index = index+1
        if(key!="RawPDF"):
            superdict[convert_first_letter_to_lowercase(key)] = dict

    return superdict

def insertIntoMongoDB(alldata, key):
    companiesCollection.update_one({"_id": key}, {'$set': alldata}, upsert=True)

def requireScrapping(isin, force):
    
    if force== True:
        return True

    query = {"isin": isin}
    result = companiesCollection.find_one(query)
    if result:
        if("marketCap" in result):
          return False
        else:
          return True
    return False

def startScrap(identifier, isin, force):
    
    scrappingRequired = requireScrapping(isin, force)
    if not scrappingRequired:
        print("Data Already Available:", isin)
        retry = False
        return
    urlprefix ="https://www.screener.in/company/"
    consolidated ='consolidated'
    standalone =""
    mode =consolidated
    retryCount =1
    MAX_RETRY=3
    
    retry = True
    
    while(retry and retryCount<=MAX_RETRY):
        try:
            URL = urlprefix+identifier+ "/" + mode
            mode_desc = mode
            if mode ==standalone:
                mode_desc = 'standalone'
            scrap(URL, isin, mode_desc)
            print("Successfully processed:", isin)
            retry = False
        except (WebPageNotAvailableException, MarketCapDataNotAvailableException, LatestDataNotAvailable):
            if mode==standalone:
                print("FAILED: WebPage not available:", isin)
                raise WebPageNotAvailableException
            elif mode==consolidated : 
                mode = standalone
                print("Switching to standalone for", isin)
        except TooManyHttpRequestsException:
            print("Too many Requests :Retrying:", isin, ":retryCount:" ,retryCount)
            time.sleep(5)
            retryCount = retryCount +1
        except Exception as error:
            print(error)
            print("FAILED: Exception:", ":retryCount:" ,retryCount)
            retry= False
            raise WebPageNotAvailableException
        if(retryCount>MAX_RETRY):
            raise WebPageNotAvailableException
        
    if MAX_RETRY<retryCount:
        print("FAILED: Retry:", isin,  ":count:", retryCount)    

def scrap(URL,  isin, mode):

    headers = {
    "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}


    while True:
        responses = requests.get(URL, headers=headers) 
        statusCode = responses.status_code
        if statusCode== 404:
            raise WebPageNotAvailableException
        elif statusCode ==200:
            break
        elif statusCode!= 429:
            print("Status Code:", statusCode)
        elif statusCode==429:
            raise TooManyHttpRequestsException
        
    soup = BeautifulSoup(responses.content, 'html5lib') 

    basic_info_dict = getbasicInfo(soup)

    securityDescription = getSecurityDescription(soup)

    website_bse_nse_codes = getWebsiteBseNseCodes(soup)

    sectorAndIndustry =  getSectorAndIndustry(soup)

    quarterly_results = getQuarterlyResults(soup)

    profit_loss_dict = getProfitAndLoss(soup)

    first_key_in_profit_and_loss = list(profit_loss_dict.keys())[0]

    profit_loss_first_dictionary = profit_loss_dict[first_key_in_profit_and_loss]
    years_list = list(profit_loss_first_dictionary.keys())
    if "TTM" in years_list:
        years_list.remove("TTM")
    last_element = years_list[-1]
    current_year = datetime.today().year
    previous_year = current_year - 1
    last_data_availability_date = datetime.strptime(last_element, "%Y-%m-%d").date()
    if last_data_availability_date.year<current_year-1:
        raise LatestDataNotAvailable

    balance_sheet = getBalanceSheet(soup)

    cashflows = getCashFlows(soup)

    ratios = getRatios(soup)

    shareholders_pattern ={}
    try:
        shareholders_pattern = getShareHoldingPattern(soup)
    except:
        print("Error while processing Shareholders pattern. seems share holdern pattern missing. security:" ,key )

    alldata ={}
    alldata["name"] = securityDescription


    alldata["_id"]=isin
    alldata["asOfDate"]=datetime.now().strftime('%Y-%m-%d')
    alldata["mode"]=mode
    
    alldata = {**alldata, **website_bse_nse_codes, **sectorAndIndustry,**basic_info_dict}
    alldata["quarterlyResults"] = quarterly_results
    alldata["profitAndLoss"] = profit_loss_dict
    alldata["balanceSheet"] = balance_sheet
    alldata["cashFlows"] = cashflows
    alldata["ratios"] =ratios
    alldata["shareholdersPattern"] =shareholders_pattern

    insertIntoMongoDB(alldata, isin)


    return PROCESSED + isin + ":" + isin

# def isWebpageAvailable(soup):
#     pagenotFound = getClassData(soup, "card card-medium")
#     if not pagenotFound:
#         return True
#     errorTag = pagenotFound.find("h2")
#     if not errorTag:
#         return True
#     errorText = errorTag.text
#     if not errorText:
#         return True
#     if errorText=="Error 404: Page Not Found":
#         return False
#     return True;
        
# define Python user-defined exceptions
class MarketCapDataNotAvailableException(Exception):
    pass

class WebPageNotAvailableException(Exception):
    pass

class TooManyHttpRequestsException(Exception):
    pass

class LatestDataNotAvailable(Exception):
    pass

if __name__ == "__main__":
    companyticker = 'KRBL'
    startScrap(companyticker,"INE001B01026","NSE" ,True)