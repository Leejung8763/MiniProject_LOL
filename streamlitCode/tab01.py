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
    ref, apikey, data = dataRead.read_output()
    st.sidebar.header("Record")
    st.sidebar.subheader("์ํ๋ ์ฑํผ์ธ๊ณผ ๋ผ์ธ์ ์ ํํ์ธ์.")
    ref, apikey, data = dataRead.read_output()
    
    choiceChamp = st.sidebar.selectbox("champion", ref.champInfoDto.name)
    choiceLane = st.sidebar.selectbox("Line", ["TOP","JUNGLE","MIDDLE","BOTTOM","SUPPORT"])
    choiceChamp = ref.champInfoDto.query("name==@choiceChamp").key.tolist()
    choiceChampStatsDf = data["champStats"].query("championId==@choiceChamp")
    choicePrdStatsDf = data["prdStats"].query("championId==@choiceChamp")
    runeStatsDf = data["runeStats"].query("championId==@choiceChamp and laneEdit==@choiceLane")
    spellStatsDf = data["spellStats"].query("championId==@choiceChamp and laneEdit==@choiceLane")   
    skillStatsDf = data["skillStats"].query("championId==@choiceChamp and laneEdit==@choiceLane")
    
    # ๊ตฌ์ญ์ 3๋ถํ 
    cols = st.columns([2,1])
    #############
    # ์ฃผ์ ์งํ #
    #############
    with cols[0]:
        st.title("์ฃผ์ ์งํ")

        # ์ฑํผ์ธ rune ์กฐํฉ
        st.subheader("์ถ์ฒ Rune")
        runeCntMed = runeStatsDf.runeCnt.median()
        runeCntDf = runeStatsDf[["perkPrimaryStyle","perk0","perk1","perk2","perk3","perkSubStyle","perk4","perk5","win","runeCnt","runePropTot"]].copy()
        runeCntDf.columns = ["ํต์ฌ๋ฃฌ","ํต์ฌ ์ผ๋ฐ๋ฃฌ#1","ํต์ฌ ์ผ๋ฐ๋ฃฌ#2","ํต์ฌ ์ผ๋ฐ๋ฃฌ#3","ํต์ฌ ์ผ๋ฐ๋ฃฌ#4","๋ณด์กฐ๋ฃฌ","ํต์ฌ ๋ณด์กฐ๋ฃฌ#1","ํต์ฌ ์ผ๋ฐ๋ฃฌ#2","์น๋ฅ ","๋น๋","ํฝ๋ฅ "]

        st.write("ํฝ๋ฅ  ๊ธฐ์ค")
        runeCntDfTmp = runeCntDf.sort_values("๋น๋",ascending=False).head(1).round(2).copy()
        gb = GridOptionsBuilder.from_dataframe(runeCntDfTmp)
        gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gridOptions = gb.build()
        AgGrid(runeCntDfTmp,
               height="",
               gridOptions=gridOptions)
        st.write("์น๋ฅ  ๊ธฐ์ค")
        runeCntDfTmp = runeCntDf.query("๋น๋>=@runeCntMed").sort_values("์น๋ฅ ",ascending=False).head(1).round(2).copy()
        gb = GridOptionsBuilder.from_dataframe(runeCntDfTmp)
        gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gridOptions = gb.build()
        AgGrid(runeCntDfTmp,
               height="",
               gridOptions=gridOptions)

        # ์ฑํผ์ธ spell ์กฐํฉ
        st.subheader("์ถ์ฒ Spell")
        spellCntMed = spellStatsDf.spellCnt.median()
        spellCntDf = spellStatsDf[["spell1Id","spell2Id","win","spellCnt","spellPropTot"]].copy()
        spellCntDf.columns = ["Spell#1","Spell#2","์น๋ฅ ","๋น๋","ํฝ๋ฅ "]

        st.write("ํฝ๋ฅ  ๊ธฐ์ค")
        spellCntDfTmp = spellCntDf.sort_values("๋น๋",ascending=False).head(1).round(2).copy()
        gb = GridOptionsBuilder.from_dataframe(spellCntDfTmp)
        gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gridOptions = gb.build()
        AgGrid(spellCntDfTmp,
               height="",
               gridOptions=gridOptions)
        
        st.write("์น๋ฅ  ๊ธฐ์ค")
        spellCntDfTmp = spellCntDf.query("๋น๋>=@spellCntMed").sort_values("์น๋ฅ ",ascending=False).head(1).round(2).copy()
        gb = GridOptionsBuilder.from_dataframe(spellCntDf)
        gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gridOptions = gb.build()
        AgGrid(spellCntDfTmp,
               height="",
               gridOptions=gridOptions)
        
        # ์ฑํผ์ธ skill ๋น๋
        st.subheader("์ถ์ฒ Skill Build")
        skillCntMed = skillStatsDf.skillCnt.median()
        skillCntDf = skillStatsDf[["num0","num1","num2","num3","num4","num5","num6","num7","num8","num9","num10","num11","num12","num13","num14","win","skillCnt","skillPropTot"]].copy()
        skillCntDf.columns = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","์น๋ฅ ","๋น๋","ํฝ๋ฅ "]
        
        st.write("ํฝ๋ฅ  ๊ธฐ์ค")
        skillWinDf = (
            skillCntDf.replace(["1","2","3","4"], ['Q','W','E','R'])
            .sort_values("๋น๋",ascending=False, ignore_index=True)
            .head(1)
        ).copy()
        skillIndex = pd.DataFrame({'skill' : ['Q','W','E','R']})
        for i in range(15):
            skillIndex = pd.merge(skillIndex, skillWinDf.iloc[:,i], left_on="skill", right_on=f"{i}", how="left")
        skillIndex.fillna("", inplace=True)
        skillIndex.set_index("skill", inplace=True)
        st.write(f"ํฝ: {int(skillWinDf.๋น๋[0])}({skillWinDf.ํฝ๋ฅ [0]*100:.2f}%) / ์น๋ฅ : {skillWinDf.์น๋ฅ [0]*100:.2f}%")
        st.dataframe(skillIndex.style.applymap(skill_paint))
                
        st.write("์น๋ฅ  ๊ธฐ์ค")
        skillWinDf = (
            skillCntDf.replace(["1","2","3","4"], ['Q','W','E','R'])
            .query("๋น๋>@skillCntMed")
            .sort_values("์น๋ฅ ",ascending=False, ignore_index=True)
            .head(1)
        ).copy()
        skillIndex = pd.DataFrame({'skill' : ['Q','W','E','R']})
        for i in range(15):
            skillIndex = pd.merge(skillIndex, skillWinDf.iloc[:,i], left_on="skill", right_on=f"{i}", how="left")
        skillIndex.fillna("", inplace=True)
        skillIndex.set_index("skill", inplace=True)
        st.write(f"ํฝ: {int(skillWinDf.๋น๋[0])}({skillWinDf.ํฝ๋ฅ [0]*100:.2f}%) / ์น๋ฅ : {skillWinDf.์น๋ฅ [0]*100:.2f}%")
        st.dataframe(skillIndex.style.applymap(skill_paint))        
        
    #############
    # ๋ณด์กฐ ์งํ #
    #############
    with cols[1]:
        st.title("๋ณด์กฐ์งํ")

        # ์ฑํผ์ธ์ lane ํฝ๋ฅ  pie chart ๊ทธ๋ฆฌ๊ธฐ   
        st.subheader("์ฑํผ์ธ์ Lane ํฝ๋ฅ ")
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

        # ์ฑํผ์ธ lane๋ณ ํฝ๋ฅ  bar chart ๊ทธ๋ฆฌ๊ธฐ   
        st.subheader("Lane ๋ณ ์ฑํผ์ธ ํฝ๋ฅ ")
        barChartPickDf = choiceChampStatsDf.query("championId==@choiceChamp")[["laneEdit", "lanePropTot"]].copy()
        barChartPickDf = (
            barChartPickDf
            .astype({"laneEdit":str,"lanePropTot":float})
            .set_index("laneEdit")
            .rename(columns={"lanePropTot":""})
            .fillna(0)*100
        )
        st.bar_chart(barChartPickDf)

        # ์ฑํผ์ธ lane๋ณ ์น๋ฅ  bar chart ๊ทธ๋ฆฌ๊ธฐ   
        st.subheader("Lane ๋ณ ์ฑํผ์ธ ์น๋ฅ ")
        barChartWinDf = choiceChampStatsDf.query("championId==@choiceChamp")[["laneEdit", "win"]].copy()
        barChartWinDf = (
            barChartWinDf
            .astype({"laneEdit":str,"win":float})
            .set_index("laneEdit")
            .rename(columns={"win":""})
            .fillna(0)*100
        )
        st.bar_chart(barChartWinDf)

        # ์ ํํ ์ฑํผ์ธ์ ๊ฒ์ ๊ธธ์ด๋ณ ์น๋ฅ 
        st.subheader("์ฑํผ์ธ ๊ฒ์ ๊ธธ์ด๋ณ ์น๋ฅ ")
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