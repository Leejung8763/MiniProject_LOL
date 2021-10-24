import requests, json, urllib, os, re, time, base64
os.sys.path.append("/home/lj/git/MiniProject_LOL/")

import streamlit as st
import pandas as pd
import numpy as np
import dataRead
import matplotlib.pyplot as plt
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

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
    ref, apikey, data = dataRead.read_output()
    st.sidebar.header("Record")
    st.sidebar.subheader("원하는 챔피언과 라인을 선택하세요.")
    ref, apikey, data = dataRead.read_output()
    
    choiceChamp = st.sidebar.selectbox("champion", ref.champInfoDto.name)
    choiceLane = st.sidebar.selectbox("Line", ["TOP","JUNGLE","MIDDLE","BOTTOM","SUPPORT"])
    choiceChamp = ref.champInfoDto.query("name==@choiceChamp").key.tolist()
    choiceChampStatsDf = data["champStats"].query("championId==@choiceChamp")
    choicePrdStatsDf = data["prdStats"].query("championId==@choiceChamp")
    runeStatsDf = data["runeStats"].query("championId==@choiceChamp and laneEdit==@choiceLane")
    spellStatsDf = data["spellStats"].query("championId==@choiceChamp and laneEdit==@choiceLane")   
    skillStatsDf = data["skillStats"].query("championId==@choiceChamp and laneEdit==@choiceLane")
    
    # 구역을 3분할
    cols = st.columns([2,1])
    #############
    # 주요 지표 #
    #############
    with cols[0]:
        st.title("주요 지표")

        # 챔피언 rune 조합
        st.subheader("추천 Rune")
        runeCntMed = runeStatsDf.runeCnt.median()
        runeCntDf = runeStatsDf[["perkPrimaryStyle","perk0","perk1","perk2","perk3","perkSubStyle","perk4","perk5","win","runeCnt","runePropTot"]].copy()
        runeCntDf.columns = ["핵심룬","핵심 일반룬#1","핵심 일반룬#2","핵심 일반룬#3","핵심 일반룬#4","보조룬","핵심 보조룬#1","핵심 일반룬#2","승률","빈도","픽률"]

        st.write("픽률 기준")
        runeCntDfTmp = runeCntDf.sort_values("빈도",ascending=False).head(1).round(2).copy()
        gb = GridOptionsBuilder.from_dataframe(runeCntDfTmp)
        gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gridOptions = gb.build()
        AgGrid(runeCntDfTmp,
               height="",
               gridOptions=gridOptions)
        st.write("승률 기준")
        runeCntDfTmp = runeCntDf.query("빈도>=@runeCntMed").sort_values("승률",ascending=False).head(1).round(2).copy()
        gb = GridOptionsBuilder.from_dataframe(runeCntDfTmp)
        gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gridOptions = gb.build()
        AgGrid(runeCntDfTmp,
               height="",
               gridOptions=gridOptions)

        # 챔피언 spell 조합
        st.subheader("추천 Spell")
        spellCntMed = spellStatsDf.spellCnt.median()
        spellCntDf = spellStatsDf[["spell1Id","spell2Id","win","spellCnt","spellPropTot"]].copy()
        spellCntDf.columns = ["Spell#1","Spell#2","승률","빈도","픽률"]

        st.write("픽률 기준")
        spellCntDfTmp = spellCntDf.sort_values("빈도",ascending=False).head(1).round(2).copy()
        gb = GridOptionsBuilder.from_dataframe(spellCntDfTmp)
        gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gridOptions = gb.build()
        AgGrid(spellCntDfTmp,
               height="",
               gridOptions=gridOptions)
        
        st.write("승률 기준")
        spellCntDfTmp = spellCntDf.query("빈도>=@spellCntMed").sort_values("승률",ascending=False).head(1).round(2).copy()
        gb = GridOptionsBuilder.from_dataframe(spellCntDf)
        gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gridOptions = gb.build()
        AgGrid(spellCntDfTmp,
               height="",
               gridOptions=gridOptions)
        
        # 챔피언 skill 빌드
        st.subheader("추천 Skill Build")
        skillCntMed = skillStatsDf.skillCnt.median()
        skillCntDf = skillStatsDf[["num0","num1","num2","num3","num4","num5","num6","num7","num8","num9","num10","num11","num12","num13","num14","win","skillCnt","skillPropTot"]].copy()
        skillCntDf.columns = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","승률","빈도","픽률"]
        
        st.write("픽률 기준")
        skillWinDf = (
            skillCntDf.replace(["1","2","3","4"], ['Q','W','E','R'])
            .sort_values("빈도",ascending=False, ignore_index=True)
            .head(1)
        ).copy()
        skillIndex = pd.DataFrame({'skill' : ['Q','W','E','R']})
        for i in range(15):
            skillIndex = pd.merge(skillIndex, skillWinDf.iloc[:,i], left_on="skill", right_on=f"{i}", how="left")
        skillIndex.fillna("", inplace=True)
        skillIndex.set_index("skill", inplace=True)
        st.write(f"픽: {int(skillWinDf.빈도[0])}({skillWinDf.픽률[0]*100:.2f}%) / 승률: {skillWinDf.승률[0]*100:.2f}%")
        st.dataframe(skillIndex.style.applymap(skill_paint))
                
        st.write("승률 기준")
        skillWinDf = (
            skillCntDf.replace(["1","2","3","4"], ['Q','W','E','R'])
            .query("빈도>@skillCntMed")
            .sort_values("승률",ascending=False, ignore_index=True)
            .head(1)
        ).copy()
        skillIndex = pd.DataFrame({'skill' : ['Q','W','E','R']})
        for i in range(15):
            skillIndex = pd.merge(skillIndex, skillWinDf.iloc[:,i], left_on="skill", right_on=f"{i}", how="left")
        skillIndex.fillna("", inplace=True)
        skillIndex.set_index("skill", inplace=True)
        st.write(f"픽: {int(skillWinDf.빈도[0])}({skillWinDf.픽률[0]*100:.2f}%) / 승률: {skillWinDf.승률[0]*100:.2f}%")
        st.dataframe(skillIndex.style.applymap(skill_paint))        
        
    #############
    # 보조 지표 #
    #############
    with cols[1]:
        st.title("보조지표")

        # 챔피언의 lane 픽률 pie chart 그리기   
        st.subheader("챔피언의 Lane 픽률")
        barChartPickDf = choiceChampStatsDf.query("championId==@choiceChamp")[["laneEdit", "champCnt"]].copy()
        barChartPickDf = (
            barChartPickDf
            .astype({"laneEdit":str,"champCnt":float})
            .set_index("laneEdit")
            .dropna()*100
        )
        fig1, ax1 = plt.subplots()
        ax1.pie(barChartPickDf.champCnt, labels=barChartPickDf.index.tolist(), autopct='%.1f%%', shadow=True)
        st.pyplot(fig1)

        # 챔피언 lane별 픽률 bar chart 그리기   
        st.subheader("Lane 별 챔피언 픽률")
        barChartPickDf = choiceChampStatsDf.query("championId==@choiceChamp")[["laneEdit", "lanePropTot"]].copy()
        barChartPickDf = (
            barChartPickDf
            .astype({"laneEdit":str,"lanePropTot":float})
            .set_index("laneEdit")
            .rename(columns={"lanePropTot":""})
            .fillna(0)*100
        )
        st.bar_chart(barChartPickDf)

        # 챔피언 lane별 승률 bar chart 그리기   
        st.subheader("Lane 별 챔피언 승률")
        barChartWinDf = choiceChampStatsDf.query("championId==@choiceChamp")[["laneEdit", "win"]].copy()
        barChartWinDf = (
            barChartWinDf
            .astype({"laneEdit":str,"win":float})
            .set_index("laneEdit")
            .rename(columns={"win":""})
            .fillna(0)*100
        )
        st.bar_chart(barChartWinDf)

        # 선택한 챔피언의 게임 길이별 승률
        st.subheader("챔피언 게임 길이별 승률")
        lineChartWinDf = pd.DataFrame()
        for lane in ["TOP","JUNGLE","MIDDLE","BOTTOM","SUPPORT"]:
            tmp = (
                choicePrdStatsDf
                .query(f"laneEdit=='{lane}'")
                .loc[:,["timeClass","win"]]
                .set_index("timeClass")
                .rename(columns={"win":f"{lane}"})
                *100
            )
            lineChartWinDf = pd.concat([lineChartWinDf, tmp], axis=1).fillna(0)
        st.line_chart(lineChartWinDf)

# skill build background color
def skill_paint(df):

    Q = 'background-color: yellow;'
    W = 'background-color: green;'
    E = 'background-color: skyblue;'
    R = 'background-color: pink;'
    default = ''
    
    if type(df) in [object, str, int, float] :
        if df == "Q":
            return Q
        elif df == "W" :
            return W
        elif df == "E" :
            return E
        elif df == "R" :
            return R

    return default