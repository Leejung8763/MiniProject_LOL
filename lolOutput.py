import requests, json, argparse, datetime, time, os
import pandas as pd
import numpy as np

class lolOutput:
    def __init__(self):
        output = dict()
        df = {"MatchParticipantFrame" : pd.DataFrame()
                  ,"MatchFrame" : pd.DataFrame()
                  ,"summonerList" : pd.DataFrame()
                  ,"MatchTimeline" : pd.DataFrame()
                  ,"MatchEvent" : pd.DataFrame()
                  ,"Participant" : pd.DataFrame()
                  ,"Match" : pd.DataFrame()
                  ,"MatchReference" : pd.DataFrame()
                  ,"TeamStats" : pd.DataFrame()
                  ,"ParticipantIdentity" : pd.DataFrame()
                  ,"period05_" : pd.DataFrame()
                  ,"period10_" : pd.DataFrame()
                  ,"period15_" : pd.DataFrame()}
    
    def dataLoad(self, startDt, endDt, dataPath="/data1/lolData/cgLeague/API_ftr"):
        dateLs = pd.Series(pd.date_range(startDt, endDt)).dt.strftime('%m%d').tolist()
        for dataFolder in dateLs:
            for file in os.listdir(os.path.join(dataPath ,dataFolder)):
                dataTmp = pd.read_feather(f"{os.path.join(dataPath, dataFolder)}/{file}")
                if all(fname not in file for fname in ["summoner","period"]):
                    dataTmp = dataTmp.loc[(dataTmp.reMatch==False)&(dataTmp.trollGame=="NORM")]
                df[file[:(len(file)-8)]] = pd.concat([df[file[:(len(file)-8)]], dataTmp], axis=0, ignore_index=True)

                # 경기 기록
    def gameSummary(self):
        Participant = pd.merge(df["ParticipantIdentity"].loc[:,["gameId","participantId","accountId"]], df["Participant"], how="left")
        standardDict = {"std1":["laneEdit","championId"]
                ,"std2":["championId"]
                ,"std3":["laneEdit"]}
        for statName in ["champStats", "champStatsInd"]:
            # Mean by Champ
            laneStat = (Participant
                        .groupby(standardDict["std1"], as_index=False, observed=True)
                        .mean())
            # Count by Champ
            champCount = (Participant
                          .groupby(standardDict["std1"], as_index=False, observed=True)
                          .agg(champCnt=("championId","size"))
                          .sort_values(standardDict["std1"], ascending=False, ignore_index=True))
            ## Lane Frequency by Champ
            champCount["champCntTot"] = champCount.groupby(standardDict["std2"], observed=True).champCnt.transform("sum")
            champCount["champPropTot"] = champCount["champCnt"] / champCount["champCntTot"]
            ## Lane Frequency by Lane
            champCount["laneCntTot"] = champCount.groupby(standardDict["std3"], observed=True).champCnt.transform("size")
            champCount["lanePropTot"] = champCount["champCnt"] / champCount["laneCntTot"]
            # Ban 
            banCount = df["TeamStats"].loc[:,["bans_1","bans_2","bans_3","bans_4","bans_5"]].stack()
            banCount = pd.DataFrame(data=banCount, columns=["championId"]).reset_index(drop=True)
            banCount["championId"] = banCount.championId.str.replace(".0","", regex=False) # 포멧 수정하면 코드 삭제
            banCount = banCount.groupby("championId", as_index=False, observed=True).agg(banCnt=("championId","size"))
            banCount["banCntTot"] = banCount.loc[banCount.championId!="-1", "banCnt"].sum()
            banCount["banPropTot"] = banCount["banCnt"] / banCount["banCntTot"]
            # 챔피언 통계 total
            champStats = pd.merge(champCount, banCount, how="left")
            output[statName] = pd.merge(champStats, laneStat, how="left")

            for key in standardDict.keys():
                standardDict[key] = ["accountId"] + standardDict[key]
    
    # 스킬 승률
    def skillSummary(self):
        skillDf = df["MatchEvent"].loc[~df["MatchEvent"].skillSlot.isnull(), ["gameId", "type", "timestamp", "participantId", "skillSlot", "levelUpType"]].copy()
        skillDf = pd.merge(df["Participant"].loc[:,["gameId", "participantId", "championId", "win"]], skillDf, how="inner")
        skillDf["rowNum"] = skillDf.groupby(["gameId","championId"]).cumcount()
        skillDfSelection = (pd.DataFrame(skillDf.skillSlot)
                            .set_index(pd.MultiIndex.from_frame(skillDf[["gameId","championId", "rowNum"]]))
                            .astype({"skillSlot":str}))
        skillDfSelection["skillSlot"] = skillDfSelection["skillSlot"].str.replace(".0","", regex=False)
        skillDfSelection = skillDfSelection.unstack(level=-1)
        skillDfSelection.columns = [i for i in range(21)]
        skillDf = pd.merge(skillDf.loc[:, ["gameId", "championId", "win"]].drop_duplicates(), skillDfSelection.reset_index(drop=False), how="left")
        skillDf.loc[:,skillDf.select_dtypes(object).columns] = skillDf.select_dtypes(object).fillna("None")
        output["skillStats"] = (skillDf
                                    .groupby(["championId", 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14], as_index=False, observed=True)
                                    .agg(spellCnt=("win","size"), win=("win","mean"))
                                    .sort_values(["championId","spellCnt"], ascending=False, ignore_index=True))
        
    # 스펠 승률
    def spellSummary(self):
        spellStat = df["Participant"].loc[df["Participant"]["reMatch"]==False, ["laneEdit","championId","spell1Id", "spell2Id", "win"]].copy()
        spellStat.loc[:,["spell1Id", "spell2Id"]] = np.sort(spellStat.loc[:,["spell1Id", "spell2Id"]].astype(int), axis=1)
        spellStat.loc[:,["spell1Id", "spell2Id"]] = spellStat.loc[:,["spell1Id", "spell2Id"]].astype("category")
        spellStat["spellCnt"] = spellStat.groupby(["laneEdit","championId","spell1Id", "spell2Id"], observed=True).win.transform("size")
        output["spellStat"] = (spellStat
                                    .groupby(["laneEdit","championId","spell1Id", "spell2Id"], as_index=False, observed=True)
                                    .mean()
                                    .sort_values(["laneEdit","championId","spellCnt"], ascending=False, ignore_index=True))
    
    # 룬 승률
    def runeSummary(self):
        perkLs = [i for i in df["Participant"].columns if ("perk" in i)&("Var" not in i)]
        runeStat = df["Participant"].loc[df["Participant"]["reMatch"]==False, ["laneEdit","championId","win"]+perkLs].copy()
        runeStat.loc[:,perkLs] = runeStat.loc[:,perkLs].astype("category")
        runeStat["runeCnt"] = runeStat.groupby(["laneEdit","championId"]+perkLs, observed=True).win.transform("size")
        runeStat = (runeStat
                          .groupby(["laneEdit","championId"]+perkLs, as_index=False, observed=True)
                          .mean()
                          .sort_values(["laneEdit","championId","runeCnt"], ascending=False, ignore_index=True))
    
    # 매치업 승률
    def matchSummary(self):
        Participant = df["Participant"].loc[df["Participant"].reMatch==False].copy()
        vsDto = pd.merge(Participant, Participant, on=["gameId","reMatch","trollGame","laneEdit"], how="left", suffixes=["","Opp"])
        vsDto = vsDto.loc[vsDto.championId!=vsDto.championIdOpp].reset_index(drop=True)
        vsDto["vsCnt"] = vsDto.groupby(["championId","championIdOpp"], observed=True).championId.transform("size")
        vsStat = vsDto.groupby(["championId","championIdOpp"], as_index=False, observed=True).mean()

    # 시간대별 경기 기록
    def prdSummary(self):
        gamePrd = df["Match"].loc[df["Match"].reMatch==False, ["gameId","gameDuration"]]
        gamePrd["timeClass"] = np.where(
            gamePrd["gameDuration"] > 45*60, "45-99",
            np.where(gamePrd["gameDuration"] > 40*60, "40-45",
               np.where(gamePrd["gameDuration"] > 35*60, "35-40",
                  np.where(gamePrd["gameDuration"] > 30*60, "30-35",
                    np.where(gamePrd["gameDuration"] > 25*60, "25-30",
                      np.where(gamePrd["gameDuration"] > 20*60, "20-25",
                        np.where(gamePrd["gameDuration"] > 15*60, "15-20",
                          np.where(gamePrd["gameDuration"] > 10*60, "10-15", "None"))))))))
        gamePrd = pd.merge(gamePrd, df["Participant"], how="left")
        gamePrd.insert(3,"periodCnt",gamePrd.groupby(["laneEdit","championId","timeClass"], observed=True).championId.transform("size"))
        prdStat = (gamePrd
                   .groupby(["laneEdit","championId","timeClass"], as_index=False, observed=True)
                   .mean()
                   .sort_values(["championId","laneEdit","periodCnt"], ascending=False, ignore_index=True))