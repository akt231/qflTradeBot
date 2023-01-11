# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 18:47:22 2023

@author: afola
"""

# Import necessary libraries
import pandas as pd
import yfinance as yf
import pandas as pd
from time import time, sleep
from finvizfinance.quote import finvizfinance

import numpy as np
import datetime
from tqdm import tqdm
import math
import telepot
import re


Tickers1=["xela","nvos","otrk"]
Tickers=["pik","brezr","mtc","vs","snmp","baos","kspn","hpco","mtp","smit","sprc","acon","jcse","jxjt","vine","aimd","op","nbrv","snoa",
         "cyan","nerv","otrk"]
["aim","ibio","zyne","mbio","lci","alzn","cycn","sesn","akba","tnxp","blrx","acst","vrpx","adxn","fbio","cdtx","cntb","aqst",
         "abvc","stsa","nhwk","cyan","fwbi","otlk","onct",""]
Tickers1=["jzxn","brezr","snmp","gfai","rdhl","syta","akan","krbp"]
Tickers1=["nept","cyrn","vive","aimd","gvp","jcse","alr","pte","qncx","mdrr","nrbo","bkyi","blrx","acst","rvyl","vcnx","gray","lfly","ssy",
 "sbig","bttr","lci","rvyl","vcnx","gray","lfly","ssy","acon","tovx","ivda","moxc","imbi","zkin","ufab","ocg","ncty","ear","reli",
 "wavd","bsgm","cnet","ibio","lixt","tomz","msn","mobq","apm","itp"]
# Load the data
tradelist=[]

for ticker in Tickers1:

    data12 = yf.download(ticker,
                      start="2022-12-1", end="2023-1-13",
                      #period="1mo",
                      interval="1h",
                      prepost=True, asynchronous=True, retry=20, status_forcelist=[404, 429, 500, 502, 503, 504])
    stock = finvizfinance(ticker)
    stock_fundament = stock.ticker_fundament()
    stock_fundament.pop('EPS this Y')
    stock_fundament.pop('Beta')
    stock_fundament.pop('Book/sh')
    stock_fundament.pop('Current Ratio')
    stock_fundament.pop('Dividend')
    stock_fundament.pop('Dividend %')
    stock_fundament.pop('Earnings')
    stock_fundament.pop('Employees')
    stock_fundament.pop('EPS (ttm)')
    stock_fundament.pop('EPS Q/Q')
    stock_fundament.pop('Forward P/E')
    stock_fundament.pop('Gross Margin')
    stock_fundament.pop('Income')
    stock_fundament.pop('Index')
    stock_fundament.pop('Industry')
    stock_fundament.pop('LT Debt/Eq')
    stock_fundament.pop('Oper. Margin')
    stock_fundament.pop('P/B')
    stock_fundament.pop('P/C')
    stock_fundament.pop('P/E')
    stock_fundament.pop('P/FCF')
    stock_fundament.pop('P/S')
    stock_fundament.pop('Payout')
    stock_fundament.pop('PEG')
    stock_fundament.pop('Perf Half Y')
    stock_fundament.pop('Perf Quarter')
    stock_fundament.pop('Perf Week')
    stock_fundament.pop('Perf Year')
    stock_fundament.pop('Perf YTD')
    stock_fundament.pop('Prev Close')
    stock_fundament.pop('Profit Margin')
    stock_fundament.pop('Quick Ratio')
    stock_fundament.pop('Recom')
    stock_fundament.pop('Rel Volume')
    stock_fundament.pop('ROA')
    stock_fundament.pop('ROE')
    stock_fundament.pop('ROI')
    stock_fundament.pop('Sales')
    stock_fundament.pop('Sector')
    #stock_fundament.pop('Short Ratio')
    stock_fundament.pop('Sales past 5Y')
    stock_fundament.pop('Sales Q/Q')
    
    stock_fundament.pop('EPS next 5Y')
    stock_fundament.pop('EPS next Q')
    stock_fundament.pop('EPS next Y')
    stock_fundament.pop('EPS past 5Y')
    stock_fundament.pop('52W High')
    stock_fundament.pop('52W Low')
    stock_fundament.pop('ATR')
    stock_fundament.pop('Debt/Eq')
    stock_fundament.pop('RSI (14)')
    data12["Float"]=stock_fundament['Shs Float']
    
    data12['symbol']=ticker
    data12['Min']=data12['Close'].min()
    data12['Max']=data12['Close'].max()
    data12['track']=(data12['Close']-data12['Min'])*100/data12['Min']
    #data12['Check']=((data12.Close[-1:])-(min(data12.Close)))*100/(min(data12.Close))
    data12['t-1']=data12['track'].shift(-1)
    data12.loc[(data12['track']<10) & (data12['t-1']>10),'signal']='buy stock/Call'
    data12.loc[(data12['track']==0),'signal']='RESET'
    data12.loc[(data12['track']>=21 ),'signal']='SELL Target1'
    data12["lastprice"]=data12["Close"][-1]
    data12["profit"]=((data12["lastprice"]/data12["Close"])-1)*100
    # these are the 20-30 percent profit
    data12["20P"]=data12["Close"]*1.2
    data12["30P"]=data12["Close"]*1.3
    data12["diff"]=data12["Close"]-data12["20P"]
    #these are to compute the options strike price ranges
    data12["currentprice"]=data12["Close"][-1]
    data12["highs"]=max(data12["High"][-800:])
    data12["lows"]=min(data12["Low"][-800:])
    data12['Targ-Opt-price']=(data12['highs']+data12['lows'])/2
    
    #data12.loc[(data12['track']>=20),'signal']='SELL'
    #data12.loc[(data12['track']>=20),'signal']='SELL'
    # data12.loc[(data12['track']>=20),'signal']='SELL'
    #data12.loc[(data12['track']>=20),'signal']='SELL'
    #data12.loc[(data12['track']>=20),'signal']='SELL'
    
    #this is the point where the buy signal occurs
 
    trade=pd.DataFrame((data12.loc[lambda data12:data12['signal']=='RESET', :]))
    tradelist.append(trade)
    trade_listfinal=pd.concat(tradelist)
    # Define the strategy

# Backtest the strategy
def backtest(data12):
    # Set initial capital
    capital = 1000.0
    # Set initial cash
    cash = capital
    # Set initial shares
    shares = 0
    # Create empty list to store portfolio value
    portfolio_value = []
    # Loop through each day's data
    for index, row in data12.iterrows():
        # Buy shares
        if row['signal'] == 'RESET':
            shares += cash / row['Close']
            cash = 0
        # Sell shares
        elif row['signal'] == 'SELL':
            cash += shares * row['High']
            shares = 0
        # Calculate portfolio value
        portfolio_value.append((shares * row['High']) + cash)
     
    # Return portfolio value
    return portfolio_value

# Run the backtest
portfolio_value = backtest(data12)


# Print the final portfolio value
print(portfolio_value)
