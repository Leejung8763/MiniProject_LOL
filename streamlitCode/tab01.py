import requests, json, urllib, os, re, time, base64
os.sys.path.append("/home/lj/git/MiniProject_LOL/")

import streamlit as st
import pandas as pd
import numpy as np
import dataRead
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

def page():
    st.sidebar.header("Record")
    st.sidebar.write("원하는 챔피언과 라인을 선택하세요.")

    add_selectbox = st.sidebar.selectbox('champion', champInfoDto[champInfoDto['key'].isin(list(Chamlist))]['id'])
    add_selectbox2 = st.sidebar.selectbox('Line', Linelist)

    st.write("This page was created as a hacky demo of tabs")

    if (add_selectbox == '858') & (add_selectbox2 == 'top'):
        st.slider(
            "champion 858 - top",
            min_value=0,
            max_value=100,
            value=50, )
