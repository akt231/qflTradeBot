import streamlit as st
import datetime

import pandas as pd
import numpy as np
import os

import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor

def initSessionStates():
    #gui session objects 1st container
    if "maingui_symbol" not in st.session_state:      
        st.session_state.maingui_symbol = None
    if "maingui_intrvl" not in st.session_state:      
        st.session_state.maingui_intrvl = None
    if "maingui_date_from" not in st.session_state:      
        st.session_state.maingui_date_from = None
    if "maingui_date_to" not in st.session_state:      
        st.session_state.maingui_date_to = None
    if "maingui_show_data" not in st.session_state:      
        st.session_state.maingui_show_data = None
    if "maingui_show_chart" not in st.session_state:      
        st.session_state.maingui_show_chart = None
    
    #gui session objects settings container
    if "maingui_show_nontrading_days" not in st.session_state:      
        st.session_state.maingui_show_nontrading_days = None
    if "maingui_chart_style" not in st.session_state:      
        st.session_state.maingui_chart_style = None
    if "maingui_chart_type" not in st.session_state:      
        st.session_state.maingui_chart_type = None

    if "maingui_mav1" not in st.session_state:      
        st.session_state.maingui_mav1 = None
    if "maingui_mav2" not in st.session_state:      
        st.session_state.maingui_mav2 = None
    if "maingui_mav3" not in st.session_state:      
        st.session_state.maingui_mav3 = None




  
    #data session objects
    if "maindata_df_output_l1" not in st.session_state:      
        st.session_state.maindata_df_output_l1 = pd.DataFrame()
    if "maindata_df_output_l2" not in st.session_state:      
        st.session_state.maindata_df_output_l2 = pd.DataFrame()

st.experimental_memo(persist='disk') #study!!!
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

def check_date_from(date_from):
    #st.markdown(f'st.session_state.start_date_input:{type(st.session_state.start_date_input)}')
    #st.markdown(f'st.session_state.start_date_input:{type(st.session_state.start_date_input)}')
    if (st.session_state.end_date_input >= date_from >= st.session_state.start_date_input):
        return True
    else:
        return False

def check_date_to(date_to):
    if (st.session_state.end_date_input >= date_to >= st.session_state.start_date_input):
        return True
    else:
        return False

def get_intrvl_match_symbol(symbol, all_lst):
    intrvl_match = []
    for symb, intrvl, df, df_ochlv in all_lst:
        if symb == symbol:
            intrvl_match.append(intrvl)
    return intrvl_match

def get_df_match_intrvl_symbol(symbol, interval, all_lst):
    df_select = pd.DataFrame()
    for symb, intrvl, df, df_ochlv in all_lst:
        if symb == symbol and intrvl == interval:
            df_select = df_ochlv

    return df_select

def gui_backtest():
    df_dct = st.session_state.df_dct
    
    #unpack the dictionaries
    symbols_lst = df_dct.get("symbols") 
    intrvl_lst = df_dct.get("interval_lst")
    df_lst = df_dct.get("df_lst")
    df_ochlv_lst = df_dct.get("df_ochlv_lst")
    all_lst = list(zip(symbols_lst, intrvl_lst, df_lst, df_ochlv_lst ))

    #get dates input
    today_date_input = datetime.date.today()
    start_date_input = st.session_state.start_date_input
    end_date_input = st.session_state.end_date_input
    
    st.title('QFL Trader App @akt')
    st.markdown('---')    
    data_crit_contain = st.container()
    with data_crit_contain:
        st.subheader('Criteria')
        st.caption('Modify charts Criteria')
        c1, c2, c3 = data_crit_contain.columns([1,1,1])
        with c1:
            st.session_state.maingui_symbol = st.selectbox('Choose stock symbol', options=symbols_lst, index=0) #study!!!
            symbol = st.session_state.maingui_symbol

            intrvl_mtch_syml_lst = get_intrvl_match_symbol(symbol, all_lst)
            st.session_state.maingui_intrvl = st.selectbox('Choose interval', options=intrvl_mtch_syml_lst, index=0)
            
            intrvl = st.session_state.maingui_intrvl
            st.session_state.maindata_df_output_l1 = get_df_match_intrvl_symbol(symbol, intrvl, all_lst)
            df_output_l1 = st.session_state.maindata_df_output_l1
        with c2:
            st.session_state.maingui_date_from = st.date_input('Show data from', start_date_input, min_value=start_date_input, max_value=end_date_input)
            st.session_state.maingui_date_to = st.date_input('Show data from', end_date_input, min_value=start_date_input, max_value=end_date_input)
            date_from = st.session_state.maingui_date_from
            date_to = st.session_state.maingui_date_to
        with c3:
            st.markdown('&nbsp;')
            st.session_state.maingui_show_data = st.checkbox('Show data table', False)
            show_data  = st.session_state.maingui_show_data 
            st.session_state.maingui_show_chart = st.checkbox('Show chart', True)
            show_chart = st.session_state.maingui_show_chart
        st.markdown('---')

    data_sett_contain = st.container()
    with data_sett_contain:
        d1, d2, d3 = data_sett_contain.columns([1,1,1])
        with d1:
            st.subheader('Settings')
            st.caption('Adjust charts settings and then press apply')
            st.session_state.maingui_show_nontrading_days = st.checkbox('Show non-trading days', True)
            show_nontrading_days = st.session_state.maingui_show_nontrading_days
            # https://github.com/matplotlib/mplfinance/blob/master/examples/styles.ipynb
            chart_styles = [
                'default', 'binance', 'blueskies', 'brasil', 
                'charles', 'checkers', 'classic', 'yahoo',
                'mike', 'nightclouds', 'sas', 'starsandstripes'
            ]
            st.session_state.maingui_chart_style = st.selectbox('Chart style', options=chart_styles, index=chart_styles.index('starsandstripes'))
            chart_style = st.session_state.maingui_chart_style
            chart_types = [
                'candle', 'ohlc', 'line', 'renko', 'pnf'
            ]
            st.session_state.maingui_chart_type = st.selectbox('Chart type', options=chart_types, index=chart_types.index('candle'))
            chart_type = st.session_state.maingui_chart_type
            st.session_state.maingui_mav1 = st.number_input('Mav 1', min_value=3, max_value=30, value=3, step=1)
            st.session_state.maingui_mav2 = st.number_input('Mav 2', min_value=3, max_value=30, value=6, step=1)
            st.session_state.maingui_mav3 = st.number_input('Mav 3', min_value=3, max_value=30, value=9, step=1)
            mav1 = st.session_state.maingui_mav1
            mav2 = st.session_state.maingui_mav2
            mav3 = st.session_state.maingui_mav3

    st.session_state.maindata_chk_date_from = check_date_from(date_from)
    st.session_state.maindata_chk_date_to = check_date_to(date_to)
    chk_date_from = st.session_state.maindata_chk_date_from
    chk_date_to   = st.session_state.maindata_chk_date_to
    if all([chk_date_from, chk_date_to] ):
        #data = get_historical_data(df_to_use, str(date_from), str(date_to))  #need to mess this up
        st.session_state.df_output_l2 = get_historical_data(df_output_l1, str(date_from), str(date_to))  #need to mess this up
        df_output_l2 = st.session_state.df_output_l2
        #print(f'shit_02')
        #print(df_output_l1.head(5))
    else:
        if chk_date_from == False:
            st.markdown(f"Please reselect date it is incorrect, Start Date should be between")
            st.markdown(f"StartDate: {start_date_input} and EndDate: {end_date_input}")
        if chk_date_to == False:
            st.markdown(f"Please reselect date it is incorrect, End Date should be between")
            st.markdown(f"StartDate: {start_date_input} and EndDate: {end_date_input}")

    #hide this cntainer in a expander
    data_output_contain = st.container()
    with data_output_contain:
        if show_chart:
            if all([chk_date_from, chk_date_to] ):
                fig, ax = mpf.plot(
                    df_output_l2,
                    title=f'{symbol}, {date_from}:{date_to}',
                    type=chart_type,
                    show_nontrading=show_nontrading_days,
                    mav=(int(mav1),int(mav2),int(mav3)),
                    volume=True,

                    style=chart_style,
                    figsize=(15,10),

                    # Need this setting for Streamlit, see source code (line 778) here:
                    # https://github.com/matplotlib/mplfinance/blob/master/src/mplfinance/plotting.py
                    returnfig=True
                )
                multi = MultiCursor(fig.canvas, ax, color = 'r', lw = 1.2, horizOn = True, vertOn = True)
                st.pyplot(fig)
    #hide this cntainer in a expander
            if show_data:
                st.markdown('---')
                st.dataframe(df_output_l2)


def guiLoad():
    #initialize session states to be used
    initSessionStates()
    gui_backtest()
    