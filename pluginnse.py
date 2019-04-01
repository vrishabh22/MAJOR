from datetime import date
import pandas as pd
import lxml
from nsepy import get_history

print('Enter symbol---')
cols=['Date','Open','High','Low','Close','Volume']
df_new=pd.DataFrame(columns=cols)
#sym=input()
print(df_new)
stock = input("Enter stock name(ex:GOOGL, AAPL): ")

df = get_history(symbol=stock,
                   start=date(2015,1,1),
                   end=date(2015,1,10))
print(df.head())
df.reset_index(drop = False, inplace = True)
print(df.head())
#df.reset_index()
#df_new=df[['Date','Open','High','Low','Close']].copy()
#df_new.set_index('Date')

#df_new.set_index('Date')
df_new['Date']=df['Date']
df_new['Open']=df['Open']
df_new['High']=df['High']
df_new['Low']=df['Low']
df_new['Close']=df['Close']
df_new['Volume']=df['Volume']

df_new.set_index('Date',inplace=True)

print(df_new.head())