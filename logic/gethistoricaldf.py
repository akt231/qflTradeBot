import sys
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from importlib import reload
from decouple import config

sys.path.insert(1, './logic')  
import helperfunctions as hlpf
reload(hlpf)


def getdf():
    #=====================================================
    #get config data for use
    #=====================================================
    symbolfile = config('symbolfile') #filepath for getting list of symbols
    default_data_interval_lst = config('default_data_interval_lst', cast=lambda v: [s.strip() for s in v.split(',')]) #list of applicable intervals
    approved_data_kline_lst = config('approved_data_kline_lst', cast=lambda v: [s.strip() for s in v.split(',')]) #list of binance type of data output
    default_data_kline_type = config('default_data_kline_type') #default binance type of data output we will use
    start_months_val = config('start_months_val', default=3, cast=int)

    #=====================================================
    #get dictionary of all symbol pairs from binance
    #=====================================================
    allsymbolassets_dct = hlpf.get_allsymbolassets_dct()
    symbol_pairs_lst = allsymbolassets_dct.get("symbol")
    base_asset_lst   = allsymbolassets_dct.get("baseAsset")
    quote_asset_lst  = allsymbolassets_dct.get("quoteAsset")
    unique_asset_lst = hlpf.get_unique_tickers_lst(base_asset_lst, quote_asset_lst)
    base_quote_lst_hyphen = list(map((lambda x,y: x + "-" + y ), base_asset_lst,quote_asset_lst))
    base_quote_lst_nohyph = list(map((lambda x,y: x + y ), base_asset_lst,quote_asset_lst))

    #=====================================================
    #get list of all to play against
    #=====================================================
    all_basequote_lst = []
    all_basequote_lst.extend(base_quote_lst_hyphen)
    all_basequote_lst.extend(base_quote_lst_nohyph)

    #=====================================================
    #get symbol pairs to work on from file
    #=====================================================
    lines = []
    printvarqty = 60
    print("=" * printvarqty)
    print(f'symbol pairs will be loaded from\n',symbolfile)
    print("=" * printvarqty)
    chk_file, illegal_symbpairs_lst, symbol_lst = hlpf.chk_symbolpair_file(symbolfile, all_basequote_lst)

    #=====================================================
    #get interval type to use *** done in config file already
    #=====================================================

    #=====================================================
    #get dates to use
    #=====================================================
    #default value of dates is 3 months prior to today till today
    today_date_input = date.today()
    end_date_dt = today_date_input

    months_val = start_months_val * -1
    start_date_dt  = hlpf.get_date_from_months(end_date_dt,  months_val)
    print(f'difference in months btw start date&end date: {start_months_val}')
    print(f'start date: {start_date_dt}')
    print(f'end date: {end_date_dt}')

    #=====================================================
    #print out of all input data to use
    #=====================================================
    print("=" * 75)
    print(f'print out of all input data to use')
    print("=" * 75)
    print(f'symbol_lst:                 {symbol_lst}')
    print(f'start_date_dt:              {start_date_dt}')
    print(f'end_date_dt:                {end_date_dt}')
    print(f'default_data_interval_lst:  {default_data_interval_lst}')
    print(f'default_data_kline_type:    {default_data_kline_type}')

    #=====================================================
    #required input data
    #=====================================================
    #symbol_lst
    #start_date_dt
    #end_date_dt
    #default_data_interval_type
    #default_data_kline_type
    kline_input_dct = hlpf.get_kline_dict(symbol_lst, start_date_dt, end_date_dt, default_data_interval_lst, default_data_kline_type)

    #=====================================================
    #check for kline dict data
    #=====================================================
    status = kline_input_dct.get("status")
    if status == "success":
        print("=" * 75)
        print(f"status:stage 01ofXX: input data for df dict extraction successful")
        print("=" * 75)
        print(kline_input_dct)

    #=====================================================
    #get zip files from binance and process them into df's
    #=====================================================
    #can this section be done with threads asyncronously????
    #persistency needs to be added to this function!!!!!!!!
    #not done!!!!!!need to log the data date parts missing-last day may be missing
    df_dct = hlpf.get_kline_data(kline_input_dct)
    status = df_dct.get("status")
    if status == "success":
        print("=" * 75)
        print(f"status:stage 02ofXX: raw ochlv df data successfully extracted")
        print("=" * 75)

    #=====================================================
    #unpack df_dct for use
    #=====================================================
    symbols_lst = df_dct.get("symbols") 
    intrvl_lst = df_dct.get("interval_lst")
    df_lst = df_dct.get("df_lst")
    df_ochlv_lst = df_dct.get("df_ochlv_lst")
    all_lst = list(zip(symbols_lst, intrvl_lst, df_lst, df_ochlv_lst ))

    #=====================================================
    # quick check of data unpacked
    #=====================================================
    print(f'nos of symbolpairs: {len(symbols_lst)}')
    print(f'nos of intervals: {len(intrvl_lst)}')
    print(f"nos of full df's: {len(df_lst)}")
    print(f"nos of ochlv df's: {len(df_ochlv_lst)}")

    print(f'list of symbolpairs: {symbols_lst}')
    print(f'list of intervals: {intrvl_lst}')

    for cnt, (symbol, intrvl, df_full, df_ochlv) in enumerate(all_lst):
        print(f'count: {cnt}|symbol: {symbol}|interval:{intrvl}|rows orig df:{len(df_full.index)}|rows ochlv df:{len(df_ochlv.index)}')
    
    return all_lst