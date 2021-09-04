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
    
    ##############
    # search bar #
    ##############
    cols = st.columns(4)
    ref, apikey, data = dataRead.read_output()
    
    with cols[0]:
        userName = st.text_input("소환사명을 입력하시오.")
    
    if userName:
        try:
            #######################
            # search current game #
            #######################
            userInfo = lolApi.summonerId(apikey, summonerName=userName)
            data_spectator = lolApi.spectator(apikey, userInfo["id"][0])
            data_stats = pd.read_csv("/data1/lolData/cgLeague/sampleOutput/userStatsTot.csv")
            data_summoner = pd.read_feather(f"/data1/lolData/cgLeague/API_ftr/210830/summonerList_{210830}.ftr")
            data_stats = pd.merge(data_summoner.loc[:,["summonerId","tier","rank","wins","losses"]], data_stats.loc[:,["summonerId", "championId", "champCntTot", "win", "kills", "deaths", "assists"]], how="left")
            displayColEn = ["teamId", "spell1Id", "spell2Id", "championId", "summonerName", "summonerId", "perkStyle", "perkSubStyle", "gameQueueConfigId", "gameStartTime", "perk0", "perk1", "perk2", "perk3", "perk4", "perk5", "statPerk0", "statPerk1", "statPerk2"]

            ######################
            # display user stats #
            ######################
            cols = st.columns(4)
            with cols[0]:
                st.markdown(f"""
                ## **{"솔로랭크" if data_spectator.gameQueueConfigId[0]==420 else "자유랭크"}**
                """)
            data_spectator = pd.merge(data_spectator, data_stats, how="left", on=["summonerId", "championId"])
            # change code to name
            ## champion
            data_spectator = data_spectator.astype({"championId":"string"}) # output 포맷 정하면 삭제
            data_spectator = pd.merge(ref.champInfoDto[["key", "name"]], data_spectator, left_on=["key"], right_on=["championId"], how="right")
            data_spectator["championId"] = data_spectator["name"]
            data_spectator.drop(["key","name"], axis=1, inplace=True)
            ## spell
            for spellName in [col for col in data_spectator.columns if "spell" in col]:
                data_spectator[spellName] = data_spectator[spellName].astype(str)
                data_spectator = pd.merge(ref.spellInfoDto[["key", "name"]], data_spectator, left_on=["key"], right_on=[spellName], how="right")
                data_spectator[spellName] = data_spectator["name"]
                data_spectator.drop(["key","name"], axis=1, inplace=True)
            ## rune
            for runeName in [col for col in data_spectator.columns if "perk" in col or "Perk" in col]:
                data_spectator[runeName] = data_spectator[runeName].astype(str)
                data_spectator = pd.merge(ref.runeInfoDto[["id", "name"]], data_spectator, left_on=["id"], right_on=[runeName], how="right")
                data_spectator[runeName] = data_spectator["name"]
                data_spectator.drop(["id","name"], axis=1, inplace=True)


            for team in [100,200]:
                st.markdown(f"""
                ### <span style="color:{"blue" if team==100 else "red"}">{"블루팀" if team==100 else "레드팀"} </span>
                """, unsafe_allow_html=True)
                spectatorTeam = data_spectator.query("teamId==@team")
                displayColEn = ["summonerName", "tier", "rank", "wins", "losses", "championId", "champCntTot", "win", "kills", "deaths", "assists", "spell1Id", "spell2Id", "perkStyle", "perkSubStyle", "perk0", "perk1", "perk2", "perk3", "perk4", "perk5", "statPerk0", "statPerk1", "statPerk2"]
                displayColKr = ["소환사", "티어", "랭크", "승", "패", "챔피언", "플레이", "승률", "처치", "사망", "도움", "스펠(D)", "스펠(F)", "메인룬", "보조룬", "메인룬#1", "메인룬#2", "메인룬#3", "보조룬#1", "보조룬#2", "보조룬#3", "룬파편#1", "룬파편#2", "룬파편#3"]
                spectatorTeam = spectatorTeam.loc[:,displayColEn]
                spectatorTeam.columns = displayColKr
                # 수정해야하는 부분
                gb = GridOptionsBuilder.from_dataframe(spectatorTeam)
                gb.configure_grid_options(autoHeight=True)
                gridOptions = gb.build()
                data = AgGrid(
                    spectatorTeam.round(2),
                    height = 200, # dataframe 높이 조절
                    gridOptions=gridOptions,
                    allow_unsafe_jscode=True
                )
        except:
            html_code=f"""
            <a href="http://192.168.150.103:8990/?tab=%EC%9D%B8%EA%B2%8C%EC%9E%84%EC%A0%95%EB%B3%B4">
            <div style="text-align : center;">
            <img src="https://media1.giphy.com/media/14uQ3cOFteDaU/giphy.gif?cid=ecf05e477wanfzjlohw9cslqir12vr9s36rpqjshl8e2fm5y&rid=giphy.gif&ct=g" width="40%" height="30%"/>
            </div>
            </a>"""
            st.markdown(html_code, unsafe_allow_html=True)