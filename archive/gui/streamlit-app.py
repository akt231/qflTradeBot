import streamlit as st
import pandas as pd
import datetime

import os
import sys


# ====================
#local Imports
# ====================
sys.path.insert(1, './logic')  
import sidebarlogic as sbl
import sidebar as side
# C:\Users\AKT\AppData\Local\Programs\Python\Python310\

# ====================
# RUN APP!!!!!
# ====================
# to run streamlit app
# streamlit run ./gui/streamlit-app.py

# ====================
# WAITING TASKS
# ====================
# Need to comment every function description/line/action done!!!!!!!

# ====================
# FIRST SETTINGS FUNCTIONS
# ====================
# set page config options
# webpage for page_icons: https://emojipedia.org/search/?q=chart
st.set_page_config(page_title="Cryto AlgoTrading", 
                        page_icon="📈",
                        layout="wide", 
                        initial_sidebar_state="expanded" 
                        #,menu_items={
                        #'Get Help': 'https://www.extremelycoolapp.com/help',
                        #'Report a bug': "https://www.extremelycoolapp.com/bug",
                        #'About': "# This is a header. This is an *extremely* cool app!"}
                        ) #auto None
# ====================
# SETTINGS FUNCTIONS
# ====================
def set_df_format():
    # ====================
    # DATAFRAME FORMATTING 
    # ====================
    pd.options.display.float_format = '{:,}'.format

def init_page_settings():
    # settings to remove top right hamburger menu
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

    # settings to remove padding between components
    padding = 0
    st.markdown(f""" <style>
        .reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {padding}rem;
            padding-left: {padding}rem;
            padding-bottom: {padding}rem;
        }} </style> """, unsafe_allow_html=True)

def init_session_states():
    if "reruns" not in st.session_state: 
        st.session_state.reruns = 0
    if "binance_MainKey" not in st.session_state:      
        st.session_state.binance_MainKey = '' 
    if "binance_SecretKey" not in st.session_state:      
        st.session_state.binance_SecretKey = ''

def print_reruns_val(reruns):
   reruns += 1
   printReruns = f'main program has ran {reruns} times'
   print("&" * 60)
   print(printReruns)
   print("&" * 60)
   return reruns

def get_keys():
    apikey_binance_main = os.environ.get('ApiKey_Binance', 'Not Set')
    apikey_binance_secret = os.environ.get('ApiKey_Binance_secret', 'Not Set')
    return {"binance main key":apikey_binance_main, "binance secret key":apikey_binance_secret}

def init_session_apikeys():
    binance_keys = get_keys()
    st.session_state.binance_MainKey = binance_keys.get("binance main key","Binance main key not in env. vars.")
    st.session_state.binance_SecretKey = binance_keys.get("binance secret key","Binance main key not in env. vars.")

def init_all_settings():
    init_page_settings()    #initialise required page settings
    init_session_states()   #initialise session states variables to use
    set_df_format()         #set format type of df's
    init_session_apikeys()  #initialise binance api keys

def showGui():
    # overall page app settings
    init_all_settings()
    st.session_state.reruns = print_reruns_val(st.session_state.reruns)
    
    # calc inits session states and side bar logic
    sbl.init_session_states()
    sbl.pre_side_bar_logic()
    
    # sidebar gui
    side.gui_sidebar()       #create side-bar gui
                             #create main area gui
    

       

if __name__ == "__main__":
   showGui()    
