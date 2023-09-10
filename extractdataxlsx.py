import pandas as pd
import time

# def getCompaniesv1():
#     bse_csv_file_name = "./exchanges/v2/bse.csv"
#     nse_csv_file_name = "./exchanges/v2/nse.csv"

#     bse_usecols = ["Security Code", "Issuer Name", "Security Id", "Status", "Group", "Instrument", "ISIN No"]
#     nse_usecols = ["SYMBOL", "NAME OF COMPANY", " ISIN NUMBER"]
#     bseData =  pd.read_csv(bse_csv_file_name, usecols=bse_usecols,index_col=False)
#     nseData = pd.read_csv(nse_csv_file_name, usecols=nse_usecols,index_col=False)
    

#     bseCompanies = getExchangeDatav1(bseData, True)
#     nseCompanies = getExchangeDatav1(nseData,False)
#     return bseCompanies, nseCompanies

# def getExchangeDatav1(exchangeData, isBse):
#     print("----------------------------------")
#     # if isBse:
#     #     df = pd.DataFrame(bseData, columns=['Security Id','Security Name', 'Instrument'])
#     # else:
#     #     df = pd.DataFrame(bseData, columns=['Symbol','Company Name'])
    
#     companies = []
#     for index, row  in exchangeData.iterrows():
#         company = {}
#         if isBse == False:
#             symbol = str(row['Symbol'])
#             name = str(row['Company Name'])
#             bseCode=''
#         if isBse ==True:
#             instrument = str(row['Instrument'])
#             status = str(row['Status'])
#             if instrument=="Equity" and status=='Active':
#                 symbol = str(row['Security Id'])
#                 bseCode = str(row['Security Code'])
#                 name = str(row['Issuer Name'])
#             else:
#                 continue
#         company["symbol"] = symbol
#         company["name"] = name
#         company["bseCode"] = bseCode

#         companies.append(company)
#         # print(name,symbol  )
                                                                
#     return companies

def getCompaniesv2():
    bse_csv_file_name = "./exchanges/v2/bse.csv"
    nse_csv_file_name = "./exchanges/v2/nse.csv"

    bse_usecols = ["Security Code", "Issuer Name", "Security Id", "Status", "Group", "Instrument", "ISIN No"]
    nse_usecols = ["SYMBOL", "NAME OF COMPANY", " ISIN NUMBER"]
    bseData =  pd.read_csv(bse_csv_file_name, usecols=bse_usecols,index_col=False)
    nseData = pd.read_csv(nse_csv_file_name, usecols=nse_usecols,index_col=False)
    
    nseCompanies = getExchangeDatav2(nseData,False)
    bseCompanies = getExchangeDatav2(bseData, True)

    bse_nse_isin_list =  sorted(set(list(nseCompanies.keys()) + list(bseCompanies.keys())))

    isin_nse_bse_codes_map = {}
    for isin in bse_nse_isin_list:
        nse_bse_codes_set = set()
        nse_company = nseCompanies.get(isin, None)
        bse_company = bseCompanies.get(isin, None)
        if nse_company != None:
            nse_bse_codes_set.add(nse_company["symbol"])
        if bse_company != None:
            nse_bse_codes_set.add(bse_company["symbol"])
        isin_nse_bse_codes_map[isin] = nse_bse_codes_set
        
    return isin_nse_bse_codes_map

def getExchangeDatav2(exchangeData, isBse):
    print("----------------------------------")
    # if isBse:
    #     df = pd.DataFrame(bseData, columns=['Security Id','Security Name', 'Instrument'])
    # else:
    #     df = pd.DataFrame(bseData, columns=['Symbol','Company Name'])
    
    companies_map = {}
    companies_symbols_set = set()
    for index, row  in exchangeData.iterrows():
        company = {}
 
        if isBse ==True:
            instrument = str(row['Instrument'])
            status = str(row['Status'])
            if instrument=="Equity" and status=='Active':
                symbol = str(row['Security Id'])
                bseCode = ''#str(row['Security Code'])
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

        companies_map[isin] = company
        companies_symbols_set.add(symbol)
        # print(name,symbol  )
                                                                
    return companies_map


if __name__ == "__main__":
   getCompaniesv2()
