import streamlit as st
import numpy as np
import os, re
import tabMain, tab01, tab02, tab03, tab04, tab05

import importlib
for remodulie in [tabMain, tab01, tab02, tab03, tab04, tab05]:
    importlib.reload(remodulie)

st.set_page_config(layout="wide", page_icon="https://lh3.googleusercontent.com/WebglHOYlW-2P7ADP9oUSSrgy12PHyAE6GP_jmJkQOZZ1XH7Pa_7216EK2qS7iJFvncqOaDjg40BrYdzPbB9qNwn", page_title="LoL_Dashboard")

# @st.cache(allow_output_mutation=True,suppress_st_warning=True)
def page_dashboard():
    ## Title
    st.title('LoL Data Analysis')
    st.text("LOL 데이터 시각화 서비스 개발 - LJ, Elina, Jamie")
    st.markdown("""<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">""", unsafe_allow_html=True
               )
        
    # Setting Tab
    query_params = st.experimental_get_query_params()
    tabs = ["Main", "챔피언기록", "유저기록", "인게임정보", "챔피언통계", "랭킹"]

    if "tab" in query_params:
        active_tab = query_params["tab"][0]
    else:
        active_tab = "Home"

    if active_tab not in tabs:
        st.experimental_set_query_params(tab="Main")
        active_tab = "Main"

    li_items = "".join(
        f"""
        <li class="nav-item">
            <a class="nav-link {'active' if t == active_tab else ''}" href="/?tab={t}">{t}</a>
        </li>
        """
        for t in tabs
    )
    tabs_html = f"""
        <ul class="nav nav-tabs">
        {li_items}
        </ul>
    """
    st.markdown(tabs_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    return active_tab

if __name__ == "__main__":
    active_tab = page_dashboard()
#     ref, apikey, data = read_output()
    
    if active_tab == "Main":
        tabMain.page()
    elif active_tab == "챔피언기록":
        tab01.page()
    elif active_tab == "유저기록":
        tab02.page()
    elif active_tab == "인게임정보":
        tab03.page()
    elif active_tab == "챔피언통계":
        tab04.page()
    elif active_tab == "랭킹":
        tab05.page()
