import pandas as pd
import time

def getCompanies():
    bse_csv_file_name = "./exchanges/bse.csv"
    nse_excel_file_name = "./exchanges/nse.xlsx"

    usecols = ["Security Code", "Issuer Name", "Security Id", "Status", "Group", "Instrument"]
    bseData =  pd.read_csv(bse_csv_file_name, usecols=usecols,index_col=False)
    nseData = pd.read_excel(nse_excel_file_name)
    

    bseCompanies = getExchangeData(bseData, True)
    nseCompanies = getExchangeData(nseData,False)
    return bseCompanies, nseCompanies

def getExchangeData(exchangeData, isBse):
    print("----------------------------------")
    # if isBse:
    #     df = pd.DataFrame(bseData, columns=['Security Id','Security Name', 'Instrument'])
    # else:
    #     df = pd.DataFrame(bseData, columns=['Symbol','Company Name'])
    
    companies = []
    for index, row  in exchangeData.iterrows():
        company = {}
        if isBse == False:
            symbol = str(row['Symbol'])
            name = str(row['Company Name'])
            bseCode=''
        if isBse ==True:
            instrument = str(row['Instrument'])
            status = str(row['Status'])
            if instrument=="Equity" and status=='Active':
                symbol = str(row['Security Id'])
                bseCode = str(row['Security Code'])
                name = str(row['Issuer Name'])
            else:
                continue
        company["symbol"] = symbol
        company["name"] = name
        company["bseCode"] = bseCode

        companies.append(company)
        # print(name,symbol  )
                                                                
    return companies

if __name__ == "__main__":
   getCompanies()
