import requests, json, argparse, datetime, time, os
import lolApi, lolRef
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

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

# reference data
ref = lolRef.lolRef()
# api
with open("/home/lj/git/MiniProject_LOL/APIData/product_keys.txt") as f:
    apiList = f.readlines()
apiList = [x.replace("\n", "") for x in apiList]
apikey = apiList[0].replace("\n", "")

dataPath = f"/data1/lolData/cgLeague/API_csv/{args.begin.replace('2021','').replace('-','')}"
df = {"MatchParticipantFrame" : pd.DataFrame(), "MatchFrame" : pd.DataFrame(), "summonerList" : pd.DataFrame(), "MatchTimeline" : pd.DataFrame(), "MatchEvent" : pd.DataFrame(), "Participant" : pd.DataFrame(), "Match" : pd.DataFrame(), "MatchReference" : pd.DataFrame(), "TeamStats" : pd.DataFrame(), "ParticipantIdentity" : pd.DataFrame()}

for file in os.listdir(dataPath):
    dataTmp = pd.read_csv(f"{dataPath}/{file[:(len(file)-4)]}.csv", dtype=ref.formatJson["inputDtype"][f"{file[:(len(file)-8)]}Dtype"])
    df[file[:(len(file)-8)]] = pd.concat([df[file[:(len(file)-8)]], dataTmp], axis=0, ignore_index=True)    

Match = df["Match"][df["Match"].queueId.isin(["420","440"])].copy()
MatchReference = df["MatchReference"][df["MatchReference"].gameId.isin(Match.gameId.unique())].copy()
TeamStats = df["TeamStats"][df["TeamStats"].gameId.isin(Match.gameId.unique())].copy()
Participant = df["Participant"][df["Participant"].gameId.isin(Match.gameId.unique())].copy()
ParticipantIdentity = df["ParticipantIdentity"][df["ParticipantIdentity"].gameId.isin(Match.gameId.unique())].copy()
MatchTimeline = df["MatchTimeline"][df["MatchTimeline"].gameId.isin(Match.gameId.unique())].copy()
MatchFrame = df["MatchFrame"][df["MatchFrame"].gameId.isin(Match.gameId.unique())].copy()
MatchParticipantFrame = df["MatchParticipantFrame"][df["MatchParticipantFrame"].gameId.isin(Match.gameId.unique())].copy()
MatchEvent = df["MatchEvent"][df["MatchEvent"].gameId.isin(Match.gameId.unique())].copy()
MatchEvent.participantId = MatchEvent.participantId.str.replace(".0","",regex=False).astype("category")
MatchEvent.itemId = MatchEvent.itemId.str.replace(".0","",regex=False).astype("category")

# 다시하기 체크
Participant = df["Participant"][df["Participant"].gameId.isin(Match.gameId.unique())].copy()
durationGameId = set(Match.loc[Match.gameDuration < 60*5, "gameId"])
turretGameId = set(TeamStats.loc[TeamStats.towerKills<5, "gameId"])
reGameId = durationGameId&turretGameId
def rematch(data, idlist):
    data.insert(1,"reMatch", True)
    data["reMatch"] = np.where(data.gameId.isin(idlist), True, False)
for data in [Match, MatchReference, TeamStats, Participant, ParticipantIdentity, MatchParticipantFrame, MatchEvent]:
    rematch(data, reGameId)
    del data

# lane 정보 수정하기
# MatchTemp 결과값 수집
Participant.insert(2, "trollGame", False)
Participant.insert(4, "laneEdit", "None")

"""
Process 1:

Jungle Lane
1) 강타, 첫 구매템(잉걸불 칼:1035, 빗발칼날:1039)
2) Define Troll Game
2.1) 강타 x, 정글 템 x 1명 이상
2.2) 강타 o, 정글 템 x 1명 이상
2.3) 강타 o, 정글 템 o 2명 이상

Support Lane
1) 첫 구매템(주문도둑의 검:3850, 영혼의 낫, 고대유물 방패, 강철 어깨 보호대)
2) Define Troll Game
2.1) 서폿 템 x 1명 이상
2.2) 서폿 템 o 2명 이상
"""
## Jungle
# 정글 아이템 ID
jungleItemId = ref.itemInfoDto.loc[ref.itemInfoDto.name.str.contains("잉걸불 칼|빗발칼날"), "itemId"].astype("category")
# 정글 아이템 구매 Participant
participantId = MatchEvent.loc[(MatchEvent.reMatch==False)&(MatchEvent.type=='ITEM_PURCHASED')&(MatchEvent.itemId.isin(jungleItemId)), ["gameId", "participantId"]]  # jungle item 구매한 participant Id
participantId["laneTmp"] = "jungle"
participantId.drop_duplicates(keep="last", inplace=True)
Participant = pd.merge(Participant, participantId, on=["gameId", "participantId"], how="left")
Participant.loc[(Participant.reMatch==False)&((Participant.spell1Id == "11")|(Participant.spell2Id == "11"))&(Participant.laneTmp == "jungle"), "laneEdit"] = "JUNGLE"
# 각 game, 각 team 정글러 숫자 확인
Participant = Participant.astype({"laneEdit":"category"})
jungleCount = Participant.groupby(by=["gameId","teamId","laneEdit"]).agg(jungleIdx=("laneEdit","size"))
jungleCount = jungleCount.reset_index(drop=False)

# Define Troll Game
# 1) 강타 x, 정글 템 x 1명 이상
if len(jungleCount.loc[jungleCount.jungleIdx==0]) > 0:
    Participant.trollGame.where(~Participant.gameId.isin(jungleCount.loc[jungleCount.jungleIdx==0,"gameId"]), True, inplace=True)
# 2) 강타 o, 정글 템 x 1명 이상
if len(Participant.loc[((Participant.spell1Id == "11")|(Participant.spell2Id == "11"))&(Participant.laneTmp.isna())]) > 0:
    trollGameLs = Participant.loc[((Participant.spell1Id == "11")|(Participant.spell2Id == "11"))&(Participant.laneTmp.isna()), "gameId"].drop_duplicates().tolist()
    Participant.loc[Participant.gameId.isin(trollGameLs),"trollGame"] = True
    Participant.loc[(Participant.reMatch==False)&(Participant.trollGame==True)&((Participant.spell1Id == "11")|(Participant.spell2Id == "11")),"laneEdit"] = "JUNGLE"
    jungleCount = Participant.groupby(by=["gameId","teamId","laneEdit"]).agg(jungleIdx=("laneEdit","size"))
    jungleCount = jungleCount.reset_index(drop=False)
# 3) 강타 o, 정글 템 x 2명 이상
if len(jungleCount[(jungleCount.laneEdit == "JUNGLE")&(jungleCount.jungleIdx != 1)]) > 0:
    # 문제가 있는 game & team
    jungleError = jungleCount[(jungleCount.jungleIdx != 1)&(jungleCount.laneEdit == "JUNGLE")]
    jungleError = pd.merge(Participant, jungleError[["gameId","teamId","jungleIdx"]], on=["gameId","teamId"], how="inner")
    # game & 팀내 최다 정글 미니언 처치 participant
    jungleErrorCount = jungleError.groupby(["gameId","teamId"]).agg(jungleIdx=("neutralMinionsKilled","idxmax"))
    jungleErrorIdx = jungleErrorCount.reset_index(drop=False)
    jungleErrorIdx = jungleError.loc[pd.Index(jungleErrorIdx[~jungleErrorIdx.jungleIdx.isnull()].astype({"jungleIdx":"int"}).jungleIdx.tolist()), ["gameId","participantId", "teamId"]]
    jungleErrorIdx["laneTmp2"] = "jungle"
    
    ParticipantTmp = pd.merge(Participant, jungleErrorIdx[["gameId", "teamId"]].astype("string"), on=["gameId", "teamId"], how="inner")
    ParticipantTmp = pd.merge(ParticipantTmp, jungleErrorIdx, on=["gameId", "participantId", "teamId"], how="left")
    ParticipantTmp.loc[(ParticipantTmp.laneEdit=="JUNGLE")&(ParticipantTmp.laneTmp2!="jungle"), "laneTmp2"] = "nonjungle"
    
    Participant = pd.merge(Participant, ParticipantTmp[["gameId", "participantId", "teamId", "laneTmp2"]], on=["gameId", "participantId", "teamId"], how="left")
    Participant.loc[Participant.laneTmp2=="nonjungle", "laneEdit"] = "None"
    Participant.loc[Participant.laneTmp2=="jungle", "laneEdit"] = "JUNGLE"
Participant = Participant.drop(["laneTmp", "laneTmp2"], axis=1, errors="ignore")
Participant = Participant.astype({"laneEdit":"string"})

## Support
# 서폿 아이템 ID
supportItemId = ref.itemInfoDto.loc[ref.itemInfoDto.name.str.contains("주문도둑의 검|영혼의 낫|고대유물 방패|강철 어깨 보호대"), "itemId"]
# 서폿 아이템 구매 Participant
participantId = MatchEvent.loc[(MatchEvent.reMatch==False)&(MatchEvent.type=='ITEM_PURCHASED')&(MatchEvent.itemId.isin(supportItemId)), ["gameId", "participantId"]]  # support item 구매한 participant Id
participantId["laneTmp"] = "support"
participantId.drop_duplicates(keep="last", inplace=True)
Participant = pd.merge(Participant, participantId, on=["gameId", "participantId"], how="left")
Participant.loc[(Participant.laneEdit!="JUNGLE")&(Participant.laneTmp=="support"), "laneEdit"] = "SUPPORT"
# 각 game, 각 team 정글러 숫자 확인
Participant = Participant.astype({"laneEdit":"category"})
supportCount = Participant.loc[Participant.reMatch==False].groupby(by=["gameId","teamId","laneEdit"]).agg(supportIdx=("laneEdit","size"))
supportCount = supportCount.reset_index(drop=False)

# 팀별 서포터가 1명이 아닌 경우
if len(supportCount[(supportCount.laneEdit == "SUPPORT")&(supportCount.supportIdx != 1)]) > 0:
    # 문제가 있는 game & team
    supportError = supportCount[(supportCount.supportIdx != 1)&(supportCount.laneEdit=="SUPPORT")]
    supportError = pd.merge(Participant, supportError[["gameId","teamId","supportIdx"]], on=["gameId","teamId"], how="inner")
    supportError.loc[:, "totalMinionsKilledSum"] = supportError.loc[:, "totalMinionsKilled"] + supportError.loc[:, "neutralMinionsKilled"]
    # game & 팀내 최소 미니언 처치 participant
    supportErrorCount = supportError.loc[supportError.laneEdit!="JUNGLE"].groupby(["gameId","teamId"]).agg(supportIdx=("totalMinionsKilledSum","idxmin"))
    supportErrorIdx = supportErrorCount.reset_index(drop=False)
    supportErrorIdx = supportError.loc[pd.Index(supportErrorIdx[~supportErrorIdx.supportIdx.isnull()].astype({"supportIdx":"int"}).supportIdx.tolist()), ["gameId","participantId", "teamId"]]
    supportErrorIdx["laneTmp2"] = "support"

    ParticipantTmp = pd.merge(Participant, supportErrorIdx[["gameId", "teamId"]], on=["gameId", "teamId"], how="inner")
    ParticipantTmp = pd.merge(ParticipantTmp, supportErrorIdx, on=["gameId", "participantId", "teamId"], how="left")
    ParticipantTmp.loc[(ParticipantTmp.laneEdit=="SUPPORT")&(ParticipantTmp.laneTmp2!="support"), "laneTmp2"] = "nonsupport"

    Participant = pd.merge(Participant, ParticipantTmp[["gameId", "participantId", "teamId", "laneTmp2"]], on=["gameId", "participantId", "teamId"], how="left")
    Participant.loc[(Participant.laneEdit!="JUNGLE")&(Participant.laneEdit=="SUPPORT")&(Participant.laneTmp2=="nonsupport"), "laneEdit"] = "None"
    Participant.loc[(Participant.laneTmp!="JUNGLE")&(Participant.laneTmp2=="support"), "laneEdit"] = "SUPPORT"
Participant = Participant.drop(["laneTmp", "laneTmp2"], axis=1, errors="ignore")
Participant = Participant.astype({"laneEdit":"string"})

'''
Procces 2:
Top lane
0 ~ 10분, 분 단위 좌표값 10 <= xEdit <= 70, 200 <= yEdit <= 340 | 10 <= xEdit <= 170, 340 <= yEdit <= 500 | 170 <= xEdit <= 310, 440 <= yEdit <= 500 
Middle lane
0 ~ 10분, 분 단위 좌표값 176 <= xEdit <= 336, 176 <= yEdit <= 336
Bottom lane
0 ~ 10분, 분 단위 좌표값 200 <= xEdit <= 340, 10 <= yEdit <= 70 | 340 <= xEdit <= 500, 10 <= yEdit <= 170 | 460 <= xEdit <= 500, 170 <= yEdit <= 230
'''
# x,y scale 재조정
xRange = np.array([-120, 14870]).astype("float64").reshape(-1, 1)
yRange = np.array([-120, 14980]).astype("float64").reshape(-1, 1)
scaler = MinMaxScaler(feature_range=(0, 511)) # Minimap Size
scaler.fit(xRange)
MatchParticipantFrame.loc[:, ["position_xEdit"]] = scaler.transform(MatchParticipantFrame.loc[:, ["position_x"]])
scaler.fit(yRange)
MatchParticipantFrame.loc[:, ["position_yEdit"]] = scaler.transform(MatchParticipantFrame.loc[:, ["position_y"]])

# 시간별 위치 정보 dict 생성
posDict = {}
posDictGrp = {}
posDf = pd.DataFrame()
# 시간별 가중치 생성
weightList = [.5, .3, .2]
# Top, Mid, Bottom 바운더리 생성
h = 70
w = h/2**.5
m, M = 10, 502
x = (M-m)*2**.5*(2*2**.5-1)/7
polTop = Polygon([(m,M),(m,m+h+w),(m+h,m+h+w),(m+h,M-x),(m+x,M-x),(m+x,M-h),(M-w-h,M-h),(M-w-h,M)])
polMid = Polygon([(m+h,m+h+w),(m+h+w,m+h),(246-x/(2*2**.5)+w/2,246-x/(2*2**.5)-w/2),(246,246-x/2**.5),(246+x/2**.5,246),(246+x/(2*2**.5)+w/2,246+x/(2*2**.5)-w/2),(M-h,M-w-h),(M-w-h,M-h),(246+x/(2*2**.5)-w/2,246+x/(2*2**.5)+w/2),(246,246+x/2**.5),(246-x/2**.5,246),(246-x/(2*2**.5)-w/2,246-x/(2*2**.5)+w/2)])
polBot = Polygon([(m+h+w,m+h),(m+h+w,m),(M,m),(M,M-w-h),(M-h,M-w-h),(M-h,m+x),(M-x,m+x),(M-x,m+h)])
# 시간대별 각 바운더리 안에 들어가는 xy 카운트
for timePeriod in range(3):
    posDict[f"period{5*(timePeriod+1)}"] = (
        MatchParticipantFrame.loc[MatchParticipantFrame.reMatch==False, ["gameId", "participantId", "position_xEdit", "position_yEdit"]]
        .groupby(by=["gameId", "participantId"], as_index=False)
        .nth([i+timePeriod*5 for i in range(1,6)])
        .copy()
    )
    # 0 ~ 10분 좌표를 추적하여 Lane 지정
    posDict[f"period{5*(timePeriod+1)}"].loc[posDict[f"period{5*(timePeriod+1)}"].apply(lambda x: polTop.contains(Point(x['position_xEdit'], x['position_yEdit'])), axis=1)
        ,"TOP"
    ]: int = 1
    posDict[f"period{5*(timePeriod+1)}"].loc[posDict[f"period{5*(timePeriod+1)}"].apply(lambda x: polMid.contains(Point(x['position_xEdit'], x['position_yEdit'])), axis=1)
        ,"MIDDLE"
    ]: int = 1
    posDict[f"period{5*(timePeriod+1)}"].loc[posDict[f"period{5*(timePeriod+1)}"].apply(lambda x: polBot.contains(Point(x['position_xEdit'], x['position_yEdit'])), axis=1)
        ,"BOTTOM"
    ]: int = 1

    posDictGrp[f"period{5*(timePeriod+1)}"] = (
        posDict[f"period{5*(timePeriod+1)}"]
        .groupby(["gameId", "participantId"], as_index=False)
        .agg(
            {"TOP": lambda x: x.sum()*weightList[timePeriod],
             "MIDDLE": lambda x: x.sum()*weightList[timePeriod],
             "BOTTOM": lambda x: x.sum()*weightList[timePeriod],
            }
        )
    )
    
    posDf = pd.concat([posDf, posDictGrp[f"period{5*(timePeriod+1)}"]], axis=0, ignore_index=True)
posDataGrp = posDf.groupby(["gameId","participantId"], as_index=False).sum()
posDataGrp["laneEdit"] = posDataGrp[["TOP", "MIDDLE", "BOTTOM"]].idxmax(axis=1)
posDataGrp.loc[posDataGrp[['TOP', 'MIDDLE', 'BOTTOM']].sum(axis=1) == 0, 'laneEdit'] = np.random.choice(["TOP","MIDDLE","BOTTOM"])
posDataGrp["teamId"] = np.where(posDataGrp.participantId.astype(int) <= 5, "100", "200")

for timePeriod in range(3):
    posDict[f"period{5*(timePeriod+1)}"] = pd.merge(posDict[f"period{5*(timePeriod+1)}"], posDataGrp[["gameId", "participantId", "laneEdit"]], how="left", on=["gameId", "participantId"])
    posDict[f"period{5*(timePeriod+1)}"] = pd.merge(posDict[f"period{5*(timePeriod+1)}"], Participant[["gameId", "participantId", "teamId"]], how="left", on=["gameId", "participantId"])

# Top, Mid, Bot 만 정보 반영
ParticipantTmp = Participant.loc[-Participant.laneEdit.isin(["JUNGLE", "SUPPORT"]), ["gameId", "participantId"]]
ParticipantTmp["change"] = 1
ParticipantTmp = pd.merge(ParticipantTmp, posDataGrp[["gameId", "participantId", "laneEdit"]].drop_duplicates(), on=["gameId", "participantId"], how="left")
Participant = pd.merge(Participant, ParticipantTmp, on=["gameId", "participantId"], how="left", suffixes=("", "_y"))
Participant.loc[-Participant.laneEdit_y.isnull(), "laneEdit"] = Participant.loc[-Participant.laneEdit_y.isnull(), "laneEdit_y"]
Participant = Participant.drop(["change","laneEdit_y"], axis=1)

laneCount = Participant.loc[Participant.reMatch==False].groupby(["gameId","teamId","laneEdit"], as_index=False, observed=True).agg(cnt=("laneEdit","size"))
laneCount = pd.merge(laneCount, laneCount.loc[laneCount.laneEdit.isin(["TOP","MIDDLE","BOTTOM"])].groupby(["gameId","teamId"], as_index=False).agg(cntSumTMB=("cnt","sum")), on=["gameId","teamId"], how="left")

if len(laneCount[laneCount.cnt!=1]) > 0:
    print(f"{len(laneCount[laneCount.cnt!=1])} games have wrong laneEdit")
    # lane의 갯수가 문제가 있는 게임
    gameList = laneCount[(laneCount.cnt!=1)|(laneCount.laneEdit=="None")].copy()
    # 포지션 정보 수정
    ParticipantChg = pd.DataFrame()
    for gameId,teamId in zip(gameList.gameId, gameList.teamId):
        gameListTmp = gameList.loc[(gameList.gameId==gameId)&(gameList.teamId==teamId)].copy()
        # preprocessing error game
        ParticipantTmp = pd.merge(Participant, gameListTmp.loc[:,["gameId","teamId"]], on=["gameId","teamId"], how="inner")
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
    Participant = pd.merge(Participant, ParticipantChg.loc[:,["gameId","participantId","laneEdit","change"]], on=["gameId", "participantId"], how="left", suffixes=("", "_y"))
    Participant.loc[-Participant.laneEdit_y.isnull(), "laneEdit"] = Participant.loc[-Participant.laneEdit_y.isnull(), "laneEdit_y"]
    Participant = Participant.drop(["change","laneEdit_y"], axis=1)
    print("PreProcess clear")
else:
    print("PreProcess clear")

# save
createFolder(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}")

df["summonerList"].reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/summonerList{args.begin.replace('2021','').replace('-','')}.ftr")
# Match.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/Match{args.begin.replace('2021','').replace('-','')}.ftr")
# MatchReference.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchReference{args.begin.replace('2021','').replace('-','')}.ftr")
# TeamStats.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/TeamStats{args.begin.replace('2021','').replace('-','')}.ftr")
# Participant.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/Participant{args.begin.replace('2021','').replace('-','')}.ftr")
# ParticipantIdentity.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/ParticipantIdentity{args.begin.replace('2021','').replace('-','')}.ftr")
# MatchTimeline.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchTimeline{args.begin.replace('2021','').replace('-','')}.ftr")
# MatchFrame.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchFrame{args.begin.replace('2021','').replace('-','')}.ftr")
# MatchParticipantFrame.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchParticipantFrame{args.begin.replace('2021','').replace('-','')}.ftr")
# MatchEvent.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchEvent{args.begin.replace('2021','').replace('-','')}.ftr")
# positionData.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/positionData{args.begin.replace('2021','').replace('-','')}.ftr")

df["summonerList"].reset_index(drop=True).astype(ref.formatJson["inputDtype"]["summonerListDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/summonerList{args.begin.replace('2021','').replace('-','')}.ftr")
Match.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["MatchDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/Match{args.begin.replace('2021','').replace('-','')}.ftr")
MatchReference.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["MatchReferenceDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchReference{args.begin.replace('2021','').replace('-','')}.ftr")
TeamStats.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["TeamStatsDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/TeamStats{args.begin.replace('2021','').replace('-','')}.ftr")
Participant.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["ParticipantDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/Participant{args.begin.replace('2021','').replace('-','')}.ftr")
ParticipantIdentity.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["ParticipantIdentityDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/ParticipantIdentity{args.begin.replace('2021','').replace('-','')}.ftr")
MatchTimeline.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["MatchTimelineDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchTimeline{args.begin.replace('2021','').replace('-','')}.ftr")
MatchFrame.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["MatchFrameDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchFrame{args.begin.replace('2021','').replace('-','')}.ftr")
MatchParticipantFrame.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["MatchParticipantFrameDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchParticipantFrame{args.begin.replace('2021','').replace('-','')}.ftr")
MatchEvent.reset_index(drop=True).astype(ref.formatJson["inputDtype"]["MatchEventDtype"]).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/MatchEvent{args.begin.replace('2021','').replace('-','')}.ftr")
posDict["period5"].reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/period05_{args.begin.replace('2021','').replace('-','')}.ftr")
posDict["period10"].reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/period10_{args.begin.replace('2021','').replace('-','')}.ftr")
posDict["period15"].reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/period15_{args.begin.replace('2021','').replace('-','')}.ftr")