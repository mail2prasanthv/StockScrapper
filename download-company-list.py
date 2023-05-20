import requests
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
response = requests.get(
    "https://static.nseindia.com//s3fs-public/inline-files/MCAP31032023_0.xlsx", headers=headers)
companylist_xlsx = open("MCAP31032023_0.xlsx", 'wb')
companylist_xlsx.write(response.content)
companylist_xlsx.close()


