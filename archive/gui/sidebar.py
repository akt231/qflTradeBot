import streamlit as st
import pandas as pd
import datetime
import sys
from io import StringIO 

# gui helper functions
#local Imports
sys.path.insert(1, './logic')  
import sidebar_backtest as sideBackTest

# streamlit run ./gui/sidebar.py
#helper functions
def init_session_states():
    if "op_option" not in st.session_state:      
        st.session_state.op_option = ''




def prnt_msg_01(op_option, placeholder):
    msg = f'You selected: {op_option}'
    fontcolor = '#800080'
    fontsze = 20
    placeholder.markdown(f'<h1 style="color:{fontcolor};font-size:{fontsze}px;">{msg}</h1>', unsafe_allow_html=True)
    
def gui_sidebar():
    #initialize session states to be used
    init_session_states()
    
    opt_select = st.sidebar.container()
    hd_placeholder = opt_select.empty()
    
    op_typ00 = 'BackTesting'
    op_typ01 = 'Scan(Not Ready)'
    op_typ02 = 'BackTesting(Not Ready)'
    operation_type = (op_typ00, op_typ01, op_typ02)
    st.session_state.op_option = st.sidebar.selectbox('Please select Operation you want', operation_type)
    
    prnt_msg_01(st.session_state.op_option, hd_placeholder)
   
    if st.session_state.op_option == 'BackTesting':
        sideBackTest.gui_backtest()
    elif st.session_state.op_option == op_typ01:
        st.sidebar.write(f"this operation {op_typ01} is not ready")
    elif st.session_state.op_option == op_typ02:
        st.sidebar.write(f"this operation {op_typ02} is not ready")

