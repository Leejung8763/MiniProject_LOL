import os, re
os.sys.path.append("/home/lj/git/MiniProject_LOL/")

import streamlit as st
import pandas as pd
import numpy as np
import dataRead
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
import lolApi, lolDataPull

def page():
    ############
    # fix list #
    ############
    st.markdown("""
    😐 **추가사항**
    <p style="font-family:Courier; color:Red;">
    1. 테이블 사이즈 및 링크 기능<br>
    2. 테이블 배치<br>
    <hr>
    """,unsafe_allow_html=True)
    
    st.button("Refresh")
    #############
    # load data #
    #############
    ref, apikey, data = dataRead.read_output()
    summonerList = lolDataPull.summonerPull(apikey)
    summonerList = summonerList.astype({key:value for key, value in ref.formatJson["inputDtype"]["summonerListDtype"].items() if key in summonerList.keys()}, )
    summonerList["Ranking"] = np.arange(len(summonerList))+1
    summonerList["playCnt"] = summonerList["wins"] + summonerList["losses"]
    summonerList["winRate"] = summonerList["wins"] / summonerList["playCnt"] * 100
    
    ######################
    # display user stats #
    ######################
    data["userStatsTot"]["championId"] = data["userStatsTot"]["championId"].astype(str)
    def drawTop(i):
        summonerId = summonerList.summonerId[i]
        
        # change code to name
        displayColEn = ["championId", "champCnt" ,"win", "kills", "deaths", "assists"]
        displayColKr = ["챔피언", "플레이" ,"승리", "처치", "사망", "도움"]
        data_ = pd.merge(ref.champInfoDto[["key", "name"]], data["userStatsTot"], left_on=["key"], right_on=["championId"], how="right")
        data_["championId"] = data_["name"]
        
        data_ = (data_.loc[data_.summonerId==summonerId, displayColEn]
                 .sort_values("champCnt", ascending=False)
                 .head(3)
                 .rename(dict(zip(displayColEn, displayColKr)), axis=1))
                
        gb = GridOptionsBuilder.from_dataframe(data_)
        gb.configure_grid_options(autoHeight=True)
        gridOptions = gb.build()
        AgGrid(
            data_.round(2),
            height = 120, # dataframe 높이 조절
            gridOptions=gridOptions,
            allow_unsafe_jscode=True
        )
    cols00 = st.columns([1,5,2,10,1,5])
    cols00[2].image("https://media0.giphy.com/media/5zHNSgczzpoY9JjvHE/200w.webp?cid=ecf05e47a80g54grwmw30fg1lhqlhml5jr20e2d8sec7hecs&rid=200w.webp&ct=s")
    with cols00[3]:
        drawTop(0)  
    cols00 = st.columns([1,5,1,5])
    cols00[0].image("https://media2.giphy.com/media/nkIixSLls8gB4FmwDZ/200.webp?cid=ecf05e47muowhvw6cn0e67fndsqknn4lyp6l4vfn72v7ukfw&rid=200.webp&ct=s")
    with cols00[1]:
        drawTop(1)
    cols00[2].image("https://media1.giphy.com/media/3abMpkigbPSspgjFad/200.webp?cid=ecf05e475nje4z3tysr0zyip27z9f6cbr6i36bydztpl866j&rid=200.webp&ct=s")
    with cols00[3]:
        drawTop(2)
    
    # display user stats
    rows02 = st.columns([1,1.5,1])
    with rows02[1]:
        displayColEn = ["Ranking", "summonerName", "tier", "leaguePoints", "winRate", "playCnt"]
        displayColKr = ["랭킹", "소환사", "티어", "리그 포인트", "승률", "플레이"]
        summonerList.rename(dict(zip(displayColEn, displayColKr)), axis=1, inplace=True)
        gb = GridOptionsBuilder.from_dataframe(summonerList.loc[:, displayColKr])
        gb.configure_pagination(paginationPageSize=50) # 한 페이지에 출력해주는 갯수
        gb.configure_grid_options(autoHeight=True)
        gridOptions = gb.build()
        data = AgGrid(
            summonerList.loc[3:, displayColKr].round(2),
            height = 600, # dataframe 높이 조절
            gridOptions=gridOptions,
            allow_unsafe_jscode=True
        )
