import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import string
import json
from pymongo import MongoClient


def getWebsiteBseNseCodes(soup):
  div = getClassData(soup, "company-links")
  children = div.find_all("span" , recursive=True)
  website = removeunwantedChars(children[0].text)
  bsecode = removeunwantedChars(children[1].text).replace('BSE:', '')
  nsecode = removeunwantedChars(children[2].text).replace('NSE:', '')
  basic_dict = {}
  basic_dict['website'] = website
  basic_dict['bsecode'] = bsecode
  basic_dict['nsecode'] = nsecode
  return basic_dict

def removeunwantedCharsInNumber(str):
    return removeunwantedChars(str).replace(',', '').replace('%', '')

def removeunwantedChars(str):
    return str.strip().replace('\n', '').replace(' ', '').replace('\xa0', '').replace('+','')

def convertToQuarter(str):
    return removeunwantedChars(str).replace('Mar', 'Q1-').replace('Jun', 'Q2-').replace('Sep', 'Q3-').replace('Dec', 'Q4-')

def convertToYear(str):
    return removeunwantedChars(str).replace('Mar', 'Year-')


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
      metric_name = li_child.find("span" , {"class": "name"}).text
      metric_value = li_child.find("span" , {"class": "number"}).text
      metric_name =removeunwantedChars(metric_name)
      metric_value = removeunwantedCharsInNumber(metric_value)
      basic_dict[metric_name] = metric_value
   return basic_dict

def getSectorAndIndustry(soup):
    basic_dict = {}
    section_children = soup.find("section", {"id": "peers"})
    sector_and_industries = section_children.find_all("a")
    sector = removeunwantedChars(sector_and_industries[0].text)
    industries = removeunwantedChars(sector_and_industries[1].text)
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
            superdict[key] = dict

    return superdict

def insertIntoMongoDB(alldata, key):
    host = 'localhost'
    port = 27017
    db_name = 'stock-market'
    table_name = 'securities'

    client = MongoClient(host, port)
    mydatabase = client[db_name]
    mycollection = mydatabase[table_name]

    mycollection.update_one({"_id": key}, {'$set': alldata}, upsert=True)




def startScrap(companyticker):
    urlprefix ="https://www.screener.in/company/"
    urlPostfix ='/consolidated/'
    URL = urlprefix+companyticker+urlPostfix

    headers = {
    "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
    
    r = requests.get(URL, headers=headers)  
    soup = BeautifulSoup(r.content, 'html5lib') 

    securityDescription = getSecurityDescription(soup)

    website_bse_nse_codes = getWebsiteBseNseCodes(soup)

    basic_info_dict = getbasicInfo(soup)

    sectorAndIndustry =  getSectorAndIndustry(soup)

    quarterly_results = getQuarterlyResults(soup)

    profit_loss_dict = getProfitAndLoss(soup)

    balance_sheet = getBalanceSheet(soup)

    cashflows = getCashFlows(soup)

    ratios = getRatios(soup)

    shareholders_pattern = getShareHoldingPattern(soup)

    alldata ={}
    alldata["securityDescription"] = securityDescription

    key = website_bse_nse_codes['nsecode'] + ":"+website_bse_nse_codes['bsecode']
    alldata["_id"]=key
    alldata = {**alldata, **website_bse_nse_codes, **sectorAndIndustry, **quarterly_results,**profit_loss_dict,**balance_sheet,**cashflows,**ratios,**shareholders_pattern}

# Converting to JSON format
    myJSON = json.dumps(alldata,sort_keys=True,
    indent=4,
    separators=(',', ': '))

    insertIntoMongoDB(alldata, key)

if __name__ == "__main__":
    companyticker = 'IRCTC'
    startScrap(companyticker)