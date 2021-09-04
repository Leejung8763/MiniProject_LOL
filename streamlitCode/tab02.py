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
    1. 챔피언 명, 소환사 명 입력시 페이지 변경<br>
    2. 테이블 사이즈 및 링크 기능<br>
    3. 이미지 정렬 및 링크 기능
    <hr>
    """,unsafe_allow_html=True)
    
    ##############
    # search bar #
    ##############
    cols = st.columns(4)
    ref, apikey, data = dataRead.read_output()
    
    with cols[0]:
        userName = st.text_input("소환사명을 입력하시오.","쪼렙이다말로하자")
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
        displayColKr = ["라인", "챔피언", "플레이", "승률", "처치", "사망" ,"도움", "적에게 가한 총 피해량", "챔피언에게 가한 총 피해량", "입은 총 피해량", "골드(평균)", "cs(평균)", "선취 확률", "타워 선취 확률", "시야 점수"]
        data_ = data_.loc[data_.accountId==userAccount, displayColEn]
        # change code to name
        data_ = data_.astype({"championId":"string"}) # output 포맷 정하면 삭제
        data_ = pd.merge(ref.champInfoDto[["key", "id"]], data_, left_on=["key"], right_on=["championId"], how="right")
        data_["championId"] = data_["id"]
        data_.drop(["key", "id"], axis=1, inplace=True)
        data_.sort_values(["champCnt"], ascending=False, inplace=True)
        data_.reset_index(drop=True, inplace=True)
        data_.columns = displayColKr
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