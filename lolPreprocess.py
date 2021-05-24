import requests, json, argparse, datetime, time, os
import lolApi, lolRef
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

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
    data["reMatch"] = 0
    data.loc[data.gameId.isin(idlist), "reMatch"] = 1
for data in [Match, MatchReference, TeamStats, Participant, ParticipantIdentity, MatchTimeline, MatchFrame, MatchParticipantFrame, MatchEvent]:
    rematch(data, reGameId)
    del data
    
# lane 정보 수정하기
# MatchTemp 결과값 수집
Participant.insert(3, "laneEdit", "None") # lane 정보 수정하기
"""
Process 1:
Jungle Lane
1) 강타, 첫 구매템(잉걸불 칼:1035, 빗발칼날:1039)
2) 2명 이상인 경우, 정글 미니언 갯수
Support Lane
1) 돈템(주문도둑의 검:3850, 영혼의 낫, 고대유물 방패, 강철 어깨 보호대) 구매 여부 확인
2) 만에 하나 안 샀을 경우, 미니언이 가장 적은 사람
"""
## Jungle
# 정글 아이템 ID
jungleItemId = ref.itemInfoDto.loc[ref.itemInfoDto.name.str.contains("잉걸불 칼|빗발칼날"), "itemId"].astype("category")
# 정글 아이템 구매 Participant
participantId = MatchEvent.loc[(MatchEvent.type == 'ITEM_PURCHASED') & (MatchEvent.itemId.isin(jungleItemId)), ["gameId", "participantId"]]  # jungle item 구매한 participant Id
participantId["laneTmp"] = "jungle"
participantId.drop_duplicates(keep="last", inplace=True)
Participant = pd.merge(Participant, participantId, on=["gameId", "participantId"], how="left")
Participant.loc[((Participant.spell1Id == "11") | (Participant.spell2Id == "11")) & (Participant.laneTmp == "jungle"), "laneEdit"] = "JUNGLE"

# 각 game, 각 team 정글러 숫자 확인
Participant = Participant.astype({"laneEdit":"category"})
jungleCount = Participant.groupby(by=["gameId","teamId","laneEdit"]).agg(jungleIdx=("laneEdit","size"))
jungleCount = jungleCount.reset_index(drop=False)

# 팀별 정글러가 1명이 아닌 경우
if len(jungleCount[(jungleCount.laneEdit == "JUNGLE")&(jungleCount.jungleIdx != 1)]) > 0:
    # 문제가 있는 game & team
    jungleError = jungleCount[(jungleCount.jungleIdx != 1)&(jungleCount.laneEdit == "JUNGLE")]
    jungleError = pd.merge(Participant, jungleError[["gameId","teamId","jungleIdx"]], on=["gameId","teamId"], how="inner")
    # game & 팀내 최다 정글 미니언 처치 participant
    jungleErrorCount = jungleError.groupby(["gameId","teamId"]).agg(jungleIdx=("neutralMinionsKilled","idxmax"))
    jungleErrorIdx = jungleErrorCount.reset_index(drop=False)
    jungleErrorIdx = jungleError.loc[pd.Index(jungleErrorIdx[-jungleErrorIdx.jungleIdx.isnull()].astype({"jungleIdx":"int"}).jungleIdx.tolist()), ["gameId","participantId", "teamId"]]
    jungleErrorIdx["laneTmp2"] = "jungle"
    
    ParticipantTmp = pd.merge(Participant, jungleErrorIdx[["gameId", "teamId"]].astype("string"), on=["gameId", "teamId"], how="inner")
    ParticipantTmp = pd.merge(ParticipantTmp, jungleErrorIdx, on=["gameId", "participantId", "teamId"], how="left")
    ParticipantTmp.loc[(ParticipantTmp.laneTmp=="jungle")&(ParticipantTmp.laneTmp2!="jungle"), "laneTmp2"] = "nonjungle"
    
    Participant = pd.merge(Participant, ParticipantTmp[["gameId", "participantId", "teamId", "laneTmp2"]], on=["gameId", "participantId", "teamId"], how="left")
    Participant.loc[Participant.laneTmp2=="nonjungle", "laneEdit"] = "None"
    Participant.loc[Participant.laneTmp2=="jungle", "laneEdit"] = "JUNGLE"
    Participant = Participant.drop(["laneTmp", "laneTmp2"], axis=1)
    Participant = Participant.astype({"laneEdit":"string"})

## Support
# 서폿 아이템 ID
supportItemId = ref.itemInfoDto.loc[ref.itemInfoDto.name.str.contains("주문도둑의 검|영혼의 낫|고대유물 방패|강철 어깨 보호대"), "itemId"]
# 서폿 아이템 구매 Participant
participantId = MatchEvent.loc[(MatchEvent.type == 'ITEM_PURCHASED') & (MatchEvent.itemId.isin(supportItemId)), ["gameId", "participantId"]]  # support item 구매한 participant Id
participantId["laneTmp"] = "support"
participantId.drop_duplicates(keep="last", inplace=True)
Participant = pd.merge(Participant, participantId, on=["gameId", "participantId"], how="left")
Participant.loc[(Participant.laneEdit!="JUNGLE")&(Participant.laneTmp=="support"), "laneEdit"] = "SUPPORT"
# 각 game, 각 team 정글러 숫자 확인
Participant = Participant.astype({"laneEdit":"category"})
supportCount = Participant.groupby(by=["gameId","teamId","laneEdit"]).agg(supportIdx=("laneEdit","size"))
supportCount = supportCount.reset_index(drop=False)
# 팀별 서포터가 1명이 아닌 경우
if len(supportCount[(supportCount.laneEdit == "SUPPORT")&(supportCount.supportIdx != 1)]) > 0:
    # 문제가 있는 game & team
    supportError = supportCount[(supportCount.laneEdit=="SUPPORT")&(supportCount.supportIdx != 1)]
    supportError = pd.merge(Participant, supportError[["gameId","teamId","supportIdx"]], on=["gameId","teamId"], how="inner")
    supportError.loc[:, "totalMinionsKilledSum"] = supportError.loc[:, "totalMinionsKilled"] + supportError.loc[:, "neutralMinionsKilled"]
    # game & 팀내 최소 미니언 처치 participant
    supportErrorCount = supportError.groupby(["gameId","teamId"]).agg(supportIdx=("totalMinionsKilledSum","idxmin"))
    supportErrorIdx = supportErrorCount.reset_index(drop=False)
    supportErrorIdx = supportError.loc[pd.Index(supportErrorIdx[-supportErrorIdx.supportIdx.isnull()].astype({"supportIdx":"int"}).supportIdx.tolist()), ["gameId","participantId", "teamId"]]
    supportErrorIdx["laneTmp2"] = "support"

    ParticipantTmp = pd.merge(Participant, supportErrorIdx[["gameId", "teamId"]], on=["gameId", "teamId"], how="inner")
    ParticipantTmp = pd.merge(ParticipantTmp, supportErrorIdx, on=["gameId", "participantId", "teamId"], how="left")
    ParticipantTmp.loc[ParticipantTmp.laneTmp2!="support", "laneTmp2"] = "nonsupport"

    Participant = pd.merge(Participant, ParticipantTmp[["gameId", "participantId", "teamId", "laneTmp2"]], on=["gameId", "participantId", "teamId"], how="left")
    Participant.loc[(Participant.laneTmp=="support")&(Participant.laneTmp2=="nonsupport"), "laneEdit"] = "None"
    Participant.loc[Participant.laneTmp2=="support", "laneEdit"] = "SUPPORT"
    Participant = Participant.drop(["laneTmp", "laneTmp2"], axis=1)
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
scaler = MinMaxScaler(feature_range=(0, 512)) # Minimap Size
scaler.fit(xRange)
MatchParticipantFrame.loc[:, ["position_xEdit"]] = scaler.transform(MatchParticipantFrame.loc[:, ["position_x"]])
scaler.fit(yRange)
MatchParticipantFrame.loc[:, ["position_yEdit"]] = scaler.transform(MatchParticipantFrame.loc[:, ["position_y"]])
# 0 ~ 10분 데이터 추출
positionData = (
    MatchParticipantFrame.loc[:, ["gameId", "participantId", "position_xEdit", "position_yEdit"]]
    .groupby(by=["gameId", "participantId"])
    .head(15)
    .copy()
)
# 0 ~ 10분 좌표를 추적하여 Lane 지정
positionData.loc[
    ((positionData.position_xEdit >= 10)& (positionData.position_xEdit <= 70)
    & (positionData.position_yEdit >= 200)& (positionData.position_yEdit <= 340)) |
    ((positionData.position_xEdit >= 10)& (positionData.position_xEdit <= 170)
    & (positionData.position_yEdit >= 340)& (positionData.position_yEdit <= 500)) |
    ((positionData.position_xEdit >= 170)& (positionData.position_xEdit <= 310)
    & (positionData.position_yEdit >= 440)& (positionData.position_yEdit <= 500))
    ,"TOP",
]: int = 1
positionData.loc[
    (positionData.position_xEdit >= 170)& (positionData.position_xEdit <= 340)
    & (positionData.position_yEdit >= 170)& (positionData.position_yEdit <= 340),
    "MIDDLE",
]: int = 1
positionData.loc[
    ((positionData.position_xEdit >= 200)& (positionData.position_xEdit <= 340)
    & (positionData.position_yEdit >= 10)& (positionData.position_yEdit <= 70)) |
    ((positionData.position_xEdit >= 340)& (positionData.position_xEdit <= 500)
    & (positionData.position_yEdit >= 10)& (positionData.position_yEdit <= 170)) |
    ((positionData.position_xEdit >= 440)& (positionData.position_xEdit <= 500)
    & (positionData.position_yEdit >= 170)& (positionData.position_yEdit <= 310)),
    "BOTTOM",
]: int = 1

positionDataGroup = positionData.groupby(["gameId", "participantId"]).sum().reset_index(drop=False)
positionDataGroup["laneEdit"] = positionDataGroup[["TOP", "MIDDLE", "BOTTOM"]].idxmax(axis=1)
positionDataGroup.loc[positionDataGroup[['TOP', 'MIDDLE', 'BOTTOM']].sum(axis=1) == 0, 'laneEdit'] = None
positionData = pd.merge(positionData, positionDataGroup[["gameId", "participantId", "laneEdit"]], how="left", on=["gameId", "participantId"])
positionData = pd.merge(positionData, Participant[["gameId", "participantId", "teamId"]], how="left", on=["gameId", "participantId"])

# 탑 미드 원딜만 정보 반영
ParticipantTmp = Participant.loc[-Participant.laneEdit.isin(["JUNGLE", "SUPPORT"]), ["gameId", "participantId"]]
ParticipantTmp = pd.merge(ParticipantTmp, positionData[["gameId", "participantId", "laneEdit"]].drop_duplicates(), on=["gameId", "participantId"], how="left")

Participant = pd.merge(Participant, ParticipantTmp, on=["gameId", "participantId"], how="left", suffixes=("", "_y"))
Participant.loc[-Participant.laneEdit_y.isnull(), "laneEdit"] = Participant.loc[-Participant.laneEdit_y.isnull(), "laneEdit_y"]
Participant = Participant.drop("laneEdit_y", axis=1)

# save
createFolder(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}")

# df["summonerList"].reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/summonerList{args.begin.replace('2021','').replace('-','')}.ftr")
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
positionData.reset_index(drop=True).to_feather(f"/data1/lolData/cgLeague/API_ftr/{args.begin.replace('2021','').replace('-','')}/positionData{args.begin.replace('2021','').replace('-','')}.ftr")