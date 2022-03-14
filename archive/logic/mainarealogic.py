import streamlit as st
import pandas as pd
import numpy as np
import os

import mplfinance as mpf
import matplotlib.pyplot as plt

def create_df_plot(df):
    fig = mpf.figure(style='yahoo', figsize=(8,6))
    mpf.plot(df)
    st.pyplot(fig) 


def pre_main_area_logic():
    df_dct = st.session_state.df_dct
    
    #unpack the dictionaries
    symbols_lst = df_dct.get("symbols") 
    intrvl_lst = df_dct.get("interval_lst")
    df_lst = df_dct.get("df_lst")
    
    #cycle through df's to modify for use
    for df in df_lst:
        create_df_plot(df)
        
        