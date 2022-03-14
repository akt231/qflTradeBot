from binance.client import Client
import pandas as pd
import numpy as np
import os

from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

import wget
from zipfile import ZipFile

import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urljoin, urlencode

import mplfinance as mpf
import matplotlib.pyplot as plt


#function to return all ticker pairs
def get_allsymbolassets():
    ''' function to return all ticker pairs'''
    apikey_binance_main = os.environ.get('ApiKey_Binance', 'Not Set')
    apikey_binance_secret = os.environ.get('ApiKey_Binance_secret', 'Not Set')
    client = Client(apikey_binance_main, apikey_binance_secret)
    symbols = client.get_exchange_info()
    df = pd.DataFrame(symbols['symbols'])

    df_spot = df[df.isSpotTradingAllowed == True]
    df_symbol_assets = df_spot.filter(["symbol", "baseAsset", "quoteAsset"])

    return df_symbol_assets

#function to check if pair exist in df_symbol_assets
def get_allsymbolassets_dct():
    '''function to check if pair exist in df_symbol_assets'''
    df = get_allsymbolassets()
    symbolasset_dict = df.to_dict(orient="list");
    return symbolasset_dict

def get_unique_tickers_lst(base_asset_lst, quote_asset_lst):
    _lst = []
    _lst.extend(base_asset_lst)
    _lst.extend(quote_asset_lst)
    asset_set = set(_lst) #get unique values
    asset_lst = list(asset_set)
    asset_lst.sort()
    return asset_lst

def get_filecontent_lst(symbolfile):
    lines = []
    symbolfile = "./inputs/symbols_inputlst.txt"
    with open(symbolfile) as txtfile:
        for line in txtfile:
            line = line.strip()
            lines.append(line)

    lst_main = []
    for count,line in enumerate(lines, start = 1):
        lst = []
        line = line.replace(' ,', ',')
        line = line.replace(', ', ',')
        lst = line.split(',')
        if '' in lst:
            lst.remove('')
        lst_main.extend(lst)
    return lst_main

def chk_symbolpair_file(symbolfile, all_basequote_lst):
    lines = []
    symbol_lst = get_filecontent_lst(symbolfile)
    print(f'nos of symbols from file is',len(symbol_lst))
    
    illegal_symbpairs_lst = []
    for symbpair in symbol_lst:
        if symbpair not in all_basequote_lst:
            illegal_symbpairs_lst.append(symbpair)
    if len(illegal_symbpairs_lst) > 0:
        chk_file = False
        print(f'the following are illegal symbol pairs\n, they dont exist in binance list,\npls look at file again\n',illegal_symbpairs_lst)
        return chk_file, illegal_symbpairs_lst, symbol_lst
    else:
        chk_file = True
        print(f'Success!!!!, all symbol pair items from file exist on binance list of symbol pairs')
        print(f'list of symbols to be processed\n{symbol_lst}')
        return chk_file, illegal_symbpairs_lst, symbol_lst
    
def get_date_from_months(date_input, months_val):
    new_date = date_input + relativedelta(months=months_val)
    return new_date

def get_historical_enddate_dt(end_date_dt):
    today_dt = datetime.today()
    today_strf = datetime.today().strftime("%Y-%m-%d")
    enddate = end_date_dt.strftime("%Y-%m-%d")
    
    if enddate == today_strf:
        end_date_dt = end_date_dt + relativedelta(days=-1)
    return end_date_dt

  

def get_kline_dict(default_symbol_lst, start_date_dt, end_date_dt, default_data_interval_lst, default_data_kline_type):
    startdate = start_date_dt.strftime("%Y-%m-%d")    #'2021-01-21'
    enddate   = end_date_dt.strftime("%Y-%m-%d")      #'2021-10-21'
    
    end_date_dt = get_historical_enddate_dt(end_date_dt)

    yrmnth_dict = get_time_range_dict(startdate, enddate)
    
    
    yearmnths_rnge = yrmnth_dict.get("yearmnths_rnge", "year-month data not existing") 
    days_rnge      = yrmnth_dict.get("days_rnge", "days data not existing") 
    
    # getting filename for each symbolpair
    if (len(yearmnths_rnge) > 1):
        yrmnth_name = yearmnths_rnge[0].replace("-","") + "-" + yearmnths_rnge[-1].replace("-","")
    elif (len(yearmnths_rnge) == 1):
        yrmnth_name = yearmnths_rnge[0].replace("-","")
    else:
        yrmnth_name = ""

    flenme_00 = ""
    flenme_01 = ""
    flenme_02 = ""
    datepart_filename = ""
    chk_startdate_lst = startdate.split("-")
    chk_enddate_lst = enddate.split("-")
    
    
    if chk_startdate_lst[0] == chk_enddate_lst[0]:
        flenme_00 = str(chk_startdate_lst[0])
        if chk_startdate_lst[1] == chk_enddate_lst[1]:
            flenme_01 = str(chk_startdate_lst[1])
            flenme_02 = str(chk_startdate_lst[2]) + "-" + str(chk_enddate_lst[2])
            datepart_filename = flenme_00 + "_" + flenme_01 + "_" + flenme_02
        else:
            datepart_filename = str(startdate).replace("-","") + "-" + str(enddate).replace("-","")
            
    else:
        datepart_filename = str(startdate).replace("-","") + "-" + str(enddate).replace("-","")

        
    if (datepart_filename == "__") or (datepart_filename == "-"):
        print("This range of dates has a problem")
        raise Exception()
    else:
        pass
        
    # choose data_period_type  "monthly" or daily   
    #data_period_type = data_period_type    #"monthly"
    # choose klines klines for chart info
    klines = default_data_kline_type   #"klines"
         
    #choose interval = "1h" #All intervals are supported: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo
    interval_lst = default_data_interval_lst  #"1h"        
    
    #choose symbol_in_uppercase = "ATOMBTC".upper()            
    symbols_lst = default_symbol_lst    #"ATOMBTC".upper()   
    
    data_dict = {
                "status"            : "success",
                "startdate"         : startdate,
                "enddate"           : enddate,
                "yearmnths_rnge"    : yearmnths_rnge,
                "days_rnge"         : days_rnge,
                #"data_period_type" : data_period_type,
                "klines"            : klines,
                "symbols_lst"       : symbols_lst,
                "interval_lst"      : interval_lst,
                "datepart_filename" : datepart_filename
                }        
    return data_dict 

def get_time_range_dict(startdate, enddate):
    startdate_dt = datetime.strptime(startdate, '%Y-%m-%d')
    enddate_dt = datetime.strptime(enddate, '%Y-%m-%d') #+ relativedelta(months=1)
    
    today_strf = datetime.today().strftime("%Y-%m-%d")
    today_dt = datetime.strptime(today_strf, '%Y-%m-%d')
    yesterday_dt = today_dt - relativedelta(days=1)
    
    # check if bothdates are beyond today
    chk_startdate_dt_beyond_today = False
    chk_enddate_dt_beyond_today = False
    if max(today_dt, startdate_dt) == startdate_dt:
        chk_startdate_dt_beyond_today = True
    if max(today_dt, enddate_dt) == enddate_dt:
        chk_enddate_dt_beyond_today = True
    
    # adjust dates for dates beyond yesterday 
    startdate_dt = adjust_dates_beyond_today(startdate_dt) 
    enddate_dt = adjust_dates_beyond_today(enddate_dt) 

    #test if  dates are in current year/month
    startdate_test_in_curr_month = test_day_in_currmonth(startdate_dt)
    enddate_test_in_curr_month = test_day_in_currmonth(enddate_dt)
   
    #scenerio 1 startdates and enddates are dates in the future, we'll need to end the program!!!
    scenerio_chk_01 = (chk_startdate_dt_beyond_today == True and chk_enddate_dt_beyond_today == True)
    if chk_startdate_dt_beyond_today == True and chk_enddate_dt_beyond_today == True:
        #print(f"datecheck: scenerio 1")
        print(f"Please adjust start and end dates. they are dates in the future!!!!")
        mnths_rnge = []
        days_rnge = []
        
    #scenerio 2 start date and end date in current year/month: we will get range of days between start and enddates
    if (startdate_test_in_curr_month==True) and (enddate_test_in_curr_month==True) and not scenerio_chk_01:
        #print(f"datecheck: scenerio 2")
        days_rnge = pd.date_range(startdate_dt, enddate_dt, freq='D').strftime("%Y-%m-%d").tolist()
        mnths_rnge = []
    #scenerio 3 end date onlyin current year/month: we will get a. range months from start date till month 
    # before curr year/month and b. days between 1st day of curr year/month to enddates
    elif (startdate_test_in_curr_month==False) and (enddate_test_in_curr_month==True):   
        #print(f"datecheck: scenerio 3")
        #get the monthX before this month and calculate the month range between startdate_dt and monthX
        thisday_lastmonth = enddate_dt - relativedelta(months=1)
        thisday_lastmonth_yr = thisday_lastmonth.year
        thisday_lastmonth_mnth = thisday_lastmonth.month
        lastmonth_dt = datetime.strptime(f"{thisday_lastmonth_yr}-{thisday_lastmonth_mnth}", '%Y-%m') + relativedelta(months=1)
        startdate_bymonth_dt = datetime.strptime(f"{startdate_dt.year}-{startdate_dt.month}", '%Y-%m')
        mnths_rnge = pd.date_range(startdate_bymonth_dt, lastmonth_dt, freq='M').strftime("%Y-%m").tolist()
        
        #get the days from 1st of curr year/month to enddate_dt
        firstday_curr_yearmonth = datetime.strptime(f"{today_dt.year}-{today_dt.month}-01", '%Y-%m-%d')
        days_rnge = pd.date_range(firstday_curr_yearmonth, enddate_dt, freq='D').strftime("%Y-%m-%d").tolist()
   #scenerio 4 we want data by month only
    elif (startdate_test_in_curr_month==False) and (enddate_test_in_curr_month==False): 
        #print(f"datecheck: scenerio 4")
        startdate_bymonth_dt = datetime.strptime(f"{startdate_dt.year}-{startdate_dt.month}", '%Y-%m')
        enddate_dt = enddate_dt
        enddate_bymonth_dt = datetime.strptime(f"{enddate_dt.year}-{enddate_dt.month}", '%Y-%m') + relativedelta(months=1)
        mnths_rnge = pd.date_range(startdate_bymonth_dt, enddate_bymonth_dt, freq='M').strftime("%Y-%m").tolist() 
        days_rnge = []  
    
    #print(f"day range: \n {days_rnge}")
    #print(f"month range: \n {mnths_rnge}")
    
    time_range_dct = {"days_rnge": days_rnge, "yearmnths_rnge": mnths_rnge}
    return time_range_dct

def adjust_dates_beyond_today(date_dt):
    today_strf = datetime.today().strftime("%Y-%m-%d")
    today_dt = datetime.strptime(today_strf, '%Y-%m-%d')
    if max(date_dt, today_dt) == date_dt:
        date_dt = today_dt - relativedelta(days=1) #we wont get data to download beyond yesterday on binance
        return date_dt 
    else:
        return date_dt  

def test_day_in_currmonth(date_dt):
    today_dt = datetime.today()
    
    curr_yr = today_dt.year
    curr_mnth = today_dt.month
    
    date_yr = date_dt.year
    date_mnth = date_dt.month
    
    if (curr_yr == date_yr) and (curr_mnth == date_mnth):
        return True
    else:
        return False

def get_kline_data(kline_dict):        
    symbols_lst = kline_dict.get("symbols_lst")
    interval_lst = kline_dict.get("interval_lst")
    yearmonths_rnge =  kline_dict.get("yearmnths_rnge")  
    days_rnge =  kline_dict.get("days_rnge") 
    datepart_filename =  kline_dict.get("datepart_filename") 
    symb_lst = []
    intrvl_lst = []
    df_lst = [] 
    df_ochlv_lst = []    
    cnt_symbol = 0 
    #we should use generator fuctions here?
    for symbol in symbols_lst:
        symbol = symbol.replace("-","") 
        symbol = symbol.upper()
        interval_set = set(interval_lst)
        for intrvl_set_item in interval_set:
            intrvl_input_dict_lst = []
            for interval in interval_lst:
                if intrvl_set_item == interval:
                    
                    if len(yearmonths_rnge) > 0:
                        for yearmonth in yearmonths_rnge:
                            #print(f"getting dict for following \n symbol: {symbol} \n interval: {interval} \n yearmonth: {yearmonth}")
                            year = yearmonth.split("-")[0]
                            month = yearmonth.split("-")[1]
                            input_dict = {
                            "timetype"          : "Year-Month",
                            "startdate"         : kline_dict.get("startdate", "months_range data not existing"),
                            "enddate"           : kline_dict.get("enddate", "enddate data not existing"),
                            "yearmonth"         : yearmonth,
                            "days"               : "",
                            #"data_period_type"  : kline_dict.get("data_period_type", "data_period_type data not existing"),
                            "klines"            : kline_dict.get("klines", "klines data nexisting"),
                            "symbol"            : symbol,
                            "interval"          : interval           
                            }
                            intrvl_input_dict_lst.append(input_dict)

                    if len(days_rnge) > 0:
                        for day in days_rnge:
                            #print(f"getting dict for following \n symbol: {symbol} \n interval: {interval} \n day: {day}")
                            input_dict = {
                                        "timetype"          : "Days",
                                        "startdate"         : kline_dict.get("startdate", "months_range data not existing"),
                                        "enddate"           : kline_dict.get("enddate", "enddate data not existing"),
                                        "yearmonth"         : "",
                                        "days"               : day,
                                        #"data_period_type"  : kline_dict.get("data_period_type", "data_period_type data not existing"),
                                        "klines"            : kline_dict.get("klines", "klines data not existing"),
                                        "symbol"            : symbol,
                                        "interval"          : interval              
                                        }
                            intrvl_input_dict_lst.append(input_dict)
            
                    if len(intrvl_input_dict_lst) > 0:
                        cnt_input_dict_lst = 0
                        df_charts = pd.DataFrame() 
                        for input_dict in intrvl_input_dict_lst:
                            df = get_kline_historical_df(input_dict)
                        
                            df_charts = df_charts.append(df, ignore_index=False, verify_integrity=True)

                            cnt_input_dict_lst += 1
                        symb_lst.append(symbol)
                        intrvl_lst.append(input_dict.get("interval"))
                        
                        df_ochlv = get_df_ochlv(df_charts)

                        df_ochlv_lst.append(df_ochlv)
                        df_lst.append(df_charts)
                        
                        ##for testing purpose only-confirming df's were extracted
                        #print(f'symbol: {symbol}|interval: {interval}')
                        #print(f'df_charts')
                        #print(df_charts.head(5))
                        #print(df_charts.tail(5))
                        #
                        #print(f'df_ochlv')
                        #print(df_ochlv.head(5))
                        #print(df_ochlv.tail(5))
                        
                        sheetname = f"{symbol}_{interval}_{datepart_filename}"
                        df_charts.to_excel(f"./outputs/binance.xlsx/{sheetname}.xlsx", sheet_name=f'{interval}_{datepart_filename}')
        cnt_symbol += 1
    df_dct = {"status": "success", "symbols": symb_lst,"interval_lst": intrvl_lst  , "df_lst": df_lst, "df_ochlv_lst": df_ochlv_lst}
    return df_dct  

def get_kline_historical_df(input_dict):
    #this data gathering needs to be done asyncrounously for each symbol pair!!!!!!!!!!!!!!
    # download a single file
    base_url = 'https://data.binance.vision'
    data_period_type = input_dict.get("data_period_type")
    klines = input_dict.get("klines")
    symbol_in_uppercase = input_dict.get("symbol")
    #All intervals are supported: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo
    interval = input_dict.get("interval")
    input_type = input_dict.get("timetype")
    if input_type == "Year-Month":
        yearmonth = input_dict.get("yearmonth")
        year = yearmonth.split("-")[0]
        month = yearmonth.split("-")[1]
    if input_type == "Days":
        days = input_dict.get("days")
    
    if input_type == "Year-Month":
        url = f"{base_url}/data/spot/monthly/{klines}/{symbol_in_uppercase}/{interval}/{symbol_in_uppercase}-{interval}-{yearmonth}.zip"
        url_checksum = url + ".CHECKSUM"
        filename_zip = f"{symbol_in_uppercase}-{interval}-{yearmonth}.zip"
        filename_checksum = filename_zip + ".CHECKSUM"
        filename_csv = f"{symbol_in_uppercase}-{interval}-{yearmonth}.csv"
    elif input_type == "Days":
        url = f"{base_url}/data/spot/daily/{klines}/{symbol_in_uppercase}/{interval}/{symbol_in_uppercase}-{interval}-{days}.zip"
        url_checksum = url + ".CHECKSUM"
        filename_zip = f"{symbol_in_uppercase}-{interval}-{days}.zip"
        filename_checksum = filename_zip + ".CHECKSUM"
        filename_csv = f"{symbol_in_uppercase}-{interval}-{days}.csv"
    
    output_directory_zip = "./outputs/binance.zip"
    output_directory_csv = "./outputs/binance.csv"

    filename_path_zip = output_directory_zip + "/" + filename_zip
    filename_path_csv = output_directory_csv + "/" + filename_csv
    
    cond_file_exist_zip = os.path.exists(filename_path_zip)
    cond_file_exist_csv = os.path.exists(filename_path_csv)
    
    #Downloading the file by sending the request to the URL
    req = requests.get(url)
    reqstatcode = req.status_code

    if reqstatcode == 404: 
        #not done yet!!!!! need to print out a listing of files that this did not produce zip files for
        print(f'response code: {reqstatcode}|{url} likely does not exist')
    elif reqstatcode == 200:
        print(f'response code: {reqstatcode}|{url} downloaded successfully')
    else:
        print(f'response code: {reqstatcode}|{url} funny response code develop further')

    if reqstatcode == 200: 
        # Writing the file to the local file system
        with open(filename_path_zip,'wb') as output_file:
            output_file.write(req.content)

        with ZipFile(filename_path_zip, 'r') as zipObj:
           # Extract all the contents of zip file in different directory
           zipObj.extractall('outputs/binance.csv')
           #print('File is unzipped') 

        #we will uncomment this section!!!!!!!!!!!!!!!!!!!
        if os.path.exists(filename_path_zip):
              os.remove(filename_path_zip)
        else:
          pass
          #print(f"The zipfile {filename_path_zip} does not exist")


        if os.path.exists(filename_path_csv):
            #print(f"PASS03a:The csv file {filename_path} exists")
            df = pd.read_csv(filename_path_csv, names=["Open time",	"Open",	"High",	"Low",	"Close", 
                                                      "Volume",	"Close time", "Quote asset volume",
                                                      "Number of trades", "Taker buy base asset volume",
                                                      "Taker buy quote asset volume", "Ignore"
                                                      ], parse_dates=['Open time'], index_col='Open time')

            #df['symbol'] = pd.Series([symbol_in_uppercase for x in range(len(df.index))])
            df['symbol'] = symbol_in_uppercase

            column_to_move = df.pop('symbol')
            df.insert(0, column_to_move.name, column_to_move)

            df.index.name = 'Open time'
            df.index = pd.to_datetime(df.index,unit='ms')

            df['Close time'] = pd.to_datetime(df['Close time'],unit='ms')

            for i in df.columns:
                  if i.lower() != 'symbol' and i.lower() != 'open time' and i.lower() != 'close time':
                      df[i] = df[i].astype(float)

            os.remove(filename_path_csv)
            rows_nos = len(df.index)

            return df
        else:
          print(f"The csv file {filename_path_csv} does not exist")
    else:
        #print(f'response code: {reqstatcode}|{url} funny response code: will return empty dataframe')
        df = pd.DataFrame(columns=["symbol", "Open time",	"Open",	"High",	"Low",	"Close", 
                                                      "Volume",	"Close time", "Quote asset volume",
                                                      "Number of trades", "Taker buy base asset volume",
                                                      "Taker buy quote asset volume", "Ignore"
                                                      ])
        return df
#tasks
    # we need to do a checksum of file downloaded

def get_df_ochlv(df_charts):
    df = pd.DataFrame()
       
    df['Open'] = df_charts['Open']
    df['Close'] = df_charts['Close']
    df['High'] = df_charts['High']
    df['Low'] = df_charts['Low']
    df['Volume'] = df_charts['Volume']
    df.index = df_charts.index
    return df

def create_df_plot(df):
    fig = mpf.figure(style='yahoo', figsize=(8,6))
    mpf.plot(df)
    st.pyplot(fig) 

def pre_main_area_logic(df_dct):
    #unpack the dictionaries
    symbols_lst = df_dct.get("symbols") 
    intrvl_lst = df_dct.get("interval_lst")
    df_lst = df_dct.get("df_lst")
    
    #cycle through df's to modify for use
    for df in df_lst:
        create_df_plot(df)

# this are not effective functions delete it!!!!!
def get_intrvl_match_symbol(symbol, all_lst):
    intrvl_match = []
    for symb, intrvl, df, df_ochlv in all_lst:
        if symb == symbol:
            intrvl_match.append(intrvl)
    return intrvl_match

# this are not effective functions delete it!!!!!
def get_df_match_intrvl_symbol(symbol, interval, all_lst):
    df_select = pd.DataFrame()
    for symb, intrvl, df, df_ochlv in all_lst:
        if symb == symbol and intrvl == interval:
            df_select = df_ochlv

    return df_select

def get_historical_data(df, start_date = None, end_date = None ):
    #print(f'testing my df {start_date}|{end_date}')
    #print(df.head(5))
 
    if start_date and end_date:
        #df = df[(df.index >= start_date) & (df.index <= end_date)]
        df_new = df.loc[start_date:end_date]
    if start_date and not end_date:
        #df = df[df.index >= start_date]
        df_new = df.loc[start_date:]
    if not start_date and end_date:
        #df = df[df.index <= end_date]
        df_new = df.loc[:end_date]
    #print(f'testing my df')
    #print(df_new.head(5))
    return df_new

def plotchart(df, symbol, date_from, date_to, interval, chart_type, show_nontrading_days, mavset, chart_style):
    #fig, ax = mpf.plot(
    #                df,
    #                title=f'symbol: {symbol}',
    #                type={chart_type},
    #                show_nontrading={show_nontrading_days},
    #                mav={mavset},
    #                volume=True,
    #                style={chart_style},
    #                figsize=(15,10),
    #                returnfig=True
    #            )
    mpf.plot(df,
            title=f'{symbol}\n{date_from}:{date_to}\nInterval: {interval}',
            type=chart_type,
            show_nontrading=show_nontrading_days,
            mav=mavset,
            volume=True,
            figsize=(12,8),
            returnfig=True,
            tight_layout=True,
            xrotation=90,
            style=chart_style
            )
#title=f'symbol: {symbol}\nDate Slice: {date_from}:{date_to}\nInterval: {interval}',
#             title=f'symbol: {symbol}\nDate Slice: {date_from}:{date_to}\nInterval: {interval}',
#figsize=(15,10),


def get_sliced_startdate_dt(datapts_btw_start_end, datapts_shift, datapts_shift_factor, interval, end_date_dt):
    approved_data_interval_lst = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"]
    approved_data_val_lst = [1, 3, 5, 15, 30, 1, 2, 4, 6, 8, 12, 1, 3, 1, 1]
    approved_data_type_lst = ["minutes", "minutes", "minutes", "minutes", "minutes", "hours", "hours", "hours", "hours", "hours", "hours", "days", "days", "weeks", "months"]

    date_from = end_date_dt
    date_to = end_date_dt
    for cnt, approved_data_interval in enumerate(approved_data_interval_lst):
        if interval == approved_data_interval:
            approved_data_val = approved_data_val_lst[cnt]
            approved_data_type = approved_data_type_lst[cnt]

            datapts_datadiff = datapts_btw_start_end * approved_data_val
            datapts_datashift = datapts_shift * datapts_shift_factor 
            
            datapts_dataval_start = datapts_datadiff + datapts_datashift
            datapts_dataval_end   = datapts_datashift
            
            if approved_data_type == "minutes":
                date_from = end_date_dt - relativedelta(minutes=datapts_dataval_start)
                date_to = end_date_dt - relativedelta(minutes=datapts_dataval_end)
            elif approved_data_type == "hours":
                date_from = end_date_dt - relativedelta(hours=datapts_dataval_start)
                date_to = end_date_dt - relativedelta(hours=datapts_dataval_end)
            elif approved_data_type == "days":
                date_from = end_date_dt - relativedelta(days=datapts_dataval_start)
                date_to = end_date_dt - relativedelta(days=datapts_dataval_end)
            elif approved_data_type == "weeks":
                date_from = end_date_dt - relativedelta(weeks=datapts_dataval_start)
                date_to = end_date_dt - relativedelta(weeks=datapts_dataval_end)
            elif approved_data_type == "months":
                date_from = end_date_dt - relativedelta(months=datapts_dataval_start)
                date_to = end_date_dt - relativedelta(months=datapts_dataval_end)
    return  [date_from, date_to]

def getsliced_date_lsts(intrvl_lst, datapts_btw_start_end, datapts_shift, datapts_shift_factor):
    date_from_lst = []
    date_to_lst = []
    
    #today_date_input = datetime.date.today()
    today_date_input = date.today()
    end_date_dt = today_date_input
    end_date_dt = get_historical_enddate_dt(end_date_dt)
    


    for interval in intrvl_lst:
        date_ = get_sliced_startdate_dt(datapts_btw_start_end, datapts_shift, datapts_shift_factor, interval, end_date_dt)

        date_from = date_[0]
        date_to = date_[1]

        date_from_lst.append(date_from)
        date_to_lst.append(date_to)
    return date_from_lst, date_to_lst

def get_sliced_df(symbols_lst, intrvl_lst, date_from_lst, date_to_lst, df_lst, df_ochlv_lst):
    df_full_slicedate_lst = []
    df_ochlv_slicedate_lst = []
    all_lst = list(zip(symbols_lst, intrvl_lst, date_from_lst, date_to_lst, df_lst, df_ochlv_lst ))
    for cnt, (symbol, intrvl, date_from, date_to, df_full, df_ochlv) in enumerate(all_lst):
        df_full_slicedate = get_historical_data(df_full, str(date_from), str(date_to))
        df_ochlv_slicedate = get_historical_data(df_ochlv, str(date_from), str(date_to))
        
        df_full_slicedate_lst.append(df_full_slicedate)
        df_ochlv_slicedate_lst.append(df_ochlv_slicedate)
    
    #quick check of df dates
    
    slicedate_lst = list(zip(symbols_lst, intrvl_lst, df_full_slicedate_lst, df_ochlv_slicedate_lst, df_lst, df_ochlv_lst))   
    for cnt, (symbol, intrvl, df_full_slicedate, df_ochlv_slicedate, df_full, df_ochlv) in enumerate(slicedate_lst):
        print(f'count: {cnt}|symbol: {symbol}|interval: {intrvl}|rows orig df sliced by date:{len(df_full_slicedate.index)} of {len(df_full.index)}|rows ochlv df sliced by date:{len(df_ochlv_slicedate.index)} of {len(df_ochlv.index)}')       
    
    return slicedate_lst
            
                
    
            