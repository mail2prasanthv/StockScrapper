import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import string

def getWebsiteBseNseCodes(soup):
  div = getClassData(soup, "company-links")
  children = div.findChildren("span" , recursive=True)
  website = removeunwantedChars(children[0].text)
  bsecode = removeunwantedChars(children[1].text).replace('BSE:', '')
  nsecode = removeunwantedChars(children[2].text).replace('NSE:', '')
  basic_dict = {}
  basic_dict['website'] = website
  basic_dict['bsecode'] = bsecode
  basic_dict['nsecode'] = nsecode
  return basic_dict

  return website, bsecode, nsecode

def removeunwantedCharsInNumber(str):
    return removeunwantedChars(str).replace(',', '')

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

# def getCashFlows(soup):
#     net_cash_flow_dict= {}
#     operating_activity_dict= {}
#     investing_activity_dict={}
#     financing_activity_dict={}
#     section_children = soup.find("section", {"id": "cash-flow"})
#     years = getHeaderInYears(section_children)
#     #
#     cashflow_activities = section_children.find_all("tr")
#     cashflow_operating_activity= cashflow_activities[1]
#     cashflow_investing_activity= cashflow_activities[2]
#     cashflow_financing_activity= cashflow_activities[3]

#     operating_activity_dict = getTimePerioddata(years, cashflow_operating_activity)
#     investing_activity_dict = getTimePerioddata(years, cashflow_investing_activity)
#     financing_activity_dict = getTimePerioddata(years, cashflow_financing_activity)

   
#     index =0
#     #Total
#     net_cash_flows = section_children.find("tr", {"class": "strong"})
#     net_cash_flow_dict = getTimePerioddata(years, net_cash_flows)

#     return operating_activity_dict, investing_activity_dict, financing_activity_dict, net_cash_flow_dict


# def getBalanceSheet(soup):
#     balancesheet_historical_assets = {}
#     balancesheet_historical_liability = {}
#     section_children = soup.find("section", {"id": "balance-sheet"})
#     years = getHeaderInYears(section_children)
        
#     assets_liabilities = section_children.find_all("tr", {"class": "strong"})
#     liabilities_all = assets_liabilities[0]
#     assets_all = assets_liabilities[1]
#     liabilities = liabilities_all.find_all("td", {"class": ""})
#     assets = assets_all.find_all("td", {"class": ""})

#     index =0
#     for liability in liabilities:
#         liability_text = removeunwantedCharsInNumber(liability.text)
#         balancesheet_historical_liability[years[index]] = liability_text
#         index = index+1

#     index =0
#     for asset in assets:
#         asset_text = removeunwantedCharsInNumber(asset.text)
#         balancesheet_historical_assets[years[index]] = asset_text
#         index = index+1

#     return balancesheet_historical_assets, balancesheet_historical_liability

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
        quarter_format = removeunwantedChars(quarter_head.text)
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
    section_children = soup.find("section", {"id": "shareholding"})
    return getGeneralData(section_children,"Quarterly")

def getQuarterlyResults(soup):
    section_children = soup.find("section", {"id": "quarters"})
    return getGeneralData(section_children,"Quarterly")

def getRatios(soup):
    section_children = soup.find("section", {"id": "ratios"})
    return getGeneralData(section_children,"Yearly")

def getProfitAndLoss(soup):
    section_children = soup.find("section", {"id": "profit-loss"})
    return getGeneralData(section_children,"Yearly")

def getBalanceSheetNew(soup):
    section_children = soup.find("section", {"id": "balance-sheet"})
    return getGeneralData(section_children,"Yearly")

def getCashFlowsNew(soup):
    section_children = soup.find("section", {"id": "cash-flow"})
    return getGeneralData(section_children, "Yearly")

def getGeneralData(section_children, period_frequency):
    period=None
    if(period_frequency=='Quarterly'):
        period = getHeaderInQuarters(section_children)
    elif(period_frequency=='Yearly'):
        period = getHeaderInYears(section_children)

    table_body = section_children.find("tbody")
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
                value = removeunwantedChars(element.text)
            if index==0:
                key= value;
                index = index+1
                continue
            if(key=="RawPDF"):
                continue
            dict[period[index-1]] = value
            index = index+1
        if(key!="RawPDF"):
            superdict[key] = dict

    return superdict


urlprefix ="https://www.screener.in/company/"
companyticker = 'AFFLE'
urlPostfix ='/consolidated/'
URL = urlprefix+companyticker+urlPostfix

r = requests.get(URL)
  
soup = BeautifulSoup(r.content, 'html5lib') 

securityDescription = getSecurityDescription(soup)

basic_dict1 = getWebsiteBseNseCodes(soup)
basic_dict2 = getbasicInfo(soup)

basic_dict3 =  getSectorAndIndustry(soup)

print("-------------QuarterlyResults-------------")
print(getQuarterlyResults(soup))

print("-------------ProfitAndLoss-------------")
print(getProfitAndLoss(soup))

print("-------------BalanceSheetNew-------------")
print(getBalanceSheetNew(soup))

print("-------------CashFlows-------------")
print(getCashFlowsNew(soup))

print("-------------Ratios-------------")
print(getRatios(soup))

print("-------------ShareHoldingPattern-------------")
print(getShareHoldingPattern(soup))