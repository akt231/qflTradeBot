from binance.client import Client
import streamlit as st
import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urljoin, urlencode

import wget
from zipfile import ZipFile

import pandas as pd
import numpy as np
import os

from datetime import datetime
from dateutil.relativedelta import relativedelta



#The Google Python Style Guide has the following convention:
#module_name, package_name, ClassName, method_name, ExceptionName, function_name, 
#GLOBAL_CONSTANT_NAME, global_var_name, instance_var_name, function_parameter_name, local_var_name.


# get api keys
#my_python_path = f'C:\Users\AKT\AppData\Local\Programs\Python\Python310\'

# =====================
# helper functions
# =====================
def init_session_states():
    if "symbolassets_dct" not in st.session_state:      
        st.session_state.symbolassets_dct = {}
        
    if "df_dct" not in st.session_state:      
        st.session_state.df_dct = {}

# =====================
# main code begins here
# =====================
class BinanceException(Exception):
    def __init__(self, status_code, data):

        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"

        # Python 2.x
        # super(BinanceException, self).__init__(message)
        super().__init__(message)

def get_allsymbolassets():
    ''' function to return all ticker pairs'''
    apikey_binance_main = os.environ.get('ApiKey_Binance', 'Not Set')
    apikey_binance_secret = os.environ.get('ApiKey_Binance_secret', 'Not Set')
    client = Client(apikey_binance_main, apikey_binance_secret)
    symbols = client.get_exchange_info()
    df = pd.DataFrame(symbols['symbols'])

    df_spot = df[df.isSpotTradingAllowed == True]
    df_symbol_assets = df_spot.filter(["symbol", "baseAsset", "quoteAsset"])

    print("we are done")
    return df_symbol_assets

#function to check if pair exist in df_symbol_assets
@st.cache
def get_allsymbolassets_dct():
    df = get_allsymbolassets()
    symbolasset_dict = df.to_dict(orient="list");
    return symbolasset_dict
    
def get_symbolmarketcap_json():
    apikey_binance_main = os.environ.get('ApiKey_Binance', 'Not Set')
    apikey_binance_secret = os.environ.get('ApiKey_Binance_secret', 'Not Set')
    #BASE_URL = 'https://api.binance.com'
    BASE_URL = 'https://www.binance.com'

    headers = {
        'X-MBX-APIKEY': apikey_binance_main
    }

    #PATH =  '/api/v1/time'
    PATH =  '/exchange-api/v2/public/asset-service/product/get-products'
    params = None

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, params=params)
    if r.status_code == 200:
        #print(json.dumps(r.json(), indent=2))
        data = r.json()
        return data
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    
    #You need to take the field cs and multiply it to the current asset price. In this case, it will be field c


def get_symbolmarketcap():
    json_data = get_symbolmarketcap_json()
    #df = pd.DataFrame.from_dict(pd.json_normalize(json_data), orient='columns')
    df = pd.json_normalize(json_data, 
                           record_path =['data'],
                           meta=['code', 'message', 'success']
                           )
    
    df["c"] = pd.to_numeric(df["c"], errors='coerce')
    df["marktCap"] = df["c"] * df["cs"]
    print(df.head(5))

def get_kline_historical_df(input_dict):
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
    
    output_directory = "./downloads"
    #filename = wget.download(url)

    #print(f'URL AND FILE NAMES')
    #print("+" * 80)
    #print(f'input_type: {input_type}')
    #print(f'url: {url}')
    #print(f'url_checksum: {url_checksum}')
    #print(f'filename_zip: {filename_zip}')
    #print(f'filename_checksum: {filename_checksum}')
    #print(f'filename_csv: {filename_csv}')
    
    filename_path = output_directory + "/" + filename_zip
    cond_file_exist = os.path.exists(filename_path)
    if cond_file_exist == False:
        try:
            file_zipped = wget.download(url, out=output_directory)
            #actiate this for checksum#file_checksum = wget.download(url_checksum, out=output_directory)
        except:
            #need to confirm if month is current month then switch to daily and get data
            print("*" * 60)
            print(f'this url may not exist \n {url}') 
            print("*" * 60)
            print('<base_url>/data/spot/monthly/klines/<symbol_in_uppercase>/<interval>/<symbol_in_uppercase>-<interval>-<year>-<month>.zip')
            print('https://data.binance.vision/data/spot/monthly/klines/BNBUSDT/1m/BNBUSDT-1m-2019-01.zip')
            print("*" * 60)

        else:
            print("download from {url} successful")


    with ZipFile(filename_path, 'r') as zipObj:
       # Extract all the contents of zip file in different directory
       zipObj.extractall('downloads')
       #print('File is unzipped') 
    
    if os.path.exists(filename_path):
          os.remove(filename_path)
    else:
      print(f"The zipfile {filename_path} does not exist")
    
    filename_path = output_directory + "/" + filename_csv      
    if os.path.exists(filename_path):
        #print(f"PASS03a:The csv file {filename_path} exists")
        df = pd.read_csv(filename_path, names=["Open time",	"Open",	"High",	"Low",	"Close", 
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
       
        os.remove(filename_path)
        rows_nos = len(df.index)
      
        return df
    else:
      print(f"The csv file {filename_path} does not exist")

#tasks
    # we need to do a checksum of file downloaded

def convert_date_yearmonth(date_datetime):
    month = date_datetime.month
    year = date_datetime.year
    month_str = str(month)
    year_str = str(year)
    date_str = year_str + '-' + month_str
    return date_str

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

def get_default_dates():
    default_enddate_dt = datetime.today()
    default_startdate_dt = default_enddate_dt - relativedelta(months=2)
    return default_startdate_dt, default_enddate_dt
    
def get_kline_dict():
#inputs from streamlit gui logic 
    #get start-end year-month date list
    startdate = st.session_state.start_date_input.strftime("%Y-%m-%d")  #'2021-01-21'
    enddate = st.session_state.end_date_input.strftime("%Y-%m-%d")      #'2021-10-21'
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
    #data_period_type = st.session_state.data_period_type    #"monthly"
    # choose klines klines for chart info
    klines = st.session_state.data_kline_type   #"klines"
         
    #choose interval = "1h" #All intervals are supported: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo
    interval_lst = st.session_state.data_interval_lst  #"1h"        
    
    #choose symbol_in_uppercase = "ATOMBTC".upper()            
    symbols_lst = st.session_state.symbol_lst    #"ATOMBTC".upper()   
    
    data_dict = {
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

def get_df_ochlv(df_charts):
    df = pd.DataFrame()
       
    df['Open'] = df_charts['Open']
    df['Close'] = df_charts['Close']
    df['High'] = df_charts['High']
    df['Low'] = df_charts['Low']
    df['Volume'] = df_charts['Volume']
    df.index = df_charts.index
    return df

def print_kline_dict_outputs(kline_dict):
    print("*" * 80)
    print(f'PASS02:Data Dict Selection Results')
    print("*" * 80)
    print(f'startdate: {kline_dict.get("startdate")}')
    print(f'enddate: {kline_dict.get("enddate")}')
    print(f'yearmnths_rnge: {kline_dict.get("yearmnths_rnge")}')
    
    print(f'days_rnge: {kline_dict.get("days_rnge")}')
    print(f'klines: {kline_dict.get("klines")}')
    print(f'symbols_lst: {kline_dict.get("symbols_lst")}')
    print(f'interval_lst: {kline_dict.get("interval_lst")}')
    print(f'datepart_filename: {kline_dict.get("datepart_filename")}')

def get_kline_data():        
    kline_dict = get_kline_dict()
    #print_kline_dict_outputs(kline_dict)
    
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
    #we will use generator fuctions here
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
                        sheetname = f"{symbol}_{interval}_{datepart_filename}"
                        df_charts.to_excel(f"./downloads/{sheetname}.xlsx", sheet_name=f'{interval}_{datepart_filename}')
        cnt_symbol += 1
    df_dct = {"symbols": symb_lst,"interval_lst": intrvl_lst  , "df_lst": df_lst, "df_ochlv_lst": df_ochlv_lst}
    return df_dct    

def pre_side_bar_logic():
    st.session_state.symbolassets_dct = get_allsymbolassets_dct()

def print_df_dct(df_dct):
    symbols_lst = df_dct.get("symbols") 
    intrvl_lst = df_dct.get("interval_lst")
    df_lst = df_dct.get("df_lst") 
    
    print("*" * 50)
    print(f'symbols_lst: {len(symbols_lst)}|intrvl_lst: {len(intrvl_lst)}|df_lst: {len(df_lst)}|')

    cnt_symbol = 0
    for symbol in symbols_lst:
        print("*" * 50)
        print(f"symbol: {symbol}")
        print(f"interval: {intrvl_lst[cnt_symbol]}")
        print(df_lst[cnt_symbol].head(5))
        cnt_symbol += 1    
    
def post_side_bar_logic():
    st.session_state.df_dct = get_kline_data()
    print("=" * 80)
    print(f"Charts Dataframe successfully gotten.........")
    print("=" * 80)
    
    df_dct = st.session_state.df_dct
    print_df_dct(df_dct)   