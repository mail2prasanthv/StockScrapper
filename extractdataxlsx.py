import pandas as pd
import time

   
def getCompaniesListFromCsv():
    bse_csv_file_name = "./exchanges/v3/bse.csv"
    nse_csv_file_name = "./exchanges/v3/nse.csv"

    bse_usecols = ["Security Code", "Issuer Name", "Security Id", "Status", "Group", "Instrument", "ISIN No"]
    nse_usecols = ["SYMBOL", "NAME OF COMPANY", " ISIN NUMBER"]
    bseData =  pd.read_csv(bse_csv_file_name, usecols=bse_usecols,index_col=False)
    nseData = pd.read_csv(nse_csv_file_name, usecols=nse_usecols,index_col=False)
    
    nseCompanies = getExchangeDatav2(nseData,False)
    bseCompanies = getExchangeDatav2(bseData, True)

    bse_nse_isin_list =  sorted(set(list(nseCompanies.keys()) + list(bseCompanies.keys())))

    isin_nse_bse_codes_map = {}
    for isin in bse_nse_isin_list:
        exchanges = []
        # nse_bse_codes_set = set()
        # exchanges_set = set()
        nse_company = nseCompanies.get(isin, None)
        bse_company = bseCompanies.get(isin, None)
        if nse_company != None:
            exchange = {}
            exchange["code"] = nse_company["symbol"]
            exchange["name"] ="NSE"
            exchanges.append(exchange)
        if bse_company != None:
            exchange = {}
            exchange["code"] = bse_company["bseCode"]
            exchange["name"] ="BSE"
            exchanges.append(exchange)

        isin_nse_bse_codes_map[isin] = exchanges
        
    return isin_nse_bse_codes_map

def getExchangeDatav2(exchangeData, isBse):
    print("----------------------------------")
    
    companies_map = {}
    companies_symbols_set = set()
    for index, row  in exchangeData.iterrows():
        company = {}
 
        if isBse ==True:
            instrument = str(row['Instrument'])
            status = str(row['Status'])
            if instrument=="Equity" and status=='Active':
                symbol = str(row['Security Id'])
                bseCode = str(row['Security Code'])
                name = str(row['Issuer Name'])
                isin = str(row['ISIN No'])
            else:
                continue
        if isBse == False:
            symbol = str(row['SYMBOL'])
            name = str(row['NAME OF COMPANY'])
            bseCode=''
            isin = str(row[' ISIN NUMBER'])
        
        company["symbol"] = symbol
        company["name"] = name
        company["bseCode"] = bseCode
        company["isin"] = isin
        print(company)
        companies_map[isin] = company
        companies_symbols_set.add(symbol)
        # print(name,symbol  )
                                                                
    return companies_map


if __name__ == "__main__":
   getCompaniesListFromCsv()

# https://tradebrains.in/find-complete-list-of-stocks-listed-indian-stock-market/
# https://www.bseindia.com/corporates/List_Scrips.html
# https://www.nseindia.com/market-data/securities-available-for-trading
# https://upstox.com/developer/api-documentation/instruments