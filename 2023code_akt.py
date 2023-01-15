# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 18:47:22 2023

@author: afola
#TODO LIST
1. pls check the results for the ticdkers i tested: ["xela","nvos","otrk"]
2. please explain what the following columns/values mean:
    2a. data12['signal'] = 'buy stock/Call'  removed
    2b. data12['signal'] = 'RESET'
    2c. data12['signal'] = 'SELL Target1'
    2d. data12['lastprice'] 
    2e. data12['profit'] 

3. please explain what the following columns/values mean:
    please are this your target values?
    data12["20P"] 
    data12["30P"] 
    data12["diff"]  
"""

# Import necessary libraries
import pandas as pd
import yfinance as yf
import pandas as pd
from time import time, sleep
from finvizfinance.quote import finvizfinance

import datetime
from datetime import date

import numpy as np
import datetime
from tqdm import tqdm
import math
import telepot
import re

def get_ticker_lst():
    #Tickers1=["xela","nvos","otrk"]
    #Tickers=["pik","brezr","mtc","vs","snmp","baos","kspn","hpco","mtp","smit","sprc","acon","jcse","jxjt","vine","aimd","op","nbrv","snoa",
    #         "cyan","nerv","otrk"]
    #["aim","ibio","zyne","mbio","lci","alzn","cycn","sesn","akba","tnxp","blrx","acst","vrpx","adxn","fbio","cdtx","cntb","aqst",
    #         "abvc","stsa","nhwk","cyan","fwbi","otlk","onct",""]
    #Tickers1=["jzxn","brezr","snmp","gfai","rdhl","syta","akan","krbp"]
    #Tickers1=["nept","cyrn","vive","aimd","gvp","jcse","alr","pte","qncx","mdrr","nrbo","bkyi","blrx","acst","rvyl","vcnx","gray","lfly","ssy",
    # "sbig","bttr","lci","rvyl","vcnx","gray","lfly","ssy","acon","tovx","ivda","moxc","imbi","zkin","ufab","ocg","ncty","ear","reli",
    # "wavd","bsgm","cnet","ibio","lixt","tomz","msn","mobq","apm","itp"]
    #Tickers1=['amzn', 'spy', 'bac', ]
    ticker_lst=["xela","nvos","otrk"]
    return ticker_lst


def pop_notneeded_column(stock_fundament):
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
    return stock_fundament
    


def getdata12(ticker):
    # Load the data
    data12 = yf.download(ticker, 
                          start="2022-12-1", end="2023-1-13",
                          #period="1mo",
                          interval="1h",
                          prepost=True)
    stock = finvizfinance(ticker)
    stock_fundament = stock.ticker_fundament()
    stock_fundament = pop_notneeded_column(stock_fundament)
    
    #calculation columns
    data12["Float"]=stock_fundament['Shs Float']
    data12['symbol']=ticker
    data12['Min']=data12['Close'].min()
    data12['Max']=data12['Close'].max()
    data12['track']=(data12['Close']-data12['Min'])*100/data12['Min']
    data12['t-1']=data12['track'].shift(-1)
    
    #signal column values
    data12.loc[(data12['track']<10) & (data12['t-1']>10),'signal'] = 'buy stock/Call'
    data12.loc[(data12['track']==0),'signal'] = 'RESET'
    
    data12.loc[(data12['track'] >= 15  & data12['track'] <= 20 ),'signal'] = 'T1:P:15-20'
    data12.loc[(data12['track'] > 20   & data12['track'] <= 25 ),'signal'] = 'T2:P:20-25'
    data12.loc[(data12['track'] > 25   & data12['track'] <= 31 ),'signal'] = 'T3:P:25-31'
    data12.loc[(data12['track'] > 31   & data12['track'] <= 38 ),'signal'] = 'T4:P:31-38'
    data12.loc[(data12['track'] > 38   & data12['track'] <= 45 ),'signal'] = 'T5:P:38-45'
    data12.loc[(data12['track'] > 45   & data12['track'] <= 50 ),'signal'] = 'T6:P:45-50'
    data12.loc[(data12['track'] > 51   & data12['track'] <= 55 ),'signal'] = 'T7:P:51-55'
    data12.loc[(data12['track'] > 55   & data12['track'] <= 61 ),'signal'] = 'T8:P:55-61'
    data12.loc[(data12['track'] > 61   & data12['track'] <= 65 ),'signal'] = 'T9:P:61-65'
    data12.loc[(data12['track'] > 65 ),'signal'] = 'T10:P:65>'
    
    data12["lastprice"] = data12["Close"][-1]
    data12["profit"] = ((data12["lastprice"]/data12["Close"])-1)*100
    
    #profit taking
    # these are the 20-30 percent profit targets
    data12["20P"] = data12["Close"] * 1.2
    data12["30P"] = data12["Close"] * 1.3
    data12["diff"] = data12["Close"]-data12["20P"]
    
    #these are to compute the options strike price ranges
    data12["currentprice"] = data12["Close"][-1]
    data12["highs"] = max(data12["High"][-800:])
    data12["lows"] = min(data12["Low"][-800:])
    data12['Targ-Opt-price'] = (data12['highs'] + data12['lows'])/2

    return data12

#this is the point where the buy signal occurs
def gettradelist(data12):   
    tradelist=[]
    trade=pd.DataFrame((data12.loc[lambda data12:data12['signal']=='RESET', :]))
    tradelist.append(trade)
    trade_listfinal=pd.concat(tradelist)
    return trade_listfinal
    
        # Define the strategy

# Backtest the strategy
def backtest(data12):
    # Set capital and cash
    capital = 1000.0    # Set initial capital
    cash = capital      # Set initial cash
    shares = 0          # Set initial shares
   
    # Create empty list to store portfolio value
    portfolio_value = []
    
    # Loop through each day's data
    shares_lst =[]
    cash_lst = []
    for index, row in data12.iterrows():
        newrow = row
        # Buy shares
        if row['signal'] == 'RESET':
            shares += cash / row['Close']
            cash = 0
        # Sell shares
        elif row['signal'] == 'SELL':
            shares = 0
            cash += shares * row['High']

        newrow['shares'] = shares
        newrow['cash'] = cash
        
        new_rows.append(newrow.values)
        df_new = data12.append(pd.DataFrame(newrow, columns=data12.columns)).reset_index()


        # Calculate portfolio value
        portfolio_value.append((shares * row['High']) + cash)
     
    # Return portfolio value
    return portfolio_value

def batchrun_tickers(ticker_lst):
    ticker_dct = {}
    for ticker in ticker_lst:
        #get ticker created data
        df_data12 = getdata12(ticker)
        ticker_dct[ticker] = df_data12
        df_data12 =backtest(df_data12)
        
        #write data to excel file
        filepath = './results/'
        filedate = date.today().strftime('%Y%m%d')
        path_and_filename = f'{filepath}{ticker}.xlsx'
        with pd.ExcelWriter(path_and_filename) as writer:
            df_data12.to_excel(writer, sheet_name = filedate )

if __name__ == "__main__":
   ticker_lst = get_ticker_lst()
   batchrun_tickers(ticker_lst)
   
   ## Return portfolio value
   #portfolio_value = backtest(data12)   
   #
   ## Print the final portfolio value
   #print(portfolio_value)
