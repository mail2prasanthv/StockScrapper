import pandas as pd
import time

def getCompanies():
    bse_csv_file_name = "./exchanges/bse.csv"
    nse_excel_file_name = "./exchanges/nse.xlsx"
    bseData = pd.read_csv(bse_csv_file_name)
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
    
    bseCompanies = {}
    for index, row  in exchangeData.iterrows():
        if isBse == False:
            symbol = str(row['Symbol'])
            name = str(row['Company Name'])
        if isBse ==True:
            instrument = str(row['Industry'])#actually checking Instrument- csv has some problems, industry is mapped to instrument
            if instrument=="Equity":
                symbol = str(row['Issuer Name'])#Issuer Name is mapped to security wrongly
                name = str(row['Security Id'])# security name
            else:
                continue
        bseCompanies[symbol] = name
        # print(name,symbol  )
                                                                
    return bseCompanies

if __name__ == "__main__":
   getCompanies()
