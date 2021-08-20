import numpy as np
import pandas as pd
import requests
import time, datetime
import math

errorTable = pd.read_csv("~/git/MiniProject_LOL/RefData/errorTable.csv")
errorTable = errorTable.set_index("code").to_dict(orient="index")

"""
API key
"""
def loadKey(dirName:str):
    with open(dirName) as f:
        apiList = f.readlines()
    apiList = [x.replace("\n", "") for x in apiList]
    apikey = apiList[0].replace("\n", "")
    return apikey

"""
APIS: LEAGUE-V4
GET: /lol/league/v4/challengerleagues/by-queue/{queue}
DESCRIPTION: Get the challenger league for given queue.
"""
def challengerLeague(apiKey:str, queue:str="RANKED_SOLO_5x5"):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # Infinite Loop 0
            while True:
                challengerListUrl = f"https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}?api_key={apiKey}"
                challengerListRequest = requests.get(challengerListUrl)
                # Request 상태 코드 확인
                if challengerListRequest.status_code == 200:
                    # challengerListDto
                    challengerListJson = challengerListRequest.json()
                    challengerListDto = pd.DataFrame(challengerListJson)
                    # LeagueItemDto
                    challengerListItemJson = dict(challengerListDto["entries"])
                    challengerListItemDto = pd.DataFrame(challengerListItemJson).T
                    # challengerListDto + LeagueItemDto
                    challengerListDto = pd.concat([challengerListDto, challengerListItemDto], axis=1)
                    challengerListDto = challengerListDto.drop(["entries"], axis=1)
                    challengerListDto = challengerListDto.sort_values(by="leaguePoints", ascending=False).reset_index(drop=True)
                    # Escape Infinite Loop 0
                    break
                # Error Occured
                elif challengerListRequest.status_code in [429, 502, 503, 504]:
                    backoff = int(30 if challengerListRequest.headers.get("Retry-After") is None else challengerListRequest.headers.get("Retry-After"))
                    print(f"challengerLeague function occured {errorTable[challengerListRequest.status_code]['message']} / {errorTable[challengerListRequest.status_code]['description']} / Try after {backoff}")
                    time.sleep(backoff)
                else:
                    challengerListDto = pd.DataFrame()
                    print(f"challengerLeague function occured {errorTable[challengerListRequest.status_code]['message']} / {errorTable[challengerListRequest.status_code]['description']}")
                    break   
            return challengerListDto
        except:
            time.sleep(60)
            print(f"challengerLeague Connection refused {datetime.datetime.now()}")
            maxRetry += 1

"""
APIS: LEAGUE-V4
GET: /lol/league/v4/grandmasterleagues/by-queue/{queue}
DESCRIPTION: Get the grandmaster league for given queue.
"""
def grandmasterLeague(apiKey:str, queue:str="RANKED_SOLO_5x5"):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # Infinite Loop 0
            while True:
                grandmasterListUrl = f"https://kr.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/{queue}?api_key={apiKey}"
                grandmasterListRequest = requests.get(grandmasterListUrl)
                # Request 상태 코드 확인
                if grandmasterListRequest.status_code == 200:
                    # grandmasterListDto
                    grandmasterListJson = grandmasterListRequest.json()
                    grandmasterListDto = pd.DataFrame(grandmasterListJson)
                    # LeagueItemDto
                    grandmasterListItemJson = dict(grandmasterListDto["entries"])
                    grandmasterListItemDto = pd.DataFrame(grandmasterListItemJson).T
                    # grandmasterListDto + LeagueItemDto
                    grandmasterListDto = pd.concat([grandmasterListDto, grandmasterListItemDto], axis=1)
                    grandmasterListDto = grandmasterListDto.drop(["entries"], axis=1)
                    grandmasterListDto = grandmasterListDto.sort_values(by="leaguePoints", ascending=False).reset_index(drop=True)
                    # Escape Infinite Loop 0
                    break
                # Error Occured
                elif grandmasterListRequest.status_code in [429, 502, 503, 504]:
                    backoff = int(30 if grandmasterListRequest.headers.get("Retry-After") is None else grandmasterListRequest.headers.get("Retry-After"))
                    print(f"grandmasterLeague function occured {errorTable[grandmasterListRequest.status_code]['message']} / {errorTable[grandmasterListRequest.status_code]['description']} / Try after {backoff}")
                    time.sleep(backoff)
                else:
                    grandmasterListDto = pd.DataFrame()
                    print(f"grandmasterLeague function occured {errorTable[grandmasterListRequest.status_code]['message']} / {errorTable[grandmasterListRequest.status_code]['description']}")
                    break
            return grandmasterListDto
        except:
            time.sleep(60)
            print(f"grandmasterLeague Connection refused {datetime.datetime.now()}")
            maxRetry += 1
            
"""
APIS: LEAGUE-V4
GET: /lol/league/v4/masterleagues/by-queue/{queue}
DESCRIPTION: Get the master league for given queue.
"""
def masterLeague(apiKey:str, queue:str="RANKED_SOLO_5x5"):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # Infinite Loop 0
            while True:
                masterListUrl = f"https://kr.api.riotgames.com/lol/league/v4/masterleagues/by-queue/{queue}?api_key={apiKey}"
                masterListRequest = requests.get(masterListUrl)
                # Request 상태 코드 확인
                if masterListRequest.status_code == 200:
                    # masterListDto
                    masterListJson = masterListRequest.json()
                    masterListDto = pd.DataFrame(masterListJson)
                    # LeagueItemDto
                    masterListItemJson = dict(masterListDto["entries"])
                    masterListItemDto = pd.DataFrame(masterListItemJson).T
                    # masterListDto + LeagueItemDto
                    masterListDto = pd.concat([masterListDto, masterListItemDto], axis=1)
                    masterListDto = masterListDto.drop(["entries"], axis=1)
                    masterListDto = masterListDto.sort_values(by="leaguePoints", ascending=False).reset_index(drop=True)
                    # Escape Infinite Loop 0
                    break
                # Error Occured
                elif masterListRequest.status_code in [429, 502, 503, 504]:
                    backoff = int(30 if masterListRequest.headers.get("Retry-After") is None else masterListRequest.headers.get("Retry-After"))
                    print(f"masterLeague function occured {errorTable[masterListRequest.status_code]['message']} / {errorTable[masterListRequest.status_code]['description']} / Try after {backoff}")
                    time.sleep(backoff)
                else:
                    masterListDto = pd.DataFrame()
                    print(f"masterLeague function occured {errorTable[masterListRequest.status_code]['message']} / {errorTable[masterListRequest.status_code]['description']}")
                    break  
            return masterListDto
        except:
            time.sleep(60)
            print(f"masterLeague Connection refused {datetime.datetime.now()}")
            
"""
APIS: LEAGUE-V4
GET: /lol/league/v4/entries/{queue}/{tier}/{division}
DESCRIPTION: Get all the league entries.
"""
# IRON, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND 리그 소환사 리스트
def ibsgpdLeague(apiKey, tier, division, queue="RANKED_SOLO_5x5"):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # LeagueEntryDto
            LeagueEntryDto = pd.DataFrame()
            # Infinite Loop 0   
            for page in range(1, 1000000):
                # Infinite Loop 1
                while True:
                    LeagueEntryUrl = f"https://kr.api.riotgames.com/lol/league/v4/entries/{queue}/{division}/{tier}?page={page}&api_key={apiKey}"
                    LeagueEntryRequest = requests.get(LeagueEntryUrl)
                    # Request 상태 코드 확인
                    if LeagueEntryRequest.status_code == 200:
                        # LeagueEntryDto
                        LeagueEntryJson = LeagueEntryRequest.json()
                        LeagueEntryDtoTemp = pd.DataFrame(LeagueEntryJson)
                        LeagueEntryDto = pd.concat([LeagueEntryDto, LeagueEntryDtoTemp], ignore_index=True)
                        # Escape Infinite Loop 1
                        break
                    # Error Occured
                    elif LeagueEntryRequest.status_code in [429, 502, 503, 504]:
                        backoff = int(30 if LeagueEntryRequest.headers.get("Retry-After") is None else LeagueEntryRequest.headers.get("Retry-After"))
                        print(f"ibsgpdLeague function occured {errorTable[LeagueEntryRequest.status_code]['message']} / {errorTable[LeagueEntryRequest.status_code]['description']} / Try after {backoff}")
                        time.sleep(backoff)
                    else:
                        LeagueEntryDtoTemp = pd.DataFrame()
                        print(f"ibsgpdLeague function occured {errorTable[LeagueEntryRequest.status_code]['message']} / {errorTable[LeagueEntryRequest.status_code]['description']}")
                        break  
                # 더 이상 추가할 페이지가 없는 경우 종료
                if len(LeagueEntryDtoTemp) == 0:
                    # Escape Infinite Loop 0
                    break
            LeagueEntryDto.rename(columns={"queueType": "queue"}, inplace=True)
            return LeagueEntryDto
        except:
            time.sleep(60)
            print(f"ibsgpdLeague Connection refused {datetime.datetime.now()}")
            maxRetry += 1
            
"""
APIS: SUMMONER-V4
GET: /lol/summoner/v4/summoners/by-name/{summonerName}
DESCRIPTION: Get a summoner by summoner name.
"""
def summonerId(apiKey:str, encryptedAccountId:str=None, summonerName:str=None, encryptedPUUID:str=None, encryptedSummonerId:str=None):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # Infinite Loop 0 
            while True:
                if encryptedAccountId is not None:
                    SummonerUrl = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-account/{encryptedAccountId}?api_key={apiKey}"
                elif summonerName is not None:
                    SummonerUrl = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={apiKey}"
                elif encryptedPUUID is not None:
                    SummonerUrl = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}?api_key={apiKey}"
                elif encryptedSummonerId is not None:
                    SummonerUrl = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{encryptedSummonerId}?api_key={apiKey}"
                SummonerRequest = requests.get(SummonerUrl)
                # Request 상태 코드 확인
                if SummonerRequest.status_code == 200:
                    # SummonerDto
                    SummonerJson = SummonerRequest.json()
                    SummonerDto = pd.DataFrame(data=[list(SummonerJson.values())], columns=list(SummonerJson.keys()))
                    # Escape Infinite Loop 0 
                    break
                # Error Occured
                elif SummonerRequest.status_code in [429, 502, 503, 504]:
                    backoff = int(30 if SummonerRequest.headers.get("Retry-After") is None else SummonerRequest.headers.get("Retry-After"))
                    print(f"summonerId function occured {errorTable[SummonerRequest.status_code]['message']} / {errorTable[SummonerRequest.status_code]['description']} / Try after {backoff}")
                    time.sleep(backoff)
                else:
                    SummonerDto = pd.DataFrame()
                    print(f"summonerId function occured {errorTable[SummonerRequest.status_code]['message']} / {errorTable[SummonerRequest.status_code]['description']}")
                    break  
            return SummonerDto
        except:
            time.sleep(60)
            print(f"summonerId Connection refused {datetime.datetime.now()}")
            maxRetry += 1
        
"""
APIS: MATCH-V4
GET: /lol/match/v4/matchlists/by-account/{encryptedAccountId}
DESCRIPTION: Get matchlist for games played on given account ID and platform ID and filtered using given filter parameters, if any.
"""
def matchId(apiKey:str, accountId:str, begintime:str, endtime:str):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # MatchlistDto
            MatchlistDto = pd.DataFrame()
            # MatchReferenceDto
            MatchReferenceDto = pd.DataFrame()
            # 날짜 범위 지정
            """
            If beginIndex is specified, but not endIndex, then endIndex defaults to beginIndex+100.
            If endIndex is specified, but not beginIndex, then beginIndex defaults to 0.
            If both are specified, then endIndex must be greater than beginIndex.
            The maximum range allowed is 100, otherwise a 400 error code is returned.
            local time
            """
            if len(begintime) != 0:
                begintime = math.floor(time.mktime(datetime.datetime.strptime(begintime, "%Y-%m-%d %H:%M:%S").timetuple())*1000)
            if len(endtime) != 0:
                endtime = math.floor(time.mktime(datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S").timetuple())*1000)
                if endtime - begintime <= (7 * 60 * 60 * 24) * 1000:
                    begintimeList, endtimeList = list([begintime]), list([endtime])
                elif endtime - begintime > (7 * 60 * 60 * 24) * 1000:
                    days = (endtime - begintime) / (60 * 60 * 24 * 1000)
                    weeks = math.ceil(days / 7)
                    begintimeList = [begintime + x * 7 * 60 * 60 * 24 * 1000 for x in range(weeks)]
                    endtimeList = list(map(lambda x: x + 7 * 60 * 60 * 24 * 1000, begintimeList))
                    endtimeList[-1] = endtime
            # 일주일 단위로 검색
            for begintime, endtime in zip(begintimeList, endtimeList):
                # Infinite Loop 0
                for step in range(10000):
                    # Infinite Loop 1
                    while True:
                        beginindex = 100 * step
                        endindex = 100 * (step + 1)
                        MatchlistUrl = f"https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{accountId}?beginIndex={beginindex}&endIndex={endindex}&api_key={apiKey}&beginTime={begintime}&endTime={endtime}"
                        MatchlistRequest = requests.get(MatchlistUrl)
                        # Request 상태 코드 확인
                        if MatchlistRequest.status_code == 200:
                            # MatchlistDto
                            MatchlistJson = MatchlistRequest.json()
                            MatchlistDtoTemp = pd.DataFrame(MatchlistJson)
                            MatchlistDto = pd.concat([MatchlistDto, MatchlistDtoTemp], ignore_index=True)
                            # MatchReferenceDto
                            MatchReferenceJson = MatchlistJson.get("matches")
                            MatchReferenceDtoTemp = pd.DataFrame(MatchReferenceJson)
                            MatchReferenceDto = pd.concat([MatchReferenceDto, MatchReferenceDtoTemp], ignore_index=True)
                            MatchReferenceDto = MatchReferenceDto.sort_values("timestamp").reset_index(drop=True)
                            # Escape Infinite Loop 1
                            break
                        elif MatchlistRequest.status_code in [429, 502, 503, 504]:
                            backoff = int(30 if MatchlistRequest.headers.get("Retry-After") is None else MatchlistRequest.headers.get("Retry-After"))
                            print(f"matchId function occured {errorTable[MatchlistRequest.status_code]['message']} / {errorTable[MatchlistRequest.status_code]['description']} / Try after {backoff}")
                            time.sleep(backoff)
                        else:
                            MatchlistDtoTemp = pd.DataFrame()
                            MatchReferenceDtoTemp = pd.DataFrame()
                            print(f"matchId function occured {errorTable[MatchlistRequest.status_code]['message']} / {errorTable[MatchlistRequest.status_code]['description']}")
                            break  
                        # 더 이상 추가할 페이지가 없는 경우 종료
                    if len(MatchlistDtoTemp) == 0:
                        # Infinite Loop 0
                        break
            return MatchlistDto, MatchReferenceDto
        except:
            time.sleep(60)
            print(f"matchId Connection refused {datetime.datetime.now()}")
            maxRetry += 1
            
"""
APIS: MATCH-V4
GET: /lol/match/v4/matches/{matchId}
DESCRIPTION: Get match by match ID.
"""
def matchResult(apiKey:str, matchId:str):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # Infinite Loop 0
            while True:
                MatchUrl = f"https://kr.api.riotgames.com/lol/match/v4/matches/{matchId}?api_key={apiKey}"
                MatchRequest = requests.get(MatchUrl)
                # Request 상태 코드 확인
                if MatchRequest.status_code == 200:
                    # MatchDto
                    MatchJson = MatchRequest.json()
                    MatchDto = pd.DataFrame(data=[list(MatchJson.values())], columns=list(MatchJson.keys()))
                    MatchDto = MatchDto.drop(["participantIdentities", "teams", "participants"], axis=1)
                    # ParticipantIdentityDto
                    ParticipantIdentityJson = MatchJson.get("participantIdentities")
                    ParticipantIdentityDto = pd.DataFrame(ParticipantIdentityJson)
                    Player = pd.DataFrame(dict(ParticipantIdentityDto["player"])).T
                    # ParticipantIdentityDto + PlayerDto
                    ParticipantIdentityDto = pd.concat([ParticipantIdentityDto, Player], axis=1)
                    ParticipantIdentityDto = ParticipantIdentityDto.drop(["player"], axis=1)
                    ParticipantIdentityDto = ParticipantIdentityDto.sort_values(by="participantId")
                    ParticipantIdentityDto.insert(0, "gameId", matchId)
                    # TeamStatsDto
                    TeamStatsJson = MatchJson.get("teams")
                    TeamStatsDto = pd.DataFrame(TeamStatsJson)
                    # TeamBansDto
                    if MatchDto.loc[0, 'queueId'] in [420, 440]:
                        # TeamBansDto
                        TeamBansDto = pd.concat([pd.DataFrame(TeamStatsDto["bans"][0]).T, pd.DataFrame(TeamStatsDto["bans"][1]).T], axis=0)
                        TeamBansDto.columns = [f"bans_{i}" for i in range(1, 6)]
                        TeamBansDto = TeamBansDto.drop(["pickTurn"], axis=0)
                    else:
                        TeamBansDto = pd.DataFrame()
                    # TeamStatsDto + TeamBansDto
                    TeamStatsDto = pd.concat([TeamStatsDto, TeamBansDto.reset_index(drop=True)], axis=1)
                    TeamStatsDto = TeamStatsDto.drop(["bans"], axis=1)
                    TeamStatsDto = TeamStatsDto.sort_values(by="teamId")
                    TeamStatsDto.insert(0, "gameId", matchId)
                    # ParticipantDto
                    ParticipantJson = MatchJson["participants"]
                    ParticipantDto = pd.DataFrame(ParticipantJson)
                    # ParticipantStatsDto
                    ParticipantStatsDto = pd.DataFrame(dict(ParticipantDto["stats"])).T
                    ParticipantStatsDto = ParticipantStatsDto.fillna(-9999)
                    ParticipantStatsDto = ParticipantStatsDto.astype("int")
                    # ParticipantTimelineDto
                    ParticipantTimelineDto = pd.DataFrame(dict(ParticipantDto["timeline"])).T
                    ParticipantDto = pd.merge(ParticipantDto, ParticipantStatsDto, on="participantId")
                    ParticipantDto = pd.merge(ParticipantDto, ParticipantTimelineDto, on="participantId")
                    ParticipantDto = ParticipantDto.drop(["stats","timeline","creepsPerMinDeltas","csDiffPerMinDeltas","damageTakenPerMinDeltas","damageTakenDiffPerMinDeltas","xpPerMinDeltas","xpDiffPerMinDeltas","goldPerMinDeltas","combatPlayerScore","objectivePlayerScore","stringivePlayerScore","totalPlayerScore","totalScoreRank","playerScore0","playerScore1","playerScore2","playerScore3","playerScore4","playerScore5","playerScore6","playerScore7","playerScore8","playerScore9"], axis=1, errors="ignore")
                    ParticipantDto.insert(0, "gameId", matchId)
                    # Infinite Loop 0
                    break
                # Error Occured
                elif MatchRequest.status_code in [429, 502, 503, 504]:
                    backoff = int(30 if MatchRequest.headers.get("Retry-After") is None else MatchRequest.headers.get("Retry-After"))
                    print(f"matchResult function occured {errorTable[MatchRequest.status_code]['message']} / {errorTable[MatchRequest.status_code]['description']} / Try after {backoff}")
                    time.sleep(backoff)
                else:
                    MatchDto = pd.DataFrame()
                    ParticipantIdentityDto = pd.DataFrame()
                    TeamStatsDto = pd.DataFrame()
                    ParticipantDto = pd.DataFrame()
                    print(f"matchResult function occured {errorTable[MatchRequest.status_code]['message']} / {errorTable[MatchRequest.status_code]['description']}")
                    break  
            return MatchDto, ParticipantIdentityDto, TeamStatsDto, ParticipantDto
        except:
            time.sleep(60)
            print(f"matchResult Connection refused {datetime.datetime.now()}")
            maxRetry += 1
            
"""
APIS: MATCH-V4
GET: /lol/match/v4/timelines/by-match/{matchId}
DESCRIPTION: Get match timeline by match ID.
"""
def matchTimeline(apiKey:str, matchId:str):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # Infinite Loop 0
            while True:
                MatchTimelineUrl = f"https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/{matchId}?api_key={apiKey}"
                MatchTimelineRequest = requests.get(MatchTimelineUrl)
                # Request 상태 코드 확인
                if MatchTimelineRequest.status_code == 200:
                    # MatchTimelineDto
                    MatchTimelineJson = MatchTimelineRequest.json()
                    MatchTimelineDto = pd.DataFrame(MatchTimelineJson)
                    MatchTimelineDto.insert(0, "gameId", matchId)
                    # MatchFrameDto
                    MatchFrameJson = MatchTimelineJson.get("frames")
                    MatchFrameDto = pd.DataFrame(MatchFrameJson)
                    MatchFrameDto.insert(0, "gameId", matchId)
                    # MatchParticipantFrameDto
                    MatchParticipantFrameDto = pd.DataFrame()
                    for rownum in range(len(MatchFrameDto)):
                        MatchParticipantFrameJson = MatchFrameDto.loc[rownum,:].get("participantFrames")
                        MatchParticipantFrameDtoTemp = pd.DataFrame(MatchParticipantFrameJson).T
                        MatchParticipantFrameDtoTemp.insert(0, "gameId", matchId)
                        MatchParticipantFrameDtoTemp.insert(1, "timestamp", MatchFrameDto.loc[rownum,:].get("timestamp"))               
                        MatchParticipantFrameDto = pd.concat([MatchParticipantFrameDto, MatchParticipantFrameDtoTemp], ignore_index=True)
                    # MatchPositionDto
                    MatchPositionJson = MatchParticipantFrameDto.get("position")
                    MatchPositionDtoTemp = pd.DataFrame(dict(MatchPositionJson)).T
                    # MatchParticipantFrameDto + MatchPositionDto
                    MatchParticipantFrameDto.insert(3, "position_x", MatchPositionDtoTemp["x"])
                    MatchParticipantFrameDto.insert(4, "position_y", MatchPositionDtoTemp["y"])
                    MatchParticipantFrameDto = MatchParticipantFrameDto.drop(["position","dominionScore","teamScore"], axis=1, errors="ignore")
                    # MatchEventDto
                    MatchEventDto = pd.DataFrame()
                    for rownum in range(len(MatchTimelineDto.get("frames"))):
                        MatchEventDtoTemp = MatchFrameDto.loc[rownum,:].get("events")
                        MatchEventDtoTemp = pd.DataFrame(MatchEventDtoTemp)
                        MatchEventDtoTemp.insert(0, "gameId", matchId)
                        MatchEventDto = pd.concat([MatchEventDto, MatchEventDtoTemp], ignore_index=True)
                    # MatchPositionDto
                    MatchPositionJson = MatchEventDto.get("position")
                    if MatchPositionJson is not None:
                        MatchPositionDtoTemp = pd.DataFrame(dict(MatchPositionJson)).T
                        # MatchParticipantFrameDto + MatchPositionDto
                        MatchEventDto.insert(3, "position_x", MatchPositionDtoTemp["x"])
                        MatchEventDto.insert(4, "position_y", MatchPositionDtoTemp["y"])
                        assistingParticipantIdsTmp = MatchEventDto.assistingParticipantIds.astype(str).str.replace("\[|\]|\s","", regex=True)
                        assistingParticipantIdsTmp = assistingParticipantIdsTmp.str.split(",", expand=True)
                        assistingParticipantIdsTmp = assistingParticipantIdsTmp.astype(str).replace("None|nan",np.nan, regex=True).replace("",np.nan)
                        while assistingParticipantIdsTmp.shape[1] < 5:
                            assistingParticipantIdsTmp = pd.concat((assistingParticipantIdsTmp, pd.Series(np.full(len(assistingParticipantIdsTmp), np.nan))), axis=1)
                        assistingParticipantIdsTmp.columns = [f"assistingParticipantIds{x}" for x in range(assistingParticipantIdsTmp.shape[1])]
                        for idx in assistingParticipantIdsTmp.columns.tolist()[::-1]:
                            MatchEventDto.insert(14, idx, assistingParticipantIdsTmp[idx])
                        MatchEventDto = MatchEventDto.drop(["position", "assistingParticipantIds"], axis=1, errors="ignore")
                    # Escape Infinite Loop 0
                    break
                # Error Occured
                elif MatchTimelineRequest.status_code in [429, 502, 503, 504]:
                    backoff = int(30 if MatchTimelineRequest.headers.get("Retry-After") is None else MatchTimelineRequest.headers.get("Retry-After"))
                    print(f"matchTimeline function occured {errorTable[MatchTimelineRequest.status_code]['message']} / {errorTable[MatchTimelineRequest.status_code]['description']} / Try after {backoff}")
                    time.sleep(backoff)
                else:
                    MatchTimelineDto = pd.DataFrame()
                    MatchFrameDto = pd.DataFrame()
                    MatchParticipantFrameDto = pd.DataFrame()
                    MatchEventDto = pd.DataFrame()
                    print(f"matchTimeline function occured {errorTable[MatchTimelineRequest.status_code]['message']} / {errorTable[MatchTimelineRequest.status_code]['description']}")
                    break  
            return MatchTimelineDto, MatchFrameDto, MatchParticipantFrameDto, MatchEventDto
        except:
            time.sleep(60)
            print(f"matchTimeline Connection refused {datetime.datetime.now()}")
            maxRetry += 1
            
"""
APIS: SPECTATOR-V4
GET: /lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}
DESCRIPTION: Get current game information for the given summoner ID.
"""
def spectator(apiKey:str, summonerId:str):
    maxRetry = 0
    while maxRetry < 60:
        try:
            # Infinite Loop 0
            while True:
                CurrentGameUrl = f"https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summonerId}?api_key={apiKey}"
                CurrentGameRequest = requests.get(CurrentGameUrl)
                # Request 상태 코드 확인
                if CurrentGameRequest.status_code == 200:
                    # CurrentGameInfo
                    CurrentGameJson = CurrentGameRequest.json()
                    CurrentGameInfo = pd.json_normalize(CurrentGameJson
                                                        ,record_path='participants'
                                                        ,meta=['gameId', 'mapId', 'gameMode', 'gameType', 'gameQueueConfigId',['observers','encryptionKey'], 'platformId', 'gameStartTime', 'gameLength']
                                                        ,max_level=2
                                                        ,errors="ignore")
                    perks = pd.DataFrame(dict(CurrentGameInfo["perks.perkIds"])).T
                    perks.columns = ['perk0', 'perk1', 'perk2', 'perk3', 'perk4', 'perk5', 'statPerk0', 'statPerk1', 'statPerk2']
                    CurrentGameInfo= pd.concat([CurrentGameInfo.drop("perks.perkIds", axis=1), perks], axis=1)
                    break
                # Error Occured
                elif CurrentGameRequest.status_code in [429, 502, 503, 504]:
                    backoff = 30 if CurrentGameRequest.headers.get("Retry-After") is None else CurrentGameRequest.headers.get("Retry-After")
                    print(f"spectator function occured {errorTable[CurrentGameRequest.status_code]['message']} / {errorTable[CurrentGameRequest.status_code]['description']} / Try after {backoff}")
                    time.sleep(backoff)
                else:
                    CurrentGameInfo = None
                    print(f"spectator function occured {errorTable[CurrentGameRequest.status_code]['message']} / {errorTable[CurrentGameRequest.status_code]['description']}")
                    break
            return CurrentGameInfo
        except:
            time.sleep(60)
            print(f"spectator Connection refused {datetime.datetime.now()}")
            maxRetry += 1