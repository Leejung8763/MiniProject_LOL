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
    π **μΆκ°μ¬ν­**
    <p style="font-family:Courier; color:Red;">
    1. νμ΄λΈ μ¬μ΄μ¦ λ° λ§ν¬ κΈ°λ₯<br>
    2. νμ΄λΈ λ΄ νΉμ  μ»¬λΌμ μ΄λ―Έμ§ν
    <hr>
    """, unsafe_allow_html=True)
    
    ##############
    # search bar #
    ##############
    cols = st.columns(4)
    ref, apikey, data = dataRead.read_output()
    
    with cols[0]:
        userName = st.text_input("μνμ¬λͺμ μλ ₯νμμ€.")
    
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
                ## **{"μλ‘λ­ν¬" if data_spectator.gameQueueConfigId[0]==420 else "μμ λ­ν¬"}**
                """)
            data_spectator = pd.merge(data_spectator, data_stats, how="left", on=["summonerId", "championId"])
            # change code to name
            ## champion
            data_spectator = data_spectator.astype({"championId":"string"}) # output ν¬λ§· μ νλ©΄ μ­μ 
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
                ### <span style="color:{"blue" if team==100 else "red"}">{"λΈλ£¨ν" if team==100 else "λ λν"} </span>
                """, unsafe_allow_html=True)
                spectatorTeam = data_spectator.query("teamId==@team")
                displayColEn = ["summonerName", "tier", "rank", "wins", "losses", "championId", "champCntTot", "win", "kills", "deaths", "assists", "spell1Id", "spell2Id", "perkStyle", "perkSubStyle", "perk0", "perk1", "perk2", "perk3", "perk4", "perk5", "statPerk0", "statPerk1", "statPerk2"]
                displayColKr = ["μνμ¬", "ν°μ΄", "λ­ν¬", "μΉ", "ν¨", "μ±νΌμΈ", "νλ μ΄", "μΉλ₯ ", "μ²μΉ", "μ¬λ§", "λμ", "μ€ν (D)", "μ€ν (F)", "λ©μΈλ£¬", "λ³΄μ‘°λ£¬", "λ©μΈλ£¬#1", "λ©μΈλ£¬#2", "λ©μΈλ£¬#3", "λ³΄μ‘°λ£¬#1", "λ³΄μ‘°λ£¬#2", "λ³΄μ‘°λ£¬#3", "λ£¬ννΈ#1", "λ£¬ννΈ#2", "λ£¬ννΈ#3"]
                spectatorTeam = spectatorTeam.loc[:,displayColEn]
                spectatorTeam.columns = displayColKr
                # μμ ν΄μΌνλ λΆλΆ
                gb = GridOptionsBuilder.from_dataframe(spectatorTeam)
                gb.configure_grid_options(autoHeight=True)
                gridOptions = gb.build()
                data = AgGrid(
                    spectatorTeam.round(2),
                    height = 200, # dataframe λμ΄ μ‘°μ 
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