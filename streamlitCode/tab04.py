import os, re
os.sys.path.append("/home/lj/git/MiniProject_LOL/")

import streamlit as st
import pandas as pd
import numpy as np
import dataRead
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
import lolApi

def page():
    ############
    # fix list #
    ############
    st.markdown("""
    ๐ **์ถ๊ฐ์ฌํญ**
    <p style="font-family:Courier; color:Red;">
    1. ํ์ด๋ธ ์ฌ์ด์ฆ ๋ฐ ๋งํฌ ๊ธฐ๋ฅ<br>
    2. ํ์ด๋ธ ๋ด ํน์  ์ปฌ๋ผ์ ์ด๋ฏธ์งํ
    <hr>
    """, unsafe_allow_html=True)
    
    ######################
    # display side stats #
    ######################
    ref, apikey, data = dataRead.read_output()
    
    # champ stats by tier
    tier = st.sidebar.selectbox("Tier", ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"])
    lane = st.sidebar.selectbox("Lane", ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"])
    
    ######################
    # disply champ stats #
    ######################
    displayColEn = ["laneEdit", "championId", "champCnt", "win", "kills", "deaths", "assists", "totalDamageDealt", "totalDamageDealtToChampions", "totalDamageTaken", "goldEarned", "totalMinionsKilled", "firstBloodKill", "firstTowerKill", "visionScore"]
    displayColKr = ["๋ผ์ธ", "์ฑํผ์ธ", "ํ๋ ์ด", "์น๋ฅ ", "์ฒ์น", "์ฌ๋ง" ,"๋์", "์ ์๊ฒ ๊ฐํ ์ด ํผํด๋", "์ฑํผ์ธ์๊ฒ ๊ฐํ ์ด ํผํด๋", "์์ ์ด ํผํด๋", "๊ณจ๋(ํ๊ท )", "cs(ํ๊ท )", "์ ์ทจ ํ๋ฅ ", "ํ์ ์ ์ทจ ํ๋ฅ ", "์์ผ ์ ์"]
    
    # chaange code to name
    data["tierStats"] = data["tierStats"].astype({"championId":"string"}) # data ํฌ๋งท ์ ํ๋ฉด ์ญ์ 
    data["tierStats"] = pd.merge(ref.champInfoDto[["key", "name"]], data["tierStats"], left_on=["key"], right_on=["championId"], how="right")
    data["tierStats"]["championId"] = data["tierStats"]["name"]
    data_ = (data["tierStats"].query("tier==@tier and laneEdit==@lane")
             .loc[:, displayColEn]
             .sort_values("champCnt", ascending=False)
             .rename(dict(zip(displayColEn, displayColKr)), axis=1))
    # display user stats
    gb = GridOptionsBuilder.from_dataframe(data_)
    gb.configure_pagination(paginationPageSize=20) # ํ ํ์ด์ง์ ์ถ๋ ฅํด์ฃผ๋ ๊ฐฏ์
    gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
    gridOptions = gb.build()
    data = AgGrid(
        data_.round(2),
        height = "", # dataframe ๋์ด ์กฐ์ 
        gridOptions=gridOptions,
        allow_unsafe_jscode=True
    )