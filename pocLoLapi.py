import pandas as pd
import requests
import time, datetime
import math
"""
APIS: LEAGUE-V4
GET: /lol/league/v4/challengerleagues/by-queue/{queue}
/lol/league/v4/grandmasterleagues/by-queue/{queue}
/lol/league/v4/masterleagues/by-queue/{queue}
DESCRIPTION: Get the challenger, grandmaster, master league for given queue.
"""
def cgmLeague(apiKey, queue="RANKED_SOLO_5x5"):
    LeagueListDto = pd.DataFrame()
    for LeagueListName in ["challenger", "grandmaster", "master"]:
        while True:
            LeagueListUrl = f"https://kr.api.riotgames.com/lol/league/v4/{LeagueListName}leagues/by-queue/{queue}?api_key={apiKey}"
            LeagueListRequest = requests.get(LeagueListUrl)
            # Request 상태 코드 확인
            if LeagueListRequest.status_code == 200:
                # LeagueListDto
                LeagueListJson = LeagueListRequest.json()
                LeagueListDtoTemp = pd.DataFrame(LeagueListJson)
                # LeagueItemDto
                LeagueListItemJson = dict(LeagueListDtoTemp["entries"])
                LeagueListItemDto = pd.DataFrame(LeagueListItemJson).T
                # LeagueListDto + LeagueItemDto
                LeagueListDtoTemp = pd.concat([LeagueListDtoTemp, LeagueListItemDto], axis=1)
                LeagueListDtoTemp = LeagueListDtoTemp.drop(["entries"], axis=1)
                LeagueListDtoTemp = LeagueListDtoTemp.sort_values(by="leaguePoints")
                break
            # Rate Limit Exceeded
            elif LeagueListRequest.status_code == 429:
                startTime = time.time()
                while True:
                    if LeagueListRequest.status_code == 429:  # Infinite Loop
                        backoff = LeagueListRequest.headers.get("Retry-After")
                        if backoff is None:
                            backoff: int = 30
                        else:
                            backoff = int(backoff)
                        print("Status: 429 Error / cgmLeague Rate Limit Exceeded")
                        time.sleep(backoff)
                        LeagueListRequest = requests.get(LeagueListUrl)
                    elif LeagueListRequest.status_code == 200:  # Loop Esacpe
                        print(f"Status: 429 Recovery / {datetime.datetime.now()}")
                        break
            # Data not found
            elif LeagueListRequest.status_code == 404:
                print(f"Status: 404 / cgmLeague Data not found / {datetime.datetime.now()}")
                LeagueListRequest = pd.DataFrame()
                break
            # Service unavailable
            elif LeagueListRequest.status_code == 503:
                startTime = time.time()
                while True:
                    if LeagueListRequest.status_code == 503:  # Infinite Loop
                        backoff = LeagueListRequest.headers.get("Retry-After")
                        if backoff is None:
                            backoff: int = 30
                        else:
                            backoff = int(backoff)
                        print(f"Status: 503 / cgmLeague Service unavailable / {datetime.datetime.now()}")
                        time.sleep(backoff)
                        LeagueListRequest = requests.get(LeagueListUrl)
                    elif LeagueListRequest.status_code == 200:  # Loop Esacpe
                        print(f"Status: 503 Recovery / {datetime.datetime.now()}")
                        break
        LeagueListDto = pd.concat([LeagueListDto, LeagueListDtoTemp], ignore_index=True)
    return LeagueListDto

"""
APIS: LEAGUE-V4
GET: /lol/league/v4/entries/{queue}/{tier}/{division}
DESCRIPTION: Get all the league entries.
"""
# IRON, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND 리그 소환사 리스트
def ibsgpdLeague(apiKey, tier, division, queue="RANKED_SOLO_5x5"):
    # LeagueEntryDto
    LeagueEntryDto = pd.DataFrame()
    for page in range(1, 1000000):
        while True:
            LeagueEntryUrl = f"https://kr.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={apiKey}"
            LeagueEntryRequest = requests.get(LeagueEntryUrl)
            # Request 상태 코드 확인
            if LeagueEntryRequest.status_code == 200:
                # LeagueEntryDto
                LeagueEntryJson = LeagueEntryRequest.json()
                LeagueEntryDtoTemp = pd.DataFrame(LeagueEntryJson)
                LeagueEntryDto = pd.concat([LeagueEntryDto, LeagueEntryDtoTemp], ignore_index=True)
                break
            # Rate Limit Exceeded
            elif LeagueEntryRequest.status_code == 429:
                startTime = time.time()
                while True:
                    if LeagueEntryRequest.status_code == 429:  # Infinite Loop
                        backoff = LeagueEntryRequest.headers.get("Retry-After")
                        if backoff is None:
                            backoff: int = 30
                        else:
                            backoff = int(backoff)
                        print(f"Status: 429 / ibsgpdLeague Rate Limit Exceede / {datetime.datetime.now()}")
                        time.sleep(bakcoff)
                        LeagueEntryRequest = requests.get(LeagueEntryUrl)
                    elif LeagueEntryRequest.status_code == 200:  # Loop Esacpe
                        print(f"Status: 429 Recovery / {datetime.datetime.now()}")
                        break
            # Service unavailable
            elif LeagueEntryRequest.status_code == 503:
                print("Status: 429 / ibsgpdLeague Service unavailable")
                startTime = time.time()
                while True:
                    if LeagueEntryRequest.status_code == 503:  # Infinite Loop
                        backoff = LeagueEntryRequest.headers.get("Retry-After")
                        if backoff is None:
                            backoff: int = 30
                        else:
                            backoff = int(backoff)
                        print(f"Status: 503 / ibsgpdLeague Service unavailable / {datetime.datetime.now()}")
                        time.sleep(bakcoff)
                        LeagueEntryRequest = requests.get(LeagueEntryUrl)
                    elif LeagueEntryRequest.status_code == 200:  # Loop Esacpe
                        print(f"Status: 503 Recovery / {datetime.datetime.now()}")
                        break
        # 더 이상 추가할 페이지가 없는 경우 종료
        if len(LeagueEntryDtoTemp) == 0:
            break
    return LeagueEntryDto.rename(columns={"queueType": "queue"})

"""
APIS: SUMMONER-V4
GET: /lol/summoner/v4/summoners/by-name/{summonerName}
DESCRIPTION: Get a summoner by summoner name.
"""
def summonerId(apiKey:str, userName:str):
    while True:
        SummonerUrl = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{userName}?api_key={apiKey}"
        SummonerRequest = requests.get(SummonerUrl)
        # Request 상태 코드 확인
        if SummonerRequest.status_code == 200:
            # SummonerDto
            SummonerJson = SummonerRequest.json()
            SummonerDto = pd.DataFrame(data=[list(SummonerJson.values())], columns=list(SummonerJson.keys()))
            break
        # Rate Limit Exceeded
        elif SummonerRequest.status_code == 429:
            startTime = time.time()
            while True:
                if SummonerRequest.status_code == 429:  # Infinite Loop
                    backoff = SummonerRequest.headers.get("Retry-After")
                    if backoff is None:
                        backoff:int = 30
                    else:
                        backoff = int(backoff)
                    print(f"Status: 429 / summonerId Rate Limit Exceeded / {datetime.datetime.now()}")
                    time.sleep(backoff)
                    SummonerRequest = requests.get(SummonerUrl)
                elif SummonerRequest.status_code == 200:  # Loop Esacpe
                    print(f"Status: 429 Recovery / {datetime.datetime.now()}")
                    break
        # Data not found
        elif SummonerRequest.status_code == 404:
            print(f"Status: 404 / summonerId Data not found / {datetime.datetime.now()}")
            SummonerDto = pd.DataFrame()
            break
        # Service unavailable
        elif SummonerRequest.status_code == 503:
            startTime = time.time()
            while True:
                if SummonerRequest.status_code == 503:  # Infinite Loop
                    backoff = SummonerRequest.headers.get("Retry-After")
                    if backoff is None:
                        backoff: int = 30
                    else:
                        backoff = int(backoff)
                    print(f"Status: 503 / summonerId Service unavailable / {datetime.datetime.now()}")
                    time.sleep(backoff)
                    SummonerRequest = requests.get(SummonerUrl)
                elif SummonerRequest.status_code == 200:  # Loop Esacpe
                    print(f"Status: 503 Recovery / {datetime.datetime.now()}")
                    break
    return SummonerDto

"""
APIS: MATCH-V4
GET: /lol/match/v4/matchlists/by-account/{encryptedAccountId}
DESCRIPTION: Get matchlist for games played on given account ID and platform ID and filtered using given filter parameters, if any.
"""
def matchId(apiKey:str, accoundId:str, season:int, begintime:str="2021-02-03 00:00:00",endtime:str="2021-02-20 00:00:00"):
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
#     now = datetime.datetime.now().timestamp()
#     timestamp = math.floor(now*1000 - 60 * 60 * 24 * 30)
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
    for begintime, endtime in zip(begintimeList, endtimeList):
        for step in range(10000):
            while True:
                beginindex = 100 * step
                endindex = 100 * (step + 1)
                MatchlistUrl = f"https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{accoundId}?season={season}&beginIndex={beginindex}&endIndex={endindex}&api_key={apiKey}&beginTime={begintime}&endTime={endtime}"
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
                    break
                # Rate Limit Exceeded
                elif MatchlistRequest.status_code == 429:
                    startTime = time.time()
                    while True:
                        if MatchlistRequest.status_code == 429:  # Infinite Loop
                            backoff = MatchlistRequest.headers.get("Retry-After")
                            if backoff is None:
                                backoff:int = 30
                            else:
                                backoff = int(backoff)
                            print(f"Status: 429 / matchId Rate Limit Exceeded / Try after {backoff} / {datetime.datetime.now()}")
                            time.sleep(backoff)
                            MatchlistRequest = requests.get(MatchlistUrl)
                        elif MatchlistRequest.status_code == 200:  # Loop Esacpe
                            print(f"Status: 429 Recovery/ {datetime.datetime.now()}")
                            break
                # Data not found
                elif MatchlistRequest.status_code == 404:
                    print(f"Status: 404 / matchId Data not found / {datetime.datetime.now()}")
                    MatchlistDtoTemp = pd.DataFrame()
                    MatchReferenceDtoTemp = pd.DataFrame()
                    break
                # Service unavailable
                elif MatchlistRequest.status_code == 503:
                    startTime = time.time()
                    while True:
                        if MatchlistRequest.status_code == 503:  # Infinite Loop
                            backoff = MatchlistRequest.headers.get("Retry-After")
                            if backoff is None:
                                backoff: int = 30
                            else:
                                backoff = int(backoff)
                            print(f"Status: 503 / matchId Service unavailable / {datetime.datetime.now()}")
                            time.sleep(backoff)
                            MatchlistRequest = requests.get(MatchlistUrl)
                        elif MatchlistRequest.status_code == 200:  # Loop Esacpe
                            print(f"Status: 503 Recovery / {datetime.datetime.now()}")
                            break
                # 더 이상 추가할 페이지가 없는 경우 종료
            if len(MatchlistDtoTemp) == 0:
                break
    return MatchlistDto, MatchReferenceDto

"""
APIS: MATCH-V4
GET: /lol/match/v4/matches/{matchId}
DESCRIPTION: Get match by match ID.
"""
def matchResult(apiKey:str, matchId:str):
    while True:
        MatchUrl = f"https://kr.api.riotgames.com/lol/match/v4/matches/{matchId}?api_key={apiKey}"
        MatchRequest = requests.get(MatchUrl)
        # Request 상태 코드 확인
        if MatchRequest.status_code == 200:
            # MatchDto
            MatchJson = MatchRequest.json()
            MatchDto = pd.DataFrame(data=[list(MatchJson.values())], columns=list(MatchJson.keys()))
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
            TeamBansDto = pd.concat([pd.DataFrame(TeamStatsDto["bans"][0]).T, pd.DataFrame(TeamStatsDto["bans"][1]).T], axis=0)
            TeamBansDto.columns = [f"bans_{i}" for i in range(1, 6)]
            TeamBansDto = TeamBansDto.drop(["pickTurn"], axis=0)
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
            ParticipantStatsDto = ParticipantStatsDto.astype("int")
            # ParticipantTimelineDto
            ParticipantTimelineDto = pd.DataFrame(dict(ParticipantDto["timeline"])).T
#             for col in ["creepsPerMinDeltas","csDiffPerMinDeltas","damageTakenPerMinDeltas","damageTakenDiffPerMinDeltas","xpPerMinDeltas","xpDiffPerMinDeltas","goldPerMinDeltas"]:
#                 if ParticipantTimelineDto.get(col) is not None:
#                     tmp_release = pd.DataFrame(dict(ParticipantTimelineDto[col])).T
#                     ParticipantTimelineDto = ParticipantTimelineDto.drop(col, axis=1)
#                 else:
#                     tmp_release = pd.DataFrame({"0-10": []})
#                 tmp_release.columns = col + "_" + tmp_release.columns
#                 ParticipantTimelineDto = pd.concat([ParticipantTimelineDto, tmp_release], axis=1)
#                 ParticipantTimelineDto = ParticipantTimelineDto.sort_values(by="participantId")
#             ParticipantDto + ParticipantStatsDto + ParticipantTimelineDto
            ParticipantDto = pd.merge(ParticipantDto, ParticipantStatsDto, on="participantId")
            ParticipantDto = pd.merge(ParticipantDto, ParticipantTimelineDto, on="participantId")
            ParticipantDto = ParticipantDto.drop(["stats","timeline","creepsPerMinDeltas","csDiffPerMinDeltas","damageTakenPerMinDeltas","damageTakenDiffPerMinDeltas","xpPerMinDeltas","xpDiffPerMinDeltas","goldPerMinDeltas","combatPlayerScore","objectivePlayerScore","stringivePlayerScore","totalPlayerScore","totalScoreRank","playerScore0","playerScore1","playerScore2","playerScore3","playerScore4","playerScore5","playerScore6","playerScore7","playerScore8","playerScore9"], axis=1, errors="ignore")
            ParticipantDto.insert(0, "gameId", matchId)
            break
        # Rate Limit Exceeded
        elif MatchRequest.status_code == 429:
            startTime = time.time()
            while True:
                if MatchRequest.status_code == 429:  # Infinite Loop
                    backoff = MatchRequest.headers.get("Retry-After")
                    if backoff is None:
                        backoff:int = 30
                    else:
                        backoff = int(backoff)
                    print(f"Status: 429 / matchResult Rate Limit Exceeded / Try after {backoff} / {datetime.datetime.now()}")
                    time.sleep(backoff)
                    MatchRequest = requests.get(MatchUrl)
                elif MatchRequest.status_code == 200:  # Loop Esacpe
                    print(f"Status: 429 Recovery/ {datetime.datetime.now()}")
                    break
        # Data not found
        elif MatchRequest.status_code == 404:
            print(f"Status: 404 / matchResult Data not found / {datetime.datetime.now()}")
            MatchTemp = pd.DataFrame()
            MatchReferenceDtoTemp = pd.DataFrame()
            break
        # Service unavailable
        elif MatchRequest.status_code == 503:
            startTime = time.time()
            while True:
                if MatchRequest.status_code == 503:  # Infinite Loop
                    backoff = MatchRequest.headers.get("Retry-After")
                    if backoff is None:
                        backoff: int = 30
                    else:
                        backoff = int(backoff)
                    print(f"Status: 503 / matchResult Service unavailable / {datetime.datetime.now()}")
                    time.sleep(backoff)
                    MatchRequest = requests.get(MatchUrl)
                elif MatchRequest.status_code == 200:  # Loop Esacpe
                    print(f"Status: 503 Recovery / {datetime.datetime.now()}")
                    break
    return MatchDto, ParticipantIdentityDto, TeamStatsDto, ParticipantDto
   
"""
APIS: MATCH-V4
GET: /lol/match/v4/timelines/by-match/{matchId}
DESCRIPTION: Get match timeline by match ID.
"""
def matchTimeline(apiKey:str, matchId:str):
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
                # MatchPositionDto
                MatchPositionJson = MatchParticipantFrameDtoTemp.get("position")
                if MatchPositionJson is not None:
                    MatchPositionDtoTemp = pd.DataFrame(dict(MatchPositionJson)).T
                    MatchParticipantFrameDtoTemp.insert(3, "position_x", MatchPositionDtoTemp["x"])
                    MatchParticipantFrameDtoTemp.insert(3, "position_y", MatchPositionDtoTemp["y"])
                    MatchParticipantFrameDtoTemp = MatchParticipantFrameDtoTemp.drop(["position","dominionScore","teamScore"], axis=1, errors="ignore")
                # MatchParticipantFrameDto + MatchPositionDto
                MatchParticipantFrameDto = pd.concat([MatchParticipantFrameDto, MatchParticipantFrameDtoTemp], ignore_index=True)
            # MatchEventDto
            MatchEventDto = pd.DataFrame()
            for rownum in range(len(MatchTimelineDto.get("frames"))):
                MatchEventDtoTemp = MatchFrameDto.loc[rownum,:].get("events")
                MatchEventDtoTemp = pd.DataFrame(MatchEventDtoTemp)
                MatchEventDtoTemp.insert(0, "gameId", matchId)
                MatchEventDto = pd.concat([MatchEventDto, MatchEventDtoTemp], ignore_index=True)
            break
        # Rate Limit Exceeded
        elif MatchTimelineRequest.status_code == 429:
            startTime = time.time()
            while True:
                if MatchTimelineRequest.status_code == 429:  # Infinite Loop
                    backoff = MatchTimelineRequest.headers.get("Retry-After")
                    if backoff is None:
                        backoff: int = 30
                    else:
                        backoff = int(backoff)
                    print(f"Status: 429 / matchTimeline Rate Limit Exceeded / Try after {backoff} / {datetime.datetime.now()}")
                    time.sleep(backoff)
                    MatchTimelineRequest = requests.get(MatchTimelineUrl)
                elif MatchTimelineRequest.status_code == 200:  # Loop Esacpe
                    print(f"Status: 429 Recovery / {datetime.datetime.now()}")
                    break
        # Data not found
        elif MatchTimelineRequest.status_code == 404:
            print(f"Status: 404 / matchTimeline Data not found / {datetime.datetime.now()}")
            MatchParticipantFrameDto = pd.DataFrame()
            MatchEventDto = pd.DataFrame()
            break
        # Service unavailable
        elif MatchTimelineRequest.status_code == 503:
            startTime = time.time()
            while True:
                if MatchTimelineRequest.status_code == 503:  # Infinite Loop
                    backoff = MatchTimelineRequest.headers.get("Retry-After")
                    if backoff is None:
                        backoff: int = 30
                    else:
                        backoff = int(backoff)
                    print(f"Status: 503 / matchTimeline Service unavailable / {datetime.datetime.now()}")
                    time.sleep(backoff)
                    MatchTimelineRequest = requests.get(MatchTimelineUrl)
                elif MatchTimelineRequest.status_code == 200:  # Loop Esacpe
                    print(f"Status: 503 Recovery / {datetime.datetime.now()}")
                    break
    return MatchTimelineDto, MatchFrameDto, MatchParticipantFrameDto, MatchEventDto