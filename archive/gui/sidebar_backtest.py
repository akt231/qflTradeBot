import streamlit as st
from io import StringIO 
import sys
import datetime
from dateutil.relativedelta import relativedelta

# gui helper functions
#local Imports
sys.path.insert(1, './logic')  
import guiMarkDown as guiMrk #used for markdown and write functions
import sidebarlogic as sbl
import mainarealogic as mlg
import mainarea_backtest as mainBackTest

# helper functions
def init_session_states():
    # widget session objects
    if "tckseltyp_radio" not in st.session_state:      
        st.session_state.tckseltyp_radio = ''
    if "sidebar_submit" not in st.session_state:      
        st.session_state.sidebar_submit = False    
    if "start_time_type" not in st.session_state:      
        st.session_state.start_time_type = ""
    if "end_time_type" not in st.session_state:      
        st.session_state.end_time_type = ""
    
    # side form outputs
    if "symbol_lst" not in st.session_state:      
        st.session_state.symbol_lst = []
    
    if "dates_lst" not in st.session_state:      
        st.session_state.dates_lst = []
    if "start_date_input" not in st.session_state:      
        st.session_state.start_date_input = datetime.datetime(1, 1, 1, 0, 0)
    if "end_date_input" not in st.session_state:      
        st.session_state.end_date_input = datetime.datetime(1, 1, 1, 0, 0)
    
    if "data_interval_lst" not in st.session_state:      
        st.session_state.data_interval_lst = []
    
    #if "data_period_type" not in st.session_state:      
    #    st.session_state.data_period_type = ""
    if "data_kline_type" not in st.session_state:      
        st.session_state.data_kline_type = ""

def read_uploadedfile(uploaded_file):
    if uploaded_file is not None:
        ticker_dict = readFileasStr(uploaded_file)
        illegal_tcker = ticker_dict.get("illegal_tcker", "illegal tickerpair not existant")
        legal_tcker   = ticker_dict.get("legal_tcker", "legal tickerpair not existant")
        if len(legal_tcker) > 0:
            symbol_lst = legal_tcker  
            return symbol_lst
    else:
        pass  

def readFileasStr(uploaded_file):
    # To read file as string:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()
    tcker_lst = g12d.get_tcker_lst_fromStringIO(string_data) #?????

    illegal_tcker = list(set(tcker_lst) - set(stocks_df.symbol))
    legal_tcker   = list(set(tcker_lst) - set(illegal_tcker))

    return {"illegal_tcker":illegal_tcker, "legal_tcker":legal_tcker}

#function to be used for streamlit selecting end dates options if start dates are provided
def get_end_date_options():
    keys_start_opts = ['user provided StartDate', "Today's Date", 'Months behind']
    end_opts_user_startdate = ('user provided EndDate', "Today's Date", 'Months ahead')
    end_opts_today = ('Months behind', )
    end_opts_months_behind = ('user provided EndDate', "Today's Date",) 
    values_end_opts = [end_opts_user_startdate, end_opts_today, end_opts_months_behind]
    end_opts_dct = dict(zip(keys_start_opts, values_end_opts))
    return end_opts_dct

# not in use
#function to be used for streamlit selecting start dates options if end dates are provided
def get_start_date_options():
    keys_end_opts = ('user provided EndDate', "Today's Date", 'Months ahead')
    start_opts_user_enddate = ('user provided StartDate',  "Today's Date", 'Months behind')
    start_opts_today = ('user provided StartDate','Months behind')
    start_opts_months_ahead = ('user provided StartDate') 
    
    values_start_opts = (start_opts_user_enddate, start_opts_today, start_opts_months_ahead) 

    start_opts_dct = dict(zip(keys_end_opts, values_start_opts))
    return start_opts_dct

def get_date_from_months(date_input, months_val):
    new_date = date_input + relativedelta(months=months_val)
    return new_date

def print_submit_outputs():
    print("*" * 80)
    print(f'PASS01:SideBar Gui Selection Results')
    print("*" * 80)
    print(f'TickerPair Selection:       {st.session_state.symbol_lst}')
    print(f'Interval Type Selection:    {st.session_state.data_interval_lst}')
    #print(f'Data Period:                {st.session_state.data_period_type}')
    print(f'KLINE type:                 {st.session_state.data_kline_type}')
    print(f'Start Date Selection:       {st.session_state.start_date_input}')
    print(f'End Date Selection:         {st.session_state.end_date_input}')
    print("*" * 80)

def get_tckerpair_lst():
    tckerpair_lst_0 = "Single or Multiple TickerPairs"
    tckerpair_lst_1 = "Load TickerPairs from File"
    tckerpair_lst_2 = "Load All TickerPairs containing a base Ticker"
    tckerpair_lst_3 = "BatchRun all TickerPairs from Binance(Not Ready Yet)"
    tckerpair_lst   = [tckerpair_lst_0, tckerpair_lst_1, tckerpair_lst_2, tckerpair_lst_3] 
    return tckerpair_lst   

def get_unique_tickers_lst(base_asset_lst, quote_asset_lst):
    _lst = []
    _lst.extend(base_asset_lst)
    _lst.extend(quote_asset_lst)
    asset_set = set(_lst) #get unique values
    asset_lst = list(asset_set)
    asset_lst.sort()
    return asset_lst

def get_allticker_based_on_baseticker(base_ticker_unsele, base_ticker_select, symbol_pairs_lst):
    match_lst = []
    if len(base_ticker_select) > 0:
        for base_ticker in base_ticker_select:
            matching = [ticker for ticker in symbol_pairs_lst if base_ticker in ticker]
            #res = list(filter(lambda x: subs in x, test_list))
            match_lst.extend(matching)
        match_lst.sort()
    unmatch_lst = match_lst
    if len(base_ticker_unsele) > 0:
        if len(base_ticker_select) == 0:
            unmatch_lst = symbol_pairs_lst
        if len(base_ticker_select) != 0:
            unmatch_lst = match_lst
        for base_ticker in base_ticker_unsele:
            unmatching = [ ticker for ticker in unmatch_lst if base_ticker not in ticker]
            unmatch_lst = unmatching
        match_lst = unmatch_lst
    return match_lst


def get_sessionstate_dates(date_lst):
    startdate = date_lst[0]
    enddate   = date_lst[1]
    st.session_state.start_date_input = min(startdate, enddate)
    st.session_state.end_date_input = max(startdate, enddate)
    
   

# PRINT functions
def prnt_msg_01(op_option, container):
    msg = f'{op_option}'
    fontcolor = '#800080'
    fontsze = 14
    container.markdown(f'<h1 style="color:{fontcolor};font-size:{fontsze}px;">{msg}</h1>', unsafe_allow_html=True)

def gui_backtest():
    init_session_states()
    contain_ticker_sel = st.sidebar.container()

    contain_data_interval = st.sidebar.container()
    
    contain_data_period_type = st.sidebar.container()
    
    contain_time_sel_01 = st.sidebar.container()
    contain_time_sel_02 = st.sidebar.container()
    contain_time_sel_03 = st.sidebar.container()
    

    
    contain_time_sel_01.markdown("---")
    contain_time_sel_02.markdown("---")  
    contain_time_sel_03.markdown("---") 
    with contain_ticker_sel:
        msg = 'TICKERPAIR SELECTION'
        prnt_msg_01(msg, contain_ticker_sel)
        
        tckerpair_lst = get_tckerpair_lst()
        st.session_state.tckseltyp_radio = contain_ticker_sel.radio("How do you want to select your TickerPairs", tckerpair_lst) 
        
        symbol_pairs_lst = st.session_state.symbolassets_dct.get("symbol","tickerpair not available")
        base_asset_lst   = st.session_state.symbolassets_dct.get("baseAsset","tickerpair not available")
        quote_asset_lst  = st.session_state.symbolassets_dct.get("quoteAsset","tickerpair not available")
        unique_asset_lst = get_unique_tickers_lst(base_asset_lst, quote_asset_lst)
        base_quote_lst = list(map((lambda x,y: x + "-" + y ), base_asset_lst,quote_asset_lst))
        
        if (st.session_state.tckseltyp_radio == tckerpair_lst[0]):
            st.session_state.symbol_lst = contain_ticker_sel.multiselect('Type in the tickerpair here', options = base_quote_lst, default = ["ATOM-USDT", "ATOM-BTC", "ATOM-BUSD"])  # DEFAULT FOR TESTING   #???????
        if (st.session_state.tckseltyp_radio == tckerpair_lst[1]):
            contain_ticker_sel.write(f"***Please Make sure file contents are comma delimited***") 
            uploaded_file = contain_ticker_sel.file_uploader("Choose a file for Ticker Symbol(s)")  
            raw_symbol_lst = read_uploadedfile(uploaded_file)
            if raw_symbol_lst is not None:
                st.session_state.symbol_lst = contain_ticker_sel.multiselect('SymbolPair list from file will appear here', raw_symbol_lst, raw_symbol_lst )  
        if (st.session_state.tckseltyp_radio == tckerpair_lst[2]):
                len_unique_asset_lst = len(unique_asset_lst)
                if len_unique_asset_lst > 0:
                    base_ticker_select = contain_ticker_sel.multiselect('Select Base Ticker(s) to use', unique_asset_lst)  
                    base_ticker_unsele = contain_ticker_sel.multiselect('Select Base Ticker(s) to exclude', unique_asset_lst)  
                else:
                    contain_ticker_sel.markdown(f"Houtston we have a problem! No Unique Tickers!!!")
                
                tcker_lst = get_allticker_based_on_baseticker(base_ticker_unsele, base_ticker_select, symbol_pairs_lst)
                len_tcker_lst = len(tcker_lst)
                if len_tcker_lst > 0:
                    contain_ticker_sel.markdown(f"{len_tcker_lst} tickerpairs selected")
                    st.session_state.symbol_lst = contain_ticker_sel.multiselect('Ticker list based on base Ticker provided', options = tcker_lst, default = tcker_lst)  # DEFAULT FOR TESTING   #???????
                else:
                    contain_ticker_sel.markdown(f"Please select ticker to get tickerpairs")
        if (st.session_state.tckseltyp_radio == tckerpair_lst[3]):
            len_all_symbolpairs = len(symbol_pairs_lst)
            st.session_state.symbol_lst = symbol_pairs_lst
            contain_ticker_sel.write(f"***{len_all_symbolpairs} TickerPairs will be processed***") 

    with contain_data_interval:  
        msg = 'INTERVAL TYPE SELECTION'
        prnt_msg_01(msg, contain_data_interval) 
         
        approved_data_interval_type = ("1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo")
        default_data_interval_type = ("1h", "1d")
        st.session_state.data_interval_lst = contain_data_period_type.multiselect('Select DATA PERIOD TYPE TO EXTRACT?', approved_data_interval_type, default_data_interval_type)
        
    with contain_data_period_type:
        msg = 'DATA PERIOD TYPE SELECTION'
        prnt_msg_01(msg, contain_data_period_type)
        
        #approved_data_period_type = ("monthly", "daily(not in use)")
        #st.session_state.data_period_type = contain_data_period_type.selectbox('Select DATA PERIOD TYPE TO #EXTRACT?',approved_data_period_type)
        ## we will stick to a default type for now/ to be removed when we start using daily data
        #st.session_state.data_period_type = "monthly"
        contain_data_period_type.markdown(f'both monthly and daily Binance kline data will be downloaded as required by start and end dates')  
        # we'll stick to a default type for now/to be removed when we start using data type apart from klines data
        st.session_state.data_kline_type = "klines" 
        contain_data_period_type.markdown(f'{st.session_state.data_kline_type}: (CandleSticks) Charts will be produced')       
    
    with contain_time_sel_01:
        msg = 'TIME RANGE SELECTION: START/END DATES'
        prnt_msg_01(msg, contain_time_sel_01)

        #start_opts_dct = get_start_date_options()
        end_opts_dct = get_end_date_options()
        
        #keys_start_opts = start_opts_dct.keys()
        keys_end_opts   = end_opts_dct.keys()

        #temp values for start and end dates
        start_date_input = datetime.date(2022, 1, 1)
        end_date_input = datetime.date.today()
        
        st.session_state.start_time_type = contain_time_sel_01.selectbox('Please select type of Start Date', keys_end_opts )
        
        start_time_type = st.session_state.start_time_type 
        end_time_lst = end_opts_dct.get(start_time_type)
        st.session_state.end_time_type = contain_time_sel_01.selectbox('Please select type of End Date', end_time_lst ) 
       
        approved_dates_type = ('user provided StartDate', 'user provided EndDate')
        months_dates_type = ('Months ahead', 'Months behind')
        
        default_startdate_dt, default_enddate_dt = sbl.get_default_dates()

        if st.session_state.start_time_type in approved_dates_type:
            #start_date_input = contain_time_sel_02.date_input(f"Select {st.session_state.start_time_type}", datetime.date(2022, 1, 1)) 
            start_date_input = contain_time_sel_02.date_input(f"Select {st.session_state.start_time_type}", default_startdate_dt) 
        if st.session_state.start_time_type in months_dates_type:
            #below statement to another container
            start_months_val = contain_time_sel_02.number_input(f'Insert Number of {st.session_state.start_time_type}', min_value = 1)
            if st.session_state.start_time_type == 'Months ahead':
                months_val = start_months_val
            if st.session_state.start_time_type == 'Months behind':
                months_val = start_months_val * -1
                start_date_input  = get_date_from_months(end_date_input,  months_val) #??????
            #if start_date_input > end_date_input:
            #   start_date_input, end_date_input = end_date_input, start_date_input
            contain_time_sel_03.markdown(f'{st.session_state.start_time_type} is: {start_months_val}')
        if st.session_state.start_time_type ==  "Today's Date":
            today_date_input = datetime.date.today()
            start_date_input = contain_time_sel_02.date_input(f"Select {st.session_state.start_time_type} as StartDay", today_date_input)
       
        
        
        if st.session_state.end_time_type in approved_dates_type:
            #end_date_input = contain_time_sel_02.date_input(f"Select {st.session_state.end_time_type}", datetime.date(2022, 1, 20)) 
            end_date_input = contain_time_sel_02.date_input(f"Select {st.session_state.end_time_type}", default_enddate_dt) 

        if st.session_state.end_time_type in months_dates_type:
            #below statement to another container
            end_months_val = contain_time_sel_02.number_input(f'Insert Number of {st.session_state.end_time_type}', min_value = 1)
            if st.session_state.end_time_type == 'Months ahead':
                months_val = end_months_val
            if st.session_state.end_time_type == 'Months behind':
                months_val = end_months_val * -1
            end_date_input  = get_date_from_months(start_date_input,  months_val) #??????
            #if start_date_input > end_date_input:
            #       start_date_input, end_date_input = end_date_input, start_date_input
            contain_time_sel_03.markdown(f'{st.session_state.end_time_type} is: {end_months_val}')
        if st.session_state.end_time_type ==  "Today's Date":
            today_date_input = datetime.date.today()
            end_date_input = contain_time_sel_02.date_input(f"Select {st.session_state.end_time_type} as EndDay", today_date_input)

        st.session_state.dates_lst = [start_date_input, end_date_input]
        get_sessionstate_dates(st.session_state.dates_lst)        
        contain_time_sel_03.markdown(f'Start Date is: {st.session_state.start_date_input}')
        contain_time_sel_03.markdown(f'End Date is: {st.session_state.end_date_input}')        
        
    
    st.session_state.sidebar_submit = st.sidebar.button("Submit")
    
    #this is trouble if placed in mainBackTest.guiLoad(), it causes problems
    if st.session_state.sidebar_submit or (st.session_state.reruns>1): 
        print_submit_outputs()
        sbl.post_side_bar_logic() 
        
        #mlg.pre_main_area_logic() 
        #mainBackTest.gui_backtest()

        mainBackTest.guiLoad()
        
        


