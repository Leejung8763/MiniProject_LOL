import requests, json, argparse, datetime, time, os
import pandas as pd
import numpy as np

class summaryCls:
    def __init__(self, apikey, ref):
        self.apikey = apikey
        self.output = dict()
        self.data = {"MatchParticipantFrame" : pd.DataFrame()
                  ,"MatchFrame" : pd.DataFrame()
                  ,"summonerList" : pd.DataFrame()
                  ,"MatchTimeline" : pd.DataFrame()
                  ,"MatchEvent" : pd.DataFrame()
                  ,"Participant" : pd.DataFrame()
                  ,"Match" : pd.DataFrame()
                  ,"MatchReference" : pd.DataFrame()
                  ,"TeamStats" : pd.DataFrame()
                  ,"ParticipantIdentity" : pd.DataFrame()
                  ,"period05" : pd.DataFrame()
                  ,"period10" : pd.DataFrame()
                  ,"period15" : pd.DataFrame()}
        self.idxTable = pd.DataFrame({"laneEdit":["TOP","JUNGLE","MIDDLE","BOTTON","SUPPORT"]*len(ref.champInfoDto.key),
                                      "championId":np.repeat(ref.champInfoDto.key.tolist(),5)})
    
    def dataLoad(self, endDt, timeLength, dataPath="/data1/lolData/cgLeague/API_ftr"):
        startDt = (datetime.datetime.strptime(endDt, "%Y%m%d") - datetime.timedelta(days=timeLength)).strftime('%Y%m%d')
        dateLs = pd.Series(pd.date_range(startDt, endDt)).dt.strftime('%y%m%d').tolist()
        for dataFolder in dateLs:
            if os.path.exists(os.path.join(dataPath ,dataFolder)):
                for file in ["Participant","MatchEvent","Match","TeamStats"]:
                    dataTmp00 = pd.read_feather(f"{os.path.join(dataPath, dataFolder)}/{file}_{dataFolder}.ftr")
                    dataTmp00 = dataTmp00.loc[(dataTmp00.reMatch==False)&(dataTmp00.trollGame=="NORM")&(dataTmp00.queueId.isin(["420","440"]))]
                    if file == "Participant":
                        dataTmp01 = pd.read_feather(f"{os.path.join(dataPath, dataFolder)}/ParticipantIdentity_{dataFolder}.ftr")
                        dataTmp02 = pd.read_feather(f"{os.path.join(dataPath, dataFolder)}/summonerList_{dataFolder}.ftr")
                        dataTmp01 = pd.merge(dataTmp01.loc[:,["gameId","participantId","accountId","summonerId"]], dataTmp02.loc[:,["summonerId","accountId","tier"]], how="left")
                        dataTmp00 = pd.merge(dataTmp01, dataTmp00, how="right")
                        del dataTmp01, dataTmp02
                    self.data[file] = pd.concat([self.data[file], dataTmp00], axis=0, ignore_index=True)
                    del dataTmp00                    
            else:
                continue
                
    # 경기 기록
    def gameSummary(self):
        standardDict = {"champStats":{"std1":["laneEdit","championId"] ,"std2":["championId"] ,"std3":["laneEdit"]},
                        "userStatsTot":{"std1":["accountId","summonerId","championId"] ,"std2":["accountId","summonerId","championId"] ,"std3":["accountId","summonerId"]},
                        "userStatsLane":{"std1":["accountId","summonerId","laneEdit","championId"] ,"std2":["accountId","summonerId","championId"] ,"std3":["accountId","summonerId","laneEdit"]},
                        "tierStats":{"std1":["tier","laneEdit","championId"] ,"std2":["tier","championId"] ,"std3":["tier","laneEdit"]}}
        for statName in ["champStats", "userStatsTot", "userStatsLane", "tierStats"]:
            # Mean by Champ
            laneStat = (self.data["Participant"]
                        .groupby(standardDict[statName]["std1"], as_index=False, observed=True)
                        .mean())
            # Count by Champ
            champCount = (self.data["Participant"]
                          .groupby(standardDict[statName]["std1"], as_index=False, observed=True)
                          .agg(champCnt=("championId","size")))
            ## Lane Frequency by Champ
            champCount["champCntTot"] = champCount.groupby(standardDict[statName]["std2"], observed=True).champCnt.transform("sum")
            ## Lane Proportion by Champ
            champCount["champPropTot"] = champCount["champCnt"] / champCount["champCntTot"]
            ## Lane Frequency by Lane
            champCount["laneCntTot"] = champCount.groupby(standardDict[statName]["std3"], observed=True).champCnt.transform("sum")
            ## Lane Proportion by Lane
            champCount["lanePropTot"] = champCount["champCnt"] / champCount["laneCntTot"]
            # Ban 
            banCount = self.data["TeamStats"].loc[:,["bans_1","bans_2","bans_3","bans_4","bans_5"]].stack()
            banCount = pd.DataFrame(data=banCount, columns=["championId"]).reset_index(drop=True)
        #     banCount["championId"] = banCount.championId.str.replace(".0","", regex=False) # 포멧 수정하면 코드 삭제
            banCount = banCount.groupby("championId", as_index=False, observed=True).agg(banCnt=("championId","size"))
            banCount["banCntTot"] = banCount.loc[banCount.championId!="-1", "banCnt"].sum()
            banCount["banPropTot"] = banCount["banCnt"] / banCount["banCntTot"]
            # 챔피언 통계 total
            champStats = pd.merge(champCount, banCount, how="left")
            champStats = pd.merge(champStats, laneStat, how="left")
            self.output[statName] = pd.merge(self.idxTable, champStats, how="left")
    
    # 스킬 승률
    def skillSummary(self):
        skillData = self.data["MatchEvent"].loc[~self.data["MatchEvent"].skillSlot.isnull(), ["gameId", "type", "timestamp", "participantId", "skillSlot", "levelUpType"]].copy()
        skillData = pd.merge(self.data["Participant"].loc[:,["gameId", "laneEdit", "participantId", "championId", "win"]], skillData, how="inner")
        # Skill Learn Order
        skillData["rowNum"] = skillData.groupby(["gameId","laneEdit","championId"]).cumcount()
        skillDataSelection = (
            pd.DataFrame(skillData.skillSlot)
            .set_index(pd.MultiIndex.from_frame(skillData[["gameId","laneEdit","championId","rowNum"]]))
        )
        skillDataSelection = skillDataSelection.unstack(level=-1)
        skillDataSelection.columns = [f"num{i}" for i in range(len(skillDataSelection.columns))]
        skillDataSelection = skillDataSelection.query("num14.notna()").reset_index(drop=False)
        skillData = pd.merge(skillData.loc[:, ["gameId", "laneEdit", "championId", "win"]].drop_duplicates(), skillDataSelection, how="left")
        # Cut Less than 15th
        skillData = skillData.query("num14.notna()")
        # Mean by Skill-Tree
        skillStats = (skillData
                      .groupby(["laneEdit","championId"]+[f"num{i}" for i in range(15)], as_index=False, observed=True)
                      .agg(win=("win","mean"), skillCnt=("win","size")))
        ## Skill-Tree Frequency by Champ, Lane
        skillStats["skillCntTot"] = skillStats.groupby(["laneEdit","championId"], observed=True).skillCnt.transform("sum")
        ## Skill-Tree Proportion by Champ, Lane
        skillStats["skillPropTot"] = skillStats["skillCnt"] / skillStats["skillCntTot"]
        self.output["skillStats"] = pd.merge(self.idxTable, skillStats, how="left")
        
    # 스펠 승률
    def spellSummary(self):
        spellData = self.data["Participant"].loc[self.data["Participant"]["reMatch"]==False, ["laneEdit","championId","spell1Id", "spell2Id", "win"]].copy()
        # Re-arange spell order regardless D,F
        spellData.loc[:,["spell1Id", "spell2Id"]] = np.sort(spellData.loc[:,["spell1Id", "spell2Id"]].astype(int), axis=1)
        spellData.loc[:,["spell1Id", "spell2Id"]] = spellData.loc[:,["spell1Id", "spell2Id"]].astype("category")
        # Mean by Spell-Combination
        spellStats = (spellData
                      .groupby(["laneEdit","championId","spell1Id", "spell2Id"], as_index=False, observed=True)
                      .agg(win=("win","mean"), spellCnt=("win","size")))
        ## Spell-Combination Frequency by Champ, Lane
        spellStats["spellCntTot"] = spellStats.groupby(["laneEdit","championId"], observed=True).spellCnt.transform("sum")
        ## Spell-Combination Proportion by Champ, Lane
        spellStats["spellPropTot"] = spellStats["spellCnt"] / spellStats["spellCntTot"]
        self.output["spellStats"] = pd.merge(self.idxTable, spellStats, how="left")
    
    # 룬 승률
    def runeSummary(self):
        perkLs = [i for i in self.data["Participant"].columns if ("perk" in i)&("Var" not in i)]
        runeData = self.data["Participant"].loc[self.data["Participant"]["reMatch"]==False, ["laneEdit","championId","win"]+perkLs].copy()
        runeData.loc[:,perkLs] = runeData.loc[:,perkLs].astype("category")
        # Mean by Rune-Combination
        runeStats = (runeData
                     .groupby(["laneEdit","championId"]+perkLs, as_index=False, observed=True)
                     .agg(win=("win","mean"), runeCnt=("win","size")))
        # Rune-Combination Frequency by Champ, Lane
        runeStats["runeCntTot"] = runeStats.groupby(["laneEdit","championId"], observed=True).runeCnt.transform("sum")
        ## Rune-Combination Proportion by Champ, Lane
        runeStats["runePropTot"] = runeStats["runeCnt"] / runeStats["runeCntTot"]
        self.output["runeStats"] = pd.merge(self.idxTable, runeStats, how="left")
    
    # 매치업 승률
    def matchSummary(self):
        Participant = self.data["Participant"].loc[self.data["Participant"].reMatch==False].copy()
        vsData = pd.merge(Participant, Participant, on=["gameId","reMatch","trollGame","laneEdit"], how="left", suffixes=["","Opp"])
        vsData = vsData.loc[vsData.championId!=vsData.championIdOpp].reset_index(drop=True)
        vsData.insert(3,"vsCnt",vsData.groupby(["laneEdit","championId","championIdOpp"], observed=True).championId.transform("size"))
        self.output["vsStats"] = vsData.groupby(["laneEdit","championId","championIdOpp"], as_index=False, observed=True).mean()

    # 시간대별 경기 기록
    def prdSummary(self):
        gamePrd = self.data["Match"].loc[self.data["Match"].reMatch==False, ["gameId","gameDuration"]]
        gamePrd["timeClass"] = np.where(
            gamePrd["gameDuration"] > 45*60, "45-99",
            np.where(gamePrd["gameDuration"] > 40*60, "40-45",
               np.where(gamePrd["gameDuration"] > 35*60, "35-40",
                  np.where(gamePrd["gameDuration"] > 30*60, "30-35",
                    np.where(gamePrd["gameDuration"] > 25*60, "25-30",
                      np.where(gamePrd["gameDuration"] > 20*60, "20-25",
                        np.where(gamePrd["gameDuration"] > 15*60, "15-20",
                          np.where(gamePrd["gameDuration"] > 10*60, "10-15", "None"))))))))
        gamePrd = pd.merge(gamePrd, self.data["Participant"], how="left")
        gamePrd.insert(3,"periodCnt",gamePrd.groupby(["laneEdit","championId","timeClass"], observed=True).championId.transform("size"))
        self.output["prdStats"] = (gamePrd
                   .groupby(["laneEdit","championId","timeClass"], as_index=False, observed=True)
                   .mean()
                   .sort_values(["championId","laneEdit","periodCnt"], ascending=False, ignore_index=True))