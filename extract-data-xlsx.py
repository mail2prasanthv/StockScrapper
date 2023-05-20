import pandas as pd
import time

data = pd.read_excel(r'MCAP31032023_0.xlsx')

df = pd.DataFrame(data, columns=['Symbol','Company Name'])

for ind in df.index:
    print(df['Symbol'][ind], df['Company Name'][ind])
    time.sleep(0.3) # Sleep for 3 seconds