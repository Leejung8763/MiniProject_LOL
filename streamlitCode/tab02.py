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
    1. ์ฑํผ์ธ ๋ช, ์ํ์ฌ ๋ช ์๋ ฅ์ ํ์ด์ง ๋ณ๊ฒฝ<br>
    2. ํ์ด๋ธ ์ฌ์ด์ฆ ๋ฐ ๋งํฌ ๊ธฐ๋ฅ<br>
    3. ์ด๋ฏธ์ง ์ ๋ ฌ ๋ฐ ๋งํฌ ๊ธฐ๋ฅ
    <hr>
    """,unsafe_allow_html=True)
    
    ##############
    # search bar #
    ##############
    cols = st.columns(4)
    ref, apikey, data = dataRead.read_output()
    
    with cols[0]:
        userName = st.text_input("์ํ์ฌ๋ช์ ์๋ ฅํ์์ค.","์ชผ๋ ์ด๋ค๋ง๋กํ์")
        data_ = pd.read_csv("/data1/lolData/cgLeague/sampleOutput/userStatsLane.csv")
    
    ######################
    # display user stats #
    ######################
    if userName:
        # user name
        userInfo = lolApi.summonerId(apikey, summonerName=userName)
        # get user accountId 
        userAccount = userInfo["accountId"][0]
        # select columns
        displayColEn = ["laneEdit", "championId", "champCnt", "win", "kills", "deaths", "assists", "totalDamageDealt", "totalDamageDealtToChampions", "totalDamageTaken", "goldEarned", "totalMinionsKilled", "firstBloodKill", "firstTowerKill", "visionScore"]
        displayColKr = ["๋ผ์ธ", "์ฑํผ์ธ", "ํ๋ ์ด", "์น๋ฅ ", "์ฒ์น", "์ฌ๋ง" ,"๋์", "์ ์๊ฒ ๊ฐํ ์ด ํผํด๋", "์ฑํผ์ธ์๊ฒ ๊ฐํ ์ด ํผํด๋", "์์ ์ด ํผํด๋", "๊ณจ๋(ํ๊ท )", "cs(ํ๊ท )", "์ ์ทจ ํ๋ฅ ", "ํ์ ์ ์ทจ ํ๋ฅ ", "์์ผ ์ ์"]
        data_ = data_.loc[data_.accountId==userAccount, displayColEn]
        # change code to name
        data_ = data_.astype({"championId":"string"}) # output ํฌ๋งท ์ ํ๋ฉด ์ญ์ 
        data_ = pd.merge(ref.champInfoDto[["key", "id"]], data_, left_on=["key"], right_on=["championId"], how="right")
        data_["championId"] = data_["id"]
        data_.drop(["key", "id"], axis=1, inplace=True)
        data_.sort_values(["champCnt"], ascending=False, inplace=True)
        data_.reset_index(drop=True, inplace=True)
        data_.columns = displayColKr
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