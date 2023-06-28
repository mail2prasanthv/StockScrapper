import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import string
import json
from pymongo import MongoClient
import time

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

def removeunwantedCharsInNumber(str):
    return removeunwantedChars(str).replace(',', '').replace('%', '')

def removeunwantedChars(str):
    return str.strip().replace('\n', '').replace(' ', '').replace('\xa0', '').replace('+','').replace('/','')

def removeunwantedCharsRetainSpace(str):
    return str.strip().replace('\n', '').replace('\xa0', '').replace('+','').replace('/','')

def convertToQuarter(str):
    return removeunwantedChars(str).replace('Mar', 'Q1-').replace('Jun', 'Q2-').replace('Sep', 'Q3-').replace('Dec', 'Q4-')

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
        raw_val = removeunwantedCharsInNumber(metric_value)
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
        quarter_format = convertToQuarter(quarter_head)
        quarters.append(quarter_format)
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
        quarter_format = removeunwantedChars(quarter_head_text)
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
    if(period_frequency=='Quarterly'):
        period = getHeaderInQuarters(body)
    elif(period_frequency=='Yearly'):
        period = getHeaderInYears(body)

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
                key= value;
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

def requireScrapping(companyticker, force):
    isRequireScrapping= True;
    query = {"_id": companyticker}
    if force==False:
        result = companiesCollection.find_one(query)
        if result:
           isRequireScrapping = False;
    return isRequireScrapping

def startScrap(companyticker,force):

    scrappingRequired = requireScrapping(companyticker, force )
    if not scrappingRequired:
        return DATA_ALREADY_AVAILABLE + companyticker

    urlprefix ="https://www.screener.in/company/"
    urlPostfix ='/consolidated/'
    URL = urlprefix+companyticker+urlPostfix

    headers = {
    "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
    
    retryCount =0;
    while True:
        responses = requests.get(URL, headers=headers) 
        statusCode = responses.status_code
        if statusCode== 404:
            return WEBPAGE_NOTFOUND + companyticker
        elif statusCode ==200:
            break
        elif statusCode!= 429:
            print("Status Code:", statusCode)
        elif statusCode==429:
            retryCount = retryCount +1
            print("Retrying:", companyticker,":" ,retryCount)
            time.sleep(5)
            if retryCount>=3:
                break;
        
    soup = BeautifulSoup(responses.content, 'html5lib') 

    securityDescription = getSecurityDescription(soup)

    website_bse_nse_codes = getWebsiteBseNseCodes(soup)

    basic_info_dict = getbasicInfo(soup)

    sectorAndIndustry =  getSectorAndIndustry(soup)

    quarterly_results = getQuarterlyResults(soup)

    profit_loss_dict = getProfitAndLoss(soup)

    balance_sheet = getBalanceSheet(soup)

    cashflows = getCashFlows(soup)

    ratios = getRatios(soup)

    shareholders_pattern ={}
    try:
        shareholders_pattern = getShareHoldingPattern(soup)
    except:
        print("Error while processing Shareholders pattern. seems share holdern pattern missing. security:" ,companyticker )

    alldata ={}
    alldata["name"] = securityDescription

    
    alldata["_id"]=companyticker
    alldata = {**alldata, **website_bse_nse_codes, **sectorAndIndustry,**basic_info_dict}
    alldata["quarterlyResults"] = quarterly_results
    alldata["profitAndLoss"] = profit_loss_dict
    alldata["balanceSheet"] = balance_sheet
    alldata["cashFlows"] = cashflows
    alldata["ratios"] =ratios
    alldata["shareholdersPattern"] =shareholders_pattern

    insertIntoMongoDB(alldata, companyticker)

    
    return PROCESSED + companyticker

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
        

if __name__ == "__main__":
    companyticker = 'ALLETEC'
    startScrap(companyticker, True)