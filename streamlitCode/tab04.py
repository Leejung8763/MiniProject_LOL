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
    😐 **추가사항**
    <p style="font-family:Courier; color:Red;">
    1. 테이블 사이즈 및 링크 기능<br>
    2. 테이블 내 특정 컬럼은 이미지화
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
    displayColKr = ["라인", "챔피언", "플레이", "승률", "처치", "사망" ,"도움", "적에게 가한 총 피해량", "챔피언에게 가한 총 피해량", "입은 총 피해량", "골드(평균)", "cs(평균)", "선취 확률", "타워 선취 확률", "시야 점수"]
    
    # chaange code to name
    data["tierStats"] = data["tierStats"].astype({"championId":"string"}) # data 포맷 정하면 삭제
    data["tierStats"] = pd.merge(ref.champInfoDto[["key", "name"]], data["tierStats"], left_on=["key"], right_on=["championId"], how="right")
    data["tierStats"]["championId"] = data["tierStats"]["name"]
    data_ = (data["tierStats"].query("tier==@tier and laneEdit==@lane")
             .loc[:, displayColEn]
             .sort_values("champCnt", ascending=False)
             .rename(dict(zip(displayColEn, displayColKr)), axis=1))
    # display user stats
    gb = GridOptionsBuilder.from_dataframe(data_)
    gb.configure_pagination(paginationPageSize=20) # 한 페이지에 출력해주는 갯수
    gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
    gridOptions = gb.build()
    data = AgGrid(
        data_.round(2),
        height = "", # dataframe 높이 조절
        gridOptions=gridOptions,
        allow_unsafe_jscode=True
    )