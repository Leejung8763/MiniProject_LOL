import os, re, time
import numpy as np
import pandas as pd
import lolApi, lolRef
from sklearn.preprocessing import MinMaxScaler
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.mkdir(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
        
def summonerPull(apikey:str):
    """
    <apikey>
    :Description - Riot developer api key
    :Type - String
    """
    summonerList = pd.DataFrame()
    summonerList = pd.concat((summonerList, lolApi.challengerLeague(apikey)), ignore_index=True)
    summonerList = pd.concat((summonerList, lolApi.grandmasterLeague(apikey)), ignore_index=True)
    
    return summonerList

def matchPull(apikey:str, begin:str, end:str, summonerList:pd.DataFrame):
    """
    <apikey>
    :Description - Riot developer api key
    :Type - String
    
    <begin>
    :Description - The begin time to use for filtering matchlist specified as epoch milliseconds. If beginTime is specified, but not endTime, then endTime defaults to the the current unix timestamp in milliseconds (the maximum time range limitation is not observed in this specific case). If endTime is specified, but not beginTime, then beginTime defaults to the start of the account's match history returning a 400 due to the maximum time range limitation. If both are specified, then endTime should be greater than beginTime. The maximum time range allowed is one week, otherwise a 400 error code is returned.
    :Type - String
    
    <end>
    :Description - The end time to use for filtering matchlist specified as epoch milliseconds. If beginTime is specified, but not endTime, then endTime defaults to the the current unix timestamp in milliseconds (the maximum time range limitation is not observed in this specific case). If endTime is specified, but not beginTime, then beginTime defaults to the start of the account's match history returning a 400 due to the maximum time range limitation. If both are specified, then endTime should be greater than beginTime. The maximum time range allowed is one week, otherwise a 400 error code is returned.
    :Type - String
    
    <sumonnerList>
    :Description - Summoners who are in Challenger, Grandmaster tier list
    :Type - DataFrame
    """
    # set empty table for savd data
    output = {"summonerList":pd.DataFrame(),"summonerIdList":pd.DataFrame(),"Matchlist":pd.DataFrame(),"MatchReference":pd.DataFrame(),"Match":pd.DataFrame(),"ParticipantIdentity":pd.DataFrame(),"TeamStats":pd.DataFrame(),"Participant":pd.DataFrame(),"MatchTimeline":pd.DataFrame(),"MatchFrame":pd.DataFrame(),"MatchParticipantFrame":pd.DataFrame(),"MatchEvent":pd.DataFrame()}
    # specify columns of summonerList
    summonerList = summonerList[["tier","leagueId","queue","name","summonerId","summonerName","leaguePoints","rank","wins","losses","veteran","inactive","freshBlood","hotStreak"]]
    # pull match data of each summoner
    for summonerIndex in range(len(summonerList)):
        while True:
            try:
                print(summonerIndex, summonerList.loc[summonerIndex, "summonerName"])
                summonerId = summonerList.summonerId[summonerIndex]
                summonerIdListTmp = lolApi.summonerId(apikey, encryptedSummonerId=summonerId)
                summonerIdListTmp = summonerIdListTmp.rename(columns={"id":"summonerId", "name":"summonerName"})
                output["summonerIdList"] = pd.concat([output["summonerIdList"], summonerIdListTmp], ignore_index=True).drop_duplicates().reset_index(drop=True)
                accountId = summonerIdListTmp.loc[0, "accountId"]
                # summoner match ?????? ??????
                MatchlistTmp, MatchReferenceTmp = lolApi.matchId(apikey, accountId, f"{begin[:4]}-{begin[4:6]}-{begin[6:]} 00:00:00", f"{end[:4]}-{end[4:6]}-{end[6:]} 00:00:00")
                if len(MatchlistTmp) > 0:
                    for gameIdx in range(len(MatchlistTmp)):
                        MatchTmp, ParticipantIdentityTmp, TeamStatsTmp, ParticipantTmp = lolApi.matchResult(apikey, MatchReferenceTmp.loc[gameIdx, "gameId"])
                        MatchTimelineTmp, MatchFrameTmp, MatchParticipantFrameTmp, MatchEventTmp = lolApi.matchTimeline(apikey, MatchReferenceTmp.loc[gameIdx, "gameId"])
                        output["Match"] = pd.concat((output["Match"], MatchTmp), ignore_index=True).drop_duplicates().reset_index(drop=True)
                        output["ParticipantIdentity"] = pd.concat((output["ParticipantIdentity"], ParticipantIdentityTmp), ignore_index=True).drop_duplicates().reset_index(drop=True)
                        output["TeamStats"] = pd.concat((output["TeamStats"], TeamStatsTmp), ignore_index=True).drop_duplicates().reset_index(drop=True)
                        output["Participant"] = pd.concat((output["Participant"], ParticipantTmp), ignore_index=True).drop_duplicates().reset_index(drop=True)
                        output["MatchTimeline"] = pd.concat((output["MatchTimeline"], MatchTimelineTmp), ignore_index=True).astype({"frames":"string"}).drop_duplicates().reset_index(drop=True)
                        output["MatchFrame"] = pd.concat((output["MatchFrame"], MatchFrameTmp), ignore_index=True).astype({"participantFrames":"string","events":"string"}).drop_duplicates().reset_index(drop=True)
                        output["MatchParticipantFrame"] = pd.concat((output["MatchParticipantFrame"], MatchParticipantFrameTmp), ignore_index=True).drop_duplicates().reset_index(drop=True)
                        output["MatchEvent"] = pd.concat((output["MatchEvent"], MatchEventTmp), ignore_index=True).drop_duplicates().reset_index(drop=True)
                    output["Matchlist"] = pd.concat((output["Matchlist"], MatchlistTmp), ignore_index=True).astype({"matches":"string"}).drop_duplicates().reset_index(drop=True)
                    output["MatchReference"] = pd.concat((output["MatchReference"], MatchReferenceTmp), ignore_index=True).drop_duplicates().reset_index(drop=True)
                break
            except:
                time.sleep(10)
    output["summonerList"] = pd.merge(summonerList, output["summonerIdList"].drop("summonerName", axis=1), how="left").drop_duplicates().reset_index(drop=True)
    output.pop("summonerIdList")
    return output

def preprocess(begin:str, end:str, dataPath:dict):
    """
    <begin>
    :Description - The begin time to use for filtering matchlist specified as epoch milliseconds. If beginTime is specified, but not endTime, then endTime defaults to the the current unix timestamp in milliseconds (the maximum time range limitation is not observed in this specific case). If endTime is specified, but not beginTime, then beginTime defaults to the start of the account's match history returning a 400 due to the maximum time range limitation. If both are specified, then endTime should be greater than beginTime. The maximum time range allowed is one week, otherwise a 400 error code is returned.
    :Type - String
    
    <end>
    :Description - The end time to use for filtering matchlist specified as epoch milliseconds. If beginTime is specified, but not endTime, then endTime defaults to the the current unix timestamp in milliseconds (the maximum time range limitation is not observed in this specific case). If endTime is specified, but not beginTime, then beginTime defaults to the start of the account's match history returning a 400 due to the maximum time range limitation. If both are specified, then endTime should be greater than beginTime. The maximum time range allowed is one week, otherwise a 400 error code is returned.
    :Type - String
    
    <sumonnerList>
    :Description - Summoners who are in Challenger, Grandmaster tier list
    :Type - DataFrame
    """
    # reference data
    ref = lolRef.Ref()
    # data 
    data = dict()
    for file in os.listdir(dataPath):
        dataName = re.sub("_|[0-9]|.csv","", file)
        data[dataName] = pd.read_csv(f"{dataPath}/{file}", dtype=ref.formatJson["inputDtype"][f"{dataName}Dtype"])
        if sum(data[dataName].columns.str.contains("platformId")) > 0:
            data[dataName]["platformId"] = data[dataName]["platformId"].str.upper()
    data["TeamStats"] = pd.merge(data["Match"][["gameId","queueId"]], data["TeamStats"], how="right")
    data["Participant"] = pd.merge(data["Match"][["gameId","queueId"]], data["Participant"], how="right")
    data["ParticipantIdentity"] = pd.merge(data["Match"][["gameId","queueId"]], data["ParticipantIdentity"], how="right")
    data["MatchTimeline"] = pd.merge(data["Match"][["gameId","queueId"]], data["MatchTimeline"], how="right")
    data["MatchFrame"] = pd.merge(data["Match"][["gameId","queueId"]], data["MatchFrame"], how="right")
    data["MatchParticipantFrame"] = pd.merge(data["Match"][["gameId","queueId"]], data["MatchParticipantFrame"], how="right")
    # currentGold ?????? ????????? ??????
    error = data["MatchParticipantFrame"].query("-(timestamp//60000*5+145+50) > currentGold and currentGold < 0").index
    data["MatchParticipantFrame"] = data["MatchParticipantFrame"].loc[~data["MatchParticipantFrame"].index.isin(error)].reset_index(drop=True)
    data["MatchEvent"] = pd.merge(data["Match"][["gameId","queueId"]], data["MatchEvent"], how="right")
    # Id??? .0 ???????????? ?????? ??? ??????
    for file in data.keys():
        idList = [x for x in data[file].columns if re.compile("(?<!game)Id|skillSlot|bans_").search(x)]
        for col in idList:
            data[file][col] = data[file][col].str.replace(".0","",regex=False).astype("category")
    # ???????????? ??????
    durationGameId = set(data["Match"].query('gameDuration < 60*5').gameId)
    turretGameId = set(data["TeamStats"].query('towerKills<5').gameId)
    reGameId = durationGameId&turretGameId

    for key in ["Match", "MatchReference", "TeamStats", "Participant", "ParticipantIdentity", "MatchTimeline", "MatchFrame", "MatchParticipantFrame", "MatchEvent"]:
        data[key].insert(1,"reMatch", True)
        data[key]["reMatch"] = np.where(data[key].gameId.isin(reGameId), True, False)
    # lane ?????? ????????????
    # MatchTemp ????????? ??????
    data["Participant"].insert(2, "trollGame", "NORM")
    data["Participant"].insert(4, "laneEdit", "None")

    """
    Process 1:

    Jungle Lane
    1) ??????, ??? ?????????(????????? ???:1035, ????????????:1039)
    2) Define Troll Game
    2.1) ?????? x, ?????? ??? x 1??? ??????
    2.2) ?????? o, ?????? ??? x 1??? ??????
    2.3) ?????? o, ?????? ??? o 2??? ??????

    Support Lane
    1) ??? ?????????(??????????????? ???:3850, ????????? ???:3862, ???????????? ??????:3858, ?????? ?????? ?????????:3854)
    2) Define Troll Game
    2.1) ?????? ??? x 1??? ??????
    2.2) ?????? ??? o 2??? ??????
    """

    ##########
    # Jungle #
    ##########
    # ?????? ????????? ID
    jungleItemId = ref.itemInfoDto.loc[ref.itemInfoDto.name.str.contains("????????? ???|????????????"), "itemId"].astype("category")
    # ?????? ????????? ?????? Participant
    participantId = (
        data["MatchEvent"]
        .query("""
        reMatch==False\
        and queueId.str.contains("420|440")\
        and type=="ITEM_PURCHASED"\
        and itemId==@jungleItemId.tolist()\
        """)
        .loc[:,["gameId", "participantId"]]
    )
    participantId["laneTmp"] = "jungle"
    participantId.drop_duplicates(keep="last", inplace=True)
    data["Participant"] = pd.merge(data["Participant"], 
                                   participantId, 
                                   how="left")
    data["Participant"].loc[(data["Participant"].reMatch==False)
                            &((data["Participant"].spell1Id=="11")|(data["Participant"].spell2Id=="11"))
                            &(data["Participant"].laneTmp=="jungle"), "laneEdit"] = "JUNGLE"
    data["Participant"] = data["Participant"].astype({"laneEdit":"category"})

    #####################
    # Define Troll Game #
    #####################
    # n(?????? ??? ??????) ??????
    jungleCount = (
        data["Participant"]
        .query("""
        reMatch==False\
        and queueId.str.contains("420|440")
        """)
        .groupby(by=["gameId","teamId","laneEdit"])
        .agg(jungleIdx=("laneEdit","size"))
    ).reset_index(drop=False)

    # 1) n(?????? ??? ??????) != 1
    if len(jungleCount.query("laneEdit=='JUNGLE' and jungleIdx==0")) > 0:
        (
            data["Participant"]["trollGame"]
            .where(~data["Participant"].gameId.isin(jungleCount.query("laneEdit=='JUNGLE' and jungleIdx!=1")["gameId"]), "TYPE", inplace=True)
        )
        # 1.1) ?????????: 0
        jungleCount = (
            data["Participant"]
            .query("""
            reMatch==False\
            and trollGame=="TYPE"\
            and queueId.str.contains("420|440")\
            """)
            .groupby(by=["gameId","teamId","laneEdit"])
            .agg(jungleIdx=("laneEdit","size"))
        ).reset_index(drop=False)
        ParticipantTmp = pd.merge(jungleCount.query("laneEdit=='JUNGLE' and jungleIdx==0").loc[:,["gameId","teamId"]], 
                                  data["Participant"].query("queueId.str.contains('420|440')"), 
                                  how="left")
        ParticipantGrp = (ParticipantTmp
                          .query("""~(spell1Id=="11" or spell2Id=="11")""")
                          .groupby(["gameId","teamId","laneEdit"], observed=True, as_index=False)
                          .agg(cnt=("laneEdit","size")))
        ParticipantGrp["change"] = True

        # 1.1.1) ?????????: 0 / ??????: 0
        if len(jungleCount.query("""laneEdit=="JUNGLE" and jungleIdx==0""")) > 0:
            ParticipantTmp = pd.merge(ParticipantTmp, ParticipantGrp.query("cnt==5")[["gameId","teamId","change"]], how="left")
            # 1.1.1-1) ???????????? ?????? Id ??????
            errorGame = ParticipantTmp.query("change==True")[["gameId","teamId"]].drop_duplicates()
            # 1.1.1-2) ?????? ?????? ??????
            randLane = np.array([np.random.choice(["None"]*4+["JUNGLE"], 5, replace=False) for i in range(len(errorGame))]).flatten()
            ParticipantTmp.loc[ParticipantTmp.change==True, "laneEdit"] = randLane
            ParticipantTmp.loc[ParticipantTmp.change==True, "trollGame"] = "TYPE01"
            ParticipantTmp.drop("change", axis=1, inplace=True)

        # 1.1.2) ?????????: 0 / ??????: >= 1
        if len(ParticipantTmp.query("spell1Id=='11' or spell2Id=='11'")) > 0:
            # 1.1.2-1) ?????? ???????????? ?????? lane ??????
            ParticipantTmp.loc[(ParticipantTmp.spell1Id=="11")|(ParticipantTmp.spell2Id=="11"), "laneEdit"] = "JUNGLE"
            ParticipantTmp.loc[ParticipantTmp.trollGame!="TYPE01", "trollGame"] = "TYPE02"
            # 1.1.2-2) ?????? ????????? 2??? ????????? ?????? ?????? ????????? ?????? ???????????? ??????
            jungleCount = ParticipantTmp.groupby(by=["gameId","teamId","laneEdit"]).agg(jungleIdx=("laneEdit","size"))
            jungleCount.reset_index(drop=False, inplace=True)
            if len(jungleCount.query("laneEdit=='JUNGLE' and jungleIdx>1")) > 0 :
                ParticipantTmp01 = pd.merge(jungleCount.query("laneEdit=='JUNGLE' and jungleIdx>1")[["gameId","teamId"]], ParticipantTmp, how="left")
                maxJungleIdx = ParticipantTmp01.groupby(["gameId","teamId"]).agg(jungleIdx=("neutralMinionsKilled","idxmax"))
                maxJungleIdx.reset_index(drop=False, inplace=True)
                maxJungleIdx = ParticipantTmp01.loc[pd.Index(maxJungleIdx[maxJungleIdx.jungleIdx.notna()].astype({"jungleIdx":"int"}).jungleIdx.tolist()), ["gameId","participantId", "teamId"]]
                maxJungleIdx["laneTmp2"] = "jungle"
                ParticipantTmp01 = pd.merge(ParticipantTmp01, maxJungleIdx, on=["gameId", "participantId", "teamId"], how="left")
                ParticipantTmp01.loc[(ParticipantTmp01.laneEdit=="JUNGLE")&(ParticipantTmp01.laneTmp2!="jungle"), "laneTmp2"] = "nonjungle"
                ParticipantTmp = pd.merge(ParticipantTmp, ParticipantTmp01[["gameId", "participantId", "teamId", "laneTmp2"]], on=["gameId", "participantId", "teamId"], how="left")
                ParticipantTmp.loc[ParticipantTmp.laneTmp2=="nonjungle", "laneEdit"] = "None"
                ParticipantTmp.loc[ParticipantTmp.laneTmp2=="jungle", "laneEdit"] = "JUNGLE"

        for c1, c2 in ParticipantTmp.loc[:,["gameId","trollGame"]].drop_duplicates().values:
            data["Participant"].loc[data["Participant"].gameId==c1, "trollGame"] = c2
        data["Participant"] = pd.merge(data["Participant"], ParticipantTmp.loc[:,["gameId","participantId","laneEdit"]], on=["gameId","participantId"], how="left", suffixes=("","_y"))
        data["Participant"].loc[data["Participant"].laneEdit_y.notna(), "laneEdit"] = data["Participant"].loc[~data["Participant"].laneEdit_y.isna(), "laneEdit_y"]
        data["Participant"].drop("laneEdit_y", axis=1, inplace=True)

    # 1.2) ?????????: >= 2 
    # 1.2-1) ?????? ????????? ?????? ???????????? ?????? lane ??????
    jungleCount = (
        data["Participant"]
        .query(
            """
            reMatch==False\
            and queueId.str.contains("420|440")\
            """
        )
        .groupby(by=["gameId","teamId","laneEdit"])
        .agg(jungleIdx=("laneEdit","size"))
    ).reset_index(drop=False)

    if len(jungleCount.query("laneEdit=='JUNGLE' and jungleIdx>1")) > 0:
        data["Participant"].loc[data["Participant"].gameId.isin(jungleCount.query("laneEdit=='JUNGLE' and jungleIdx!=1").gameId), "trollGame"] = "TYPE03"
        ParticipantTmp = pd.merge(jungleCount.query("laneEdit=='JUNGLE' and jungleIdx!=1")[["gameId","teamId"]], data["Participant"].query("queueId.str.contains('420|440')"), how="left")
        maxJungleIdx = ParticipantTmp.query("laneEdit=='JUNGLE'").groupby(["gameId","teamId"]).agg(jungleIdx=("neutralMinionsKilled","idxmax"))
        maxJungleIdx.reset_index(drop=False, inplace=True)
        maxJungleIdx = ParticipantTmp.loc[pd.Index(maxJungleIdx[maxJungleIdx.jungleIdx.notna()].astype({"jungleIdx":"int"}).jungleIdx.tolist()), ["gameId","participantId", "teamId"]]
        maxJungleIdx["laneTmp2"] = "jungle"
        ParticipantTmp = pd.merge(data["Participant"], maxJungleIdx[["gameId", "teamId"]].astype("string"), on=["gameId", "teamId"], how="inner")
        ParticipantTmp = pd.merge(ParticipantTmp, maxJungleIdx, on=["gameId", "participantId", "teamId"], how="left")
        ParticipantTmp.loc[(ParticipantTmp.laneEdit=="JUNGLE")&(ParticipantTmp.laneTmp2!="jungle"), "laneTmp2"] = "nonjungle"
        data["Participant"] = pd.merge(data["Participant"], ParticipantTmp[["gameId", "participantId", "teamId", "laneTmp2"]], on=["gameId", "participantId", "teamId"], how="left")
        data["Participant"].loc[data["Participant"].laneTmp2=="nonjungle", "laneEdit"] = "None"
        data["Participant"].loc[data["Participant"].laneTmp2=="jungle", "laneEdit"] = "JUNGLE"
    data["Participant"].drop(["laneTmp", "laneTmp2"], axis=1, errors="ignore", inplace=True)
    data["Participant"] = data["Participant"].astype({"laneEdit":"string"})

    ###########
    # Support #
    ###########
    # ?????? ????????? ID
    supportItemId = ref.itemInfoDto.loc[ref.itemInfoDto.name.str.contains("??????????????? ???|????????? ???|???????????? ??????|?????? ?????? ?????????"), "itemId"]
    # ?????? ????????? ?????? Participant
    participantId = (
        data["MatchEvent"]
        .query("""
        reMatch==False\
        and queueId.str.contains('420|440')\
        and type=='ITEM_PURCHASED'\
        and itemId==@supportItemId.tolist()\
        """)
        .loc[:, ["gameId", "participantId"]]
    ) # support item ????????? participant Id
    participantId["laneTmp"] = "support"
    participantId.drop_duplicates(keep="last", inplace=True)
    data["Participant"] = pd.merge(data["Participant"], 
                                   participantId, 
                                   how="left")
    data["Participant"].loc[(data["Participant"].laneEdit!="JUNGLE")
                            &(data["Participant"].laneTmp=="support"), "laneEdit"] = "SUPPORT"
    # ??? game, ??? team ????????? ?????? ??????
    data["Participant"] = data["Participant"].astype({"laneEdit":"category"})

    #####################
    # Define Troll Game #
    #####################
    # n(?????? ??? ??????) ??????
    supportCount = (
        data["Participant"]
        .query("""
        reMatch==False\
        and queueId.str.contains("420|440")
        """)
        .groupby(by=["gameId","teamId","laneEdit"])
        .agg(supportIdx=("laneEdit","size"))
    ).reset_index(drop=False)

    # 2) n(?????? ??? ??????) != 1
    if len(supportCount.query("laneEdit=='SUPPORT' and supportIdx==0")) > 0:
        (
            data["Participant"]["trollGame"]
            .where(~data["Participant"].gameId.isin(supportCount.query("laneEdit=='SUPPORT' and supportIdx!=1")["gameId"]), "TYPE", inplace=True)
        )
        # 2.1) ?????????: 0
        if len(supportCount.query("laneEdit=='SUPPORT' and supportIdx==0")) > 0:
            ParticipantTmp = pd.merge(supportCount.query("laneEdit=='SUPPORT' and supportIdx==0").loc[:,["gameId","teamId"]], 
                                      data["Participant"].query("queueId.str.contains('420|440')"), 
                                      how="left")
            ParticipantTmp.loc[:, "totalMinionsKilledSum"] = ParticipantTmp.loc[:, "totalMinionsKilled"] + ParticipantTmp.loc[:, "neutralMinionsKilled"]
            errorGame = ParticipantTmp.loc[:,["gameId","teamId"]].drop_duplicates()
            randLane = np.array([np.random.choice(["None"]*3+["SUPPORT"], 4, replace=False) for i in range(len(errorGame))]).flatten()
            ParticipantTmp.loc[ParticipantTmp.laneEdit!="JUNGLE", "laneEdit"] = randLane
            ParticipantTmp.loc[:,"trollGame"] = "TYPE04"
        for c1, c2 in ParticipantTmp.loc[:,["gameId","trollGame"]].drop_duplicates().values:
            data["Participant"].loc[data["Participant"].gameId==c1, "trollGame"] = c2
        data["Participant"] = pd.merge(data["Participant"], ParticipantTmp.loc[:,["gameId","participantId","laneEdit"]], on=["gameId","participantId"], how="left", suffixes=("","_y"))
        data["Participant"].loc[data["Participant"].laneEdit_y.notna(), "laneEdit"] = data["Participant"].loc[~data["Participant"].laneEdit_y.isna(), "laneEdit_y"]
        data["Participant"].drop("laneEdit_y", axis=1, inplace=True)

    # 2.2) ?????????: >= 2
    # 2.2-1) ????????? ?????? ???????????? ?????? ?????? ??????
    supportCount = data["Participant"].query("queueId.str.contains('420|440')").groupby(by=["gameId","teamId","laneEdit"]).agg(supportIdx=("laneEdit","size"))
    supportCount.reset_index(drop=False, inplace=True)
    if len(supportCount[(supportCount.laneEdit == "SUPPORT")&(supportCount.supportIdx>1)]) > 0:
        data["Participant"].loc[data["Participant"].gameId.isin(supportCount.query("laneEdit=='SUPPORT' and supportIdx!=1").gameId), "trollGame"] = "TYPE05"
        ParticipantTmp = pd.merge(supportCount.query("laneEdit=='SUPPORT' and supportIdx!=1")[["gameId","teamId"]], data["Participant"], how="left")
        ParticipantTmp.loc[:, "totalMinionsKilledSum"] = ParticipantTmp.loc[:, "totalMinionsKilled"] + ParticipantTmp.loc[:, "neutralMinionsKilled"]
        minSupportIdx = ParticipantTmp.query("laneEdit=='SUPPORT'").groupby(["gameId","teamId"]).agg(supportIdx=("totalMinionsKilledSum","idxmin"))
        minSupportIdx.reset_index(drop=False, inplace=True)
        minSupportIdx = ParticipantTmp.loc[pd.Index(minSupportIdx[minSupportIdx.supportIdx.notna()].astype({"supportIdx":"int"}).supportIdx.tolist()), ["gameId","participantId", "teamId"]]
        minSupportIdx["laneTmp2"] = "support"
        ParticipantTmp = pd.merge(data["Participant"], minSupportIdx[["gameId", "teamId"]].astype("string"), on=["gameId", "teamId"], how="inner")
        ParticipantTmp = pd.merge(ParticipantTmp, minSupportIdx, on=["gameId", "participantId", "teamId"], how="left")
        ParticipantTmp.loc[(ParticipantTmp.laneEdit=="SUPPORT")&(ParticipantTmp.laneTmp2!="support"), "laneTmp2"] = "nonsupport"
        data["Participant"] = pd.merge(data["Participant"], ParticipantTmp[["gameId", "participantId", "teamId", "laneTmp2"]], on=["gameId", "participantId", "teamId"], how="left")
        data["Participant"].loc[data["Participant"].laneTmp2=="nonsupport", "laneEdit"] = "None"
        data["Participant"].loc[data["Participant"].laneTmp2=="support", "laneEdit"] = "SUPPORT"
    data["Participant"].drop(["laneTmp", "laneTmp2"], axis=1, errors="ignore", inplace=True)
    data["Participant"] = data["Participant"].astype({"laneEdit":"string"})

    '''
    Procces 2:
    Top lane
    0 ~ 10???, ??? ?????? ????????? 10 <= xEdit <= 70, 200 <= yEdit <= 340 | 10 <= xEdit <= 170, 340 <= yEdit <= 500 | 170 <= xEdit <= 310, 440 <= yEdit <= 500 
    Middle lane
    0 ~ 10???, ??? ?????? ????????? 176 <= xEdit <= 336, 176 <= yEdit <= 336
    Bottom lane
    0 ~ 10???, ??? ?????? ????????? 200 <= xEdit <= 340, 10 <= yEdit <= 70 | 340 <= xEdit <= 500, 10 <= yEdit <= 170 | 460 <= xEdit <= 500, 170 <= yEdit <= 230
    '''
    # x,y scale ?????????
    xRange = np.array([-120, 14870]).astype("float64").reshape(-1, 1)
    yRange = np.array([-120, 14980]).astype("float64").reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 511)) # Minimap Size
    scaler.fit(xRange)
    data["MatchParticipantFrame"].loc[:, ["position_xEdit"]] = scaler.transform(data["MatchParticipantFrame"].loc[:, ["position_x"]])
    scaler.fit(yRange)
    data["MatchParticipantFrame"].loc[:, ["position_yEdit"]] = scaler.transform(data["MatchParticipantFrame"].loc[:, ["position_y"]])
    # ????????? ?????? ?????? dict ??????
    #     posDict = {}
    posDictGrp = {}
    posDf = pd.DataFrame()
    # ????????? ????????? ??????
    weightList = [.5, .3, .2]
    # Top, Mid, Bottom ???????????? ??????
    h = 70
    w = h/2**.5
    m, M = 10, 502
    x = (M-m)*2**.5*(2*2**.5-1)/7
    polTop = Polygon([(m,M),(m,m+h+w),(m+h,m+h+w),(m+h,M-x),(m+x,M-x),(m+x,M-h),(M-w-h,M-h),(M-w-h,M)])
    polMid = Polygon([(m+h,m+h+w),(m+h+w,m+h),(246-x/(2*2**.5)+w/2,246-x/(2*2**.5)-w/2),(246,246-x/2**.5),(246+x/2**.5,246),(246+x/(2*2**.5)+w/2,246+x/(2*2**.5)-w/2),(M-h,M-w-h),(M-w-h,M-h),(246+x/(2*2**.5)-w/2,246+x/(2*2**.5)+w/2),(246,246+x/2**.5),(246-x/2**.5,246),(246-x/(2*2**.5)-w/2,246-x/(2*2**.5)+w/2)])
    polBot = Polygon([(m+h+w,m+h),(m+h+w,m),(M,m),(M,M-w-h),(M-h,M-w-h),(M-h,m+x),(M-x,m+x),(M-x,m+h)])
    # ???????????? ??? ???????????? ?????? ???????????? xy ?????????
    for timePeriod in range(3):
        data[f"period{5*(timePeriod+1):02d}"] = (
            data["MatchParticipantFrame"]
            .query("reMatch==False and queueId.str.contains('420|440')")[["gameId", "participantId", "position_xEdit", "position_yEdit"]]
            .groupby(by=["gameId", "participantId"], as_index=False)
            .nth([i+timePeriod*5 for i in range(1,6)])
            .copy()
        )
        # 0 ~ 10??? ????????? ???????????? Lane ??????
        data[f"period{5*(timePeriod+1):02d}"].loc[data[f"period{5*(timePeriod+1):02d}"].apply(lambda x: polTop.contains(Point(x['position_xEdit'], x['position_yEdit'])), axis=1)
            ,"TOP"
        ]: int = 1
        data[f"period{5*(timePeriod+1):02d}"].loc[data[f"period{5*(timePeriod+1):02d}"].apply(lambda x: polMid.contains(Point(x['position_xEdit'], x['position_yEdit'])), axis=1)
            ,"MIDDLE"
        ]: int = 1
        data[f"period{5*(timePeriod+1):02d}"].loc[data[f"period{5*(timePeriod+1):02d}"].apply(lambda x: polBot.contains(Point(x['position_xEdit'], x['position_yEdit'])), axis=1)
            ,"BOTTOM"
        ]: int = 1

        posDictGrp[f"period{5*(timePeriod+1):02d}"] = (
            data[f"period{5*(timePeriod+1):02d}"]
            .groupby(["gameId", "participantId"], as_index=False, observed=True)
            .agg(
                {"TOP": lambda x: x.sum()*weightList[timePeriod],
                 "MIDDLE": lambda x: x.sum()*weightList[timePeriod],
                 "BOTTOM": lambda x: x.sum()*weightList[timePeriod],
                }
            )
        )
        posDf = pd.concat([posDf, posDictGrp[f"period{5*(timePeriod+1):02d}"]], axis=0, ignore_index=True)
    posDataGrp = posDf.groupby(["gameId","participantId"], as_index=False).sum()
    posDataGrp["laneEdit"] = posDataGrp[["TOP", "MIDDLE", "BOTTOM"]].idxmax(axis=1)
    posDataGrp.loc[posDataGrp[['TOP', 'MIDDLE', 'BOTTOM']].sum(axis=1) == 0, 'laneEdit'] = np.random.choice(["TOP","MIDDLE","BOTTOM"])
    posDataGrp["teamId"] = np.where(posDataGrp.participantId.astype(int) <= 5, "100", "200")

    for timePeriod in range(3):
        data[f"period{5*(timePeriod+1):02d}"] = pd.merge(data[f"period{5*(timePeriod+1):02d}"], posDataGrp[["gameId", "participantId", "laneEdit"]], how="left", on=["gameId", "participantId"])
        data[f"period{5*(timePeriod+1):02d}"] = pd.merge(data[f"period{5*(timePeriod+1):02d}"], data["Participant"][["gameId", "participantId", "teamId"]], how="left", on=["gameId", "participantId"])

    # Top, Mid, Bot ??? ?????? ??????
    ParticipantTmp = data["Participant"].query("laneEdit not in ['JUNGLE','SUPPORT'] and queueId.str.contains('420|440')")[["gameId", "participantId"]]
    ParticipantTmp["change"] = 1
    ParticipantTmp = pd.merge(ParticipantTmp, posDataGrp[["gameId", "participantId", "laneEdit"]].drop_duplicates(), on=["gameId", "participantId"], how="left")
    data["Participant"] = pd.merge(data["Participant"], ParticipantTmp, on=["gameId", "participantId"], how="left", suffixes=("", "_y"))
    data["Participant"].loc[data["Participant"].laneEdit_y.notna(), "laneEdit"] = data["Participant"].loc[data["Participant"].laneEdit_y.notna(), "laneEdit_y"]
    data["Participant"] = data["Participant"].drop(["change","laneEdit_y"], axis=1)

    # n(TOP, MIDDLE, BOTTOM) ??????
    laneCount = (
        data["Participant"].query("reMatch==False and queueId.str.contains('420|440')")
        .groupby(["gameId","teamId","laneEdit"], as_index=False, observed=True)
        .agg(cnt=("laneEdit","size"))
    )
    laneCount = pd.merge(
        laneCount, 
        laneCount.query("laneEdit in ['TOP','MIDDLE','BOTTOM']").groupby(["gameId","teamId"], as_index=False).agg(cntSumTMB=("cnt","sum")), 
        on=["gameId","teamId"], 
        how="left"
    )

    # n(TOP, MIDDLE, BOTTOM) != 1
    if len(laneCount[laneCount.cnt!=1]) > 0:
        print(f"{len(laneCount.loc[laneCount.cnt!=1,'gameId'].unique())} games have wrong laneEdit")
        # lane??? ????????? ????????? ?????? ??????
        gameList = laneCount[(laneCount.cnt!=1)|(laneCount.laneEdit=="None")].copy()
        # ????????? ?????? ??????
        ParticipantChg = pd.DataFrame()
        for gameId,teamId in zip(gameList.gameId, gameList.teamId):
            gameListTmp = gameList.loc[(gameList.gameId==gameId)&(gameList.teamId==teamId)].copy()
            # preprocessing error game
            ParticipantTmp = pd.merge(data["Participant"], gameListTmp.loc[:,["gameId","teamId"]], on=["gameId","teamId"], how="inner")
            posDataGrpTmp = pd.merge(posDataGrp, gameListTmp.loc[:,["gameId","teamId"]], on=["gameId","teamId"], how="inner")
            setTot = set(["TOP","JUNGLE","MIDDLE","BOTTOM","SUPPORT"])
            setTmp = set(["JUNGLE","SUPPORT"])
            while setTot!=setTmp:
                # preprocessing error game - checking Error lane
                errorLane = ParticipantTmp.groupby(["gameId","teamId","laneEdit"], as_index=False, observed=True).agg(cnt=("laneEdit","size"))
                errorLane = errorLane.loc[errorLane.cnt>1,"laneEdit"]
                # preprocessing error game - error participant
                participantId = ParticipantTmp.loc[ParticipantTmp.laneEdit.isin(errorLane),"participantId"]
                posChgParticipant = posDataGrpTmp.loc[posDataGrpTmp.participantId.isin(participantId)].copy()
                posChgParticipant.drop(list(setTmp), errors="ignore", axis=1, inplace=True)
                posChgParticipant["laneEdit"] = errorLane.item()
                # preprocessing error game - error participant - fix largest participant to error lane
                posChgParticipant.laneEdit.where(posChgParticipant.index == posChgParticipant[f"{posChgParticipant['laneEdit'].tolist()[0]}"].idxmax(), "None", inplace=True)
                # preprocessing error game - error participant - change the others to second largest lane
                posChgParticipant.loc[posChgParticipant.laneEdit!=errorLane.item(), "laneEdit"] = posChgParticipant.drop(["gameId","participantId","laneEdit","teamId",f"{errorLane.item()}"], axis=1).loc[posChgParticipant.laneEdit!=errorLane.item()].idxmax(axis=1)
                posChgParticipant["change"] = 1
                ParticipantTmp = pd.merge(ParticipantTmp, posChgParticipant.drop(["TOP","MIDDLE","BOTTOM"], errors="ignore", axis=1), on=["gameId","teamId","participantId"], how="left", suffixes=["","_x"])
                ParticipantTmp.loc[ParticipantTmp.change==1,"laneEdit"] = ParticipantTmp.loc[ParticipantTmp.change==1,"laneEdit_x"]
                ParticipantTmp.drop(["laneEdit_x","change"], axis=1, inplace=True)
                # update setTmp
                corretLane = ParticipantTmp.groupby(["gameId","teamId","laneEdit"], as_index=False).agg(cnt=("laneEdit","size"))
                corretLane = corretLane.loc[corretLane.cnt==1,"laneEdit"]
                setTmp = set(corretLane)
            ParticipantChg = pd.concat([ParticipantChg, ParticipantTmp], axis=0, ignore_index=True)
        ParticipantChg["change"] = 1
        data["Participant"] = pd.merge(data["Participant"], ParticipantChg.loc[:,["gameId","participantId","laneEdit","change"]], on=["gameId", "participantId"], how="left", suffixes=("", "_y"))
        data["Participant"].loc[data["Participant"].laneEdit_y.notna(), "laneEdit"] = data["Participant"].loc[-data["Participant"].laneEdit_y.isnull(), "laneEdit_y"]
        data["Participant"] = data["Participant"].drop(["change","laneEdit_y"], axis=1)
        print("PreProcess clear")
    else:
        print("PreProcess clear")

    # add trollGame columns
    for key in data.keys():
        if ("gameId" in data[key].columns) and ("trollGame" not in data[key].columns):
            data[key] = pd.merge(data["Participant"][["gameId","trollGame"]].drop_duplicates(), data[key], how="right").reset_index(drop=True)
        else:
            continue

    return data