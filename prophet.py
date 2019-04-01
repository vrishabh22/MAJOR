# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pandas_datareader.data as web
from fbprophet import Prophet
import datetime
from flask import Flask, render_template
from flask import request, redirect
from pathlib import Path
import os
import os.path
import csv
from itertools import zip_longest
import lxml
from nsepy import get_history

app = Flask(__name__)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response
    
@app.route("/")
def first_page():
    """
    original_end = 175
    forecast_start = 200
    stock = "IBM"
    return render_template("plot.html", original = original_end, forecast = forecast_start, stock_tinker = stock)
    """
    tmp = Path("static/Dalal-Street.png")
    tmp_csv = Path("static/numbers.csv")
    if tmp.is_file():
        os.remove(tmp)
    if tmp_csv.is_file():
        os.remove(tmp_csv)
    return render_template("index.html")

#function to get stock data
def yahoo_stocks(stock, startd, endd):

    cols=['Date','Open','High','Low','Close','Volume']
    df_new=pd.DataFrame(columns=cols)
    #sym=input()
    #print(df_new)
    #stock = input("Enter stock name(ex:GOOGL, AAPL): ")

    df = get_history(symbol=stock,
                    start=startd,
                    end=endd)
    #print(df.head())
    df.reset_index(drop = False, inplace = True)
    #print(df.head())
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
    return df_new
    #print(df_new.head())
    #return web.DataReader(symbol, 'yahoo', start, end)
    
def get_historical_stock_price(stock):
    print ("Getting historical stock prices for stock ", stock)
    
    #get 7 year stock data for Apple
    startDate = datetime.datetime(2015, 1, 1).date()
    #date = datetime.datetime.now().date()
    #endDate = pd.to_datetime(date)
    endDate = datetime.datetime(2019, 3, 27).date()
    stockData = yahoo_stocks(stock, startDate, endDate)
    return stockData

@app.route("/plot" , methods = ['POST', 'GET'] )
def main():
    if request.method == 'POST':
        stock = request.form['companyname']
        df_whole = get_historical_stock_price(stock)

        df = df_whole.filter(['Close'])
        
        df['ds'] = df.index
        #log transform the ‘Close’ variable to convert non-stationary data to stationary.
        #arr=[]
        df['y']=np.log(df['Close'])
        
        original_end = df['Close'].iloc[-1]
        
        model = Prophet()
        model.fit(df)

        #num_days = int(input("Enter no of days to predict stock price for: "))
        
        num_days = 10
        future = model.make_future_dataframe(periods=num_days)
        forecast = model.predict(future)
        
        print (forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
        
        #Prophet plots the observed values of our time series (the black dots), the forecasted values (blue line) and
        #the uncertainty intervalsof our forecasts (the blue shaded regions).
        
        #forecast_plot = model.plot(forecast)
        #forecast_plot.show()
        
        #make the vizualization a little better to understand
        df.set_index('ds', inplace=True)
        forecast.set_index('ds', inplace=True)
        #date = df['ds'].tail(plot_num)
        
        #join based on union i.e include close column
        viz_df = df.join(forecast[['yhat', 'yhat_lower','yhat_upper']], how = 'outer')
        viz_df['yhat_scaled'] = np.exp(viz_df['yhat'])

        #close_data = viz_df.Close.tail(plot_num)
        #forecasted_data = viz_df.yhat_scaled.tail(plot_num)
        #date = future['ds'].tail(num_days+plot_num)

        close_data = viz_df.Close
        forecasted_data = viz_df.yhat_scaled
        date = future['ds']
        #date = viz_df.index[-plot_num:-1]
        forecast_start = forecasted_data[-num_days]

        d = [date, close_data, forecasted_data]
        export_data = zip_longest(*d, fillvalue = '')
        with open('static/numbers.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(("Date", "Actual", "Forecasted"))
            wr.writerows(export_data)
        myfile.close()

        return render_template("plot.html", original = round(original_end,2), forecast = round(forecast_start,2), stock_tinker = stock.upper())
'''
if __name__ == "__main__":
    main()
'''

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
