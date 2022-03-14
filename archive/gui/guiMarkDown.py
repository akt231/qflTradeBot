import streamlit as st


# ====================
# HELPER MARKDOWN FUNCTIONS
# ====================
#<font color=‘red’>THIS TEXT WILL BE RED</font>, unsafe_allow_html=True)

def colorMarkDown(fontcolor = '#33ff33', fontsze = 24, msg="Enter some Text"):
    # will need color to color coding map. default color '#33ff33' is green
    st.markdown(f'<h1 style="color:{fontcolor};font-size:{fontsze}px;">{msg}</h1>', unsafe_allow_html=True)

def sideBarcolorMarkDown(fontcolor = '#33ff33', fontsze = 24, msg="Enter some Text"):
    # will need color to color coding map. default color '#33ff33' is green
    st.sidebar.markdown(f'<h1 style="color:{fontcolor};font-size:{fontsze}px;">{msg}</h1>', unsafe_allow_html=True)

def colorHeader(fontcolor = '#33ff33', fontsze = 30, msg="Enter some Text"):
    # will need color to color coding map. default color '#33ff33' is green
    st.markdown(f'<h1 style="color:{fontcolor};font-size:{fontsze}px;">{msg}</h1>', unsafe_allow_html=True)

def sideBarcolorHeader(fontcolor = '#33ff33', fontsze = 30, msg="Enter some Text"):
    # will need color to color coding map. default color '#33ff33' is green
    st.sidebar.markdown(f'<h1 style="color:{fontcolor};font-size:{fontsze}px;">{msg}</h1>', unsafe_allow_html=True)
