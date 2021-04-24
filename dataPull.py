import argparse
import pandas as pd
import time, datetime
import lolApi
import lolModule
import requests
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import os

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.mkdir(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

# 인자값을 받을 수 있느 인스턴스 생성
parser = argparse.ArgumentParser(description='Riot api data pulling')

# parameter default value
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
today  = datetime.datetime.now().date().strftime("%Y-%m-%d")

# 입력 받을 인자값 등록
parser.add_argument('--begin', required=False, default=yesterday, help='시작일자 작성')
parser.add_argument('--end', required=False, default=today, help='종료일자 작성')

# 입력 받은 인자값을 args에 저장 (type: namespace)
args = parser.parse_args()

# 입력 받은 인자값 출력
if (args.begin != yesterday) & (args.end == today):
    args.end = (datetime.datetime.strptime(args.begin, '%Y-%m-%d') + datetime.timedelta(1)).strftime("%Y-%m-%d")
    
startTime = time.time()

with open("/home/lj/git/MiniProject_LOL/APIData/product_keys.txt") as f:
    apiList = f.readlines()
apiList = [x.replace("\n", "") for x in apiList]

apikey = apiList[0].replace("\n", "")

summonerList = pd.DataFrame()
summonerList = pd.concat((summonerList, lolApi.challengerLeague(apikey)))
summonerList = pd.concat((summonerList, lolApi.grandmasterLeague(apikey)))
# summonerList = pd.concat((summonerList, lolApi.masterLeague(apikey)))
# for division in ["I", "II", "III", "IV"]:
#     tmp = lolApi.ibsgpdLeague(apikey, "DIAMOND", division)
#     summonerList = pd.concat([summonerList, tmp], axis=0)
createFolder(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}")
summonerList.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/summonerList{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')

summonerIdList = pd.DataFrame()
Matchlist, MatchReference = pd.DataFrame(), pd.DataFrame()
Match, ParticipantIdentity, TeamStats, Participant = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
MatchTimeline, MatchFrame, MatchParticipantFrame, MatchEvent = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
CurrentGameInfo = pd.DataFrame()

for summonerIndex in range(len(summonerList)):
    try:
        print(summonerList.loc[summonerIndex, "summonerName"])
        summonerId = summonerList.summonerId[summonerIndex]
        summonerIdListTmp = lolApi.summonerId(apikey, encryptedSummonerId=summonerId)
        accountId = summonerIdListTmp.loc[0, "accountId"]
        # summoner match 정보 수집
        MatchlistTmp, MatchReferenceTmp = lolApi.matchId(apikey, accountId, 13, f"{args.begin} 00:00:00", f"{args.end} 00:00:00")
        if len(MatchlistTmp) > 0:
            for gameIdx in range(len(MatchlistTmp)):
                MatchTmp, ParticipantIdentityTmp, TeamStatsTmp, ParticipantTmp = lolApi.matchResult(apikey, MatchReferenceTmp.loc[gameIdx, "gameId"])
                MatchTimelineTmp, MatchFrameTmp, MatchParticipantFrameTmp, MatchEventTmp = lolApi.matchTimeline(apikey, MatchReferenceTmp.loc[gameIdx, "gameId"])

                Match = pd.concat((Match, MatchTmp), axis=0, ignore_index=True)
                ParticipantIdentity = pd.concat((ParticipantIdentity, ParticipantIdentityTmp), axis=0, ignore_index=True)
                TeamStats = pd.concat((TeamStats, TeamStatsTmp), axis=0, ignore_index=True)
                Participant = pd.concat((Participant, ParticipantTmp), axis=0, ignore_index=True)
                MatchTimeline = pd.concat((MatchTimeline, MatchTimelineTmp), axis=0, ignore_index=True)
                MatchFrame = pd.concat((MatchFrame, MatchFrameTmp), axis=0, ignore_index=True)
                MatchParticipantFrame = pd.concat((MatchParticipantFrame, MatchParticipantFrameTmp), axis=0, ignore_index=True)
                MatchEvent = pd.concat((MatchEvent, MatchEventTmp), axis=0, ignore_index=True)           
        Matchlist = pd.concat((Matchlist, MatchlistTmp), axis=0, ignore_index=True)
        MatchReference = pd.concat((MatchReference, MatchReferenceTmp), axis=0, ignore_index=True)

        if (summonerIndex%20 == 0)|(summonerIndex == len(summonerList)-1):
            # Drop duplicated data 
            Match = Match.drop_duplicates()
            ParticipantIdentity = ParticipantIdentity.drop_duplicates()
            TeamStats = TeamStats.drop_duplicates()
            Participant = Participant.drop_duplicates()
            # MatchTimeline = # MatchTimeline.drop_duplicates()
            # MatchFrame = # MatchFrame.drop_duplicates()
            MatchParticipantFrame = MatchParticipantFrame.drop_duplicates()
            MatchEvent = MatchEvent.drop_duplicates()
            MatchReference = MatchReference.drop_duplicates()

            # save to csv
            Match.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/Match{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
            ParticipantIdentity.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/ParticipantIdentity{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
            TeamStats.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/TeamStats{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
            Participant.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/Participant{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
            MatchTimeline.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/MatchTimeline{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
            MatchFrame.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/MatchFrame{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
            MatchParticipantFrame.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/MatchParticipantFrame{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
            MatchEvent.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/MatchEvent{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
            MatchReference.to_csv(f"/data1/lolData/cgLeague/APIData/{args.begin.replace('2021','').replace('-','')}/MatchReference{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')
    except:
        time.sleep(2)
        print(f"Connection refused {datetime.datetime.now()}")
print(f"Start: {datetime.datetime.fromtimestamp(startTime)}, End: {datetime.datetime.fromtimestamp(time.time())}, Total: {time.time()-startTime}")