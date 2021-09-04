import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
import pandas as pd
import numpy as np
import requests, json, urllib
import lolApi, lolRef, lolDataPull

st.set_page_config(layout="wide", page_icon="https://lh3.googleusercontent.com/WebglHOYlW-2P7ADP9oUSSrgy12PHyAE6GP_jmJkQOZZ1XH7Pa_7216EK2qS7iJFvncqOaDjg40BrYdzPbB9qNwn", page_title="LoL_Dashboard")

## Title
st.title('LoL Data Analysis')
st.text("LOL 데이터 시각화 서비스 개발 - LJ, Elina, Jamie")

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)

# load Ref
ref = lolRef.Ref()
apikey = lolApi.loadKey("/data1/lolData/RefData/product_keys.txt")

verRequest = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
current_version = verRequest.json()[0]
champRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/champion.json")
champInfo = pd.DataFrame(champRequest.json())
champInfoDto = (pd.DataFrame(dict(champInfo["data"])).T).reset_index(drop=False)
champInfoDto = champInfoDto.astype(
    {"index": "string", "version": "string", "id": "string", "key": "string", "name": "string", "title": "string",
     "blurb": "string", "info": "string", "image": "string", "tags": "string", "partype": "string", "stats": "string"})

query_params = st.experimental_get_query_params()
tabs = ["Main", "챔피언기록", "유저기록", "인게임정보", "챔피언통계", "랭킹"]

if "tab" in query_params:
    active_tab = query_params["tab"][0]
else:
    active_tab = "Home"

if active_tab not in tabs:
    st.experimental_set_query_params(tab="Main")
    active_tab = "Main"

li_items = "".join(
    f"""
    <li class="nav-item">
        <a class="nav-link{' active' if t == active_tab else ''}" href="/?tab={t}">{t}</a>
    </li>
    """
    for t in tabs
)
tabs_html = f"""
    <ul class="nav nav-tabs">
    {li_items}
    </ul>
"""
data = pd.read_csv('/data1/tst/output/champStats.csv')
# Chamlist = tuple(data['championId'].astype('string').drop_duplicates().values)
# Linelist = tuple(data['laneEdit'].drop_duplicates().values)

st.markdown(tabs_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if active_tab == "Main":
    st.header("챔피언 리스트")
#     st.write(f"lol 게임 내의 챔피언 리스트 입니다 ({len(champInfoDto[champInfoDto['key'].isin(list(Chamlist))]['id'])} 명)")

    #cols = st.columns([4,4,2,2])
    cols = st.columns([4, 4, 4])

    userName = cols[0].text_input("챔피언명을 입력하시오.")
    userName = cols[0].text_input("소환사명을 입력하시오.")

    #cols[2].button('Top')
    #cols[2].button('Middle')
    #cols[3].button('Bottom')
    #cols[3].button('Jungle')

    with cols[2]:
        st.subheader(f"챔피어 티어")
        chosen = st.radio("",("TOP", "MIDDLE", "BOTTOM", "JUNGLE", "Support"))

    flag, idd = 0, 0
    for i in range(1, 20):
        cols = st.columns([1,1,1,1,1,1,1,1,4])

        for idx in range(0, 8):
            img_name = json.loads(champInfoDto['image'].iloc[flag + idx].replace("'", "\""))['full']

            try:
                cols[idx].image(f'/data1/tst/champion/{img_name}', use_column_width=True)

            except FileNotFoundError:
                cols[idx].image(f'/data1/tst/champion/blank.PNG', use_column_width=True)

            cols[idx].write(champInfoDto['id'].iloc[flag + idx])

        champInfoDto['key'] = champInfoDto['key'].astype('int')
        df = pd.merge(data, champInfoDto[['id', 'key']], how='left', left_on='championId', right_on='key')

        #cols[8].table(df[df['laneEdit']==chosen][['id', 'lanePropTot', 'champPropTot']].sort_values(by='lanePropTot', ascending=False).reset_index().iloc[idd:2+idd])

        flag += 8
        idd += 2

elif active_tab == "챔피언기록":

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

elif active_tab == "유저기록":
    userName = st.text_input("소환사명을 입력하시오.")
    userStats = pd.read_csv("/data1/lolData/cgLeague/sampleOutput/champStatsInd.csv")
    if userName:
        # user name
        userInfo = lolApi.summonerId(apikey, summonerName=userName)
        # get user accountId 
        userAccount = userInfo["accountId"][0]
        # select columns
        displayCol = ["laneEdit", "championId", "champCnt", "win", "kills", "deaths", "assists", "totalDamageDealt", "totalDamageDealtToChampions", "totalDamageTaken", "goldEarned", "totalMinionsKilled", "firstBloodKill", "firstTowerKill", "visionScore"]
        displayColFormat = dict(zip(["champCnt", "win", "kills", "deaths", "assists", "totalDamageDealt", "totalDamageDealtToChampions", "totalDamageTaken", "goldEarned", "totalMinionsKilled", "firstBloodKill", "firstTowerKill", "visionScore"], ["{:d}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}"]))
        userStats = userStats.loc[userStats.accountId==userAccount, displayCol]
        # change code to name
        userStats = userStats.astype({"championId":"string"}) # output 포맷 정하면 삭제
        userStats = pd.merge(ref.champInfoDto[["key", "id"]], userStats, left_on=["key"], right_on=["championId"], how="right")
        userStats["championId"] = userStats["id"]
        userStats.drop(["key", "id"], axis=1, inplace=True)
        userStats.set_index(["laneEdit", "championId"], inplace=True)
        st.dataframe(userStats.style.format(displayColFormat))

elif active_tab == "인게임정보":
    st.write("1. 이미지 기능 추가")
    
    userName = st.text_input("소환사명을 입력하시오.")    
    if userName:
        userInfo = lolApi.summonerId(apikey, summonerName=userName)
        spectator = lolApi.spectator(apikey, userInfo["id"][0])
        st.dataframe(spectator)
      
    spectator = pd.read_csv("/data1/lolData/cgLeague/sampleOutput/spectator.csv")
    userStats = pd.read_csv("/data1/lolData/cgLeague/sampleOutput/champStatsInd.csv")
    # 최신 날짜 들어가게 코드 
    summoner = pd.read_feather("/data1/lolData/cgLeague/API_ftr/210830/summonerList_210830.ftr") 
    userStats = pd.merge(summoner.loc[:,["summonerId","tier","rank","wins","losses"]], userStats.loc[:,["summonerId", "championId", "champCntTot", "win", "kills", "deaths", "assists"]], how="left")
    displayCol = ["teamId", "spell1Id", "spell2Id", "championId", "summonerName", "summonerId", "perkStyle", "perkSubStyle", "gameId", "mapId", "gameQueueConfigId", "gameStartTime", "perk0", "perk1", "perk2", "perk3", "perk4", "perk5", "statPerk0", "statPerk1", "statPerk2"]
    spectator = spectator.loc[:,displayCol]
    spectator = pd.merge(spectator, userStats, how="left")

    for team in [100,200]:
        spectatorTeam = spectator.query("teamId==@team")
        # 수정해야하는 부분
        link_jscode = JsCode("""
        function(params) {
            var eGridDiv = document.querySelector('#myGrid');
            eGridDiv.style.setProperty('width', 80);
            eGridDiv.style.setProperty('height', 80);
        }
        """)
        gb = GridOptionsBuilder.from_dataframe(spectatorTeam)
#         gb.configure_pagination(paginationPageSize=100) # 한 페이지에 출력해주는 갯수
#         gb.configure_column(cellRenderer=link_jscode, autoSizeColumns=displayCol)
#         gb.configure_grid_options(autoHeight=True, domLayout='autoHeight')
        gb.configure_grid_options(autoHeight=True)
        gridOptions = gb.build()
        data = AgGrid(
            spectatorTeam,
            height = 200, # dataframe 높이 조절
            gridOptions=gridOptions,
            allow_unsafe_jscode=True
        )      
                        
elif active_tab == "챔피언통계":
    st.write("1. 이미지 기능 추가")
    
    # champ stats by tier
    output = dict()
    output["champStats"] = pd.read_csv("/data1/lolData/cgLeague/sampleOutput/champStats.csv")
    output["tierStats"] = pd.read_csv("/data1/lolData/cgLeague/sampleOutput/champStatsTier.csv")
    displayCol = ["champCnt", "win", "kills", "deaths", "assists", "totalDamageDealt", "totalDamageDealtToChampions", "totalDamageTaken", "goldEarned", "totalMinionsKilled", "firstBloodKill", "firstTowerKill", "visionScore"]
    displayColFormat = dict(zip(["champCnt", "win", "kills", "deaths", "assists", "totalDamageDealt", "totalDamageDealtToChampions", "totalDamageTaken", "goldEarned", "totalMinionsKilled", "firstBloodKill", "firstTowerKill", "visionScore"], ["{:d}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}", "{:.2f}"]))
    
    tier = st.sidebar.selectbox("Tier", ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"])
#     champion = st.sidebar.selectbox("champion", ref.champInfoDto.id) # 챔피언 구분이 필요할까?
    lane = st.sidebar.selectbox("Lane", ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"])
    
    # chaange code to name
    output["tierStats"] = output["tierStats"].astype({"championId":"string"}) # output 포맷 정하면 삭제
    output["tierStats"] = pd.merge(ref.champInfoDto[["key", "id"]], output["tierStats"], left_on=["key"], right_on=["championId"], how="right")
    output["tierStats"]["championId"] = output["tierStats"]["id"]
    output["tierStats"].drop(["key", "id"], axis=1, inplace=True)
    output["tierStats"].set_index(["championId"], inplace=True)
    st.dataframe(output["tierStats"]
                 .query("tier==@tier and laneEdit==@lane")
                 .loc[:, displayCol]
                 .sort_values("champCnt", ascending=False))
    
elif active_tab == "랭킹":
    st.write("배치 수정해야 됨.")
    st.button("Refresh")
    apikey = lolApi.loadKey("/home/lj/git/MiniProject_LOL/APIData/product_keys.txt")
    summonerList = lolDataPull.summonerPull(apikey)
    summonerList["Ranking"] = np.arange(len(summonerList))+1
    summonerList["playCnt"] = summonerList["wins"] + summonerList["losses"]
    summonerList["winRate"] = summonerList["wins"] / summonerList["playCnt"] * 100
    st.dataframe(summonerList.loc[:, ["Ranking", "summonerName", "tier", "leaguePoints", "winRate", "playCnt"]])
    
    userStats = pd.read_csv("/data1/lolData/cgLeague/sampleOutput/champStatsInd.csv")
    for i in range(3):
        st.write(f"ranking {i+1} - Most 3")
        summonerId = summonerList.summonerId[i]
        displayCols = ["championId", "laneEdit", "champCnt" ,"win"]
        userStatsTmp = (userStats.loc[userStats.summonerId==summonerId, displayCols]
                        .sort_values("champCnt", ascending=False)
                        .head(3))
        userStatsTmp["winRate"] = userStatsTmp["win"]
        userStatsTmp["win"] = userStatsTmp["champCnt"]*userStatsTmp["winRate"]
        userStatsTmp["lose"] = userStatsTmp["champCnt"]-userStatsTmp["win"]
        st.dataframe(userStatsTmp)


else:
    st.error("Something has gone terribly wrong.")







