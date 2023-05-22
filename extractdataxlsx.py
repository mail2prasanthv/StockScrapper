import pandas as pd
import time

def getCompanies():
    file_name = "nse_security_list.xlsx"
    data = pd.read_excel(file_name)

    df = pd.DataFrame(data, columns=['Symbol','Company Name'])

    companyInfo = {}
    for ind in df.index:
        companyInfo[df['Symbol'][ind]] = df['Company Name'][ind]

    return companyInfo

if __name__ == "__main__":
    getCompanies()
