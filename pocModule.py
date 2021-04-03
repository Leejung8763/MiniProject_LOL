import pocLoLapi as lol
import pandas as pd
import numpy as np
import requests, json
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# version data 확인
verRequest = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
current_version = verRequest.json()[0]
# Champion Info DataFrame
champRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/champion.json")
champInfo = pd.DataFrame(champRequest.json())
champInfoDto = (pd.DataFrame(dict(champInfo['data'])).T).reset_index(drop=False)
champInfoDto = champInfoDto.astype({'key':int})
# Champion Info DataFrame
itemRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/item.json")
itemInfoDto = pd.DataFrame(itemRequest.json()['data']).T
itemInfoDto.reset_index(drop=False, inplace=True)
itemInfoDto.rename(columns={'index':'itemId'}, inplace=True)
itemInfoDto = itemInfoDto.astype({'itemId':int})
# Spell Info DataFrame
spellRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/summoner.json")
spellInfo = pd.DataFrame(spellRequest.json())
spellInfoDto = pd.concat([spellInfo, pd.DataFrame(dict(spellInfo["data"])).T], axis=1)
spellInfoDto = spellInfoDto.drop(["data"], axis=1)
spellInfoDto = spellInfoDto.reset_index(drop=True)
spellInfoDto = spellInfoDto.astype({'key':int})
# Summoner's Rift DataFrame
mapUrl = f"https://ddragon.leagueoflegends.com/cdn/10.18.1/img/map/map11.png"
lolMap = plt.imread(mapUrl)
# Rune Info DataFrame
runeRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/runesReforged.json")
runeInfoDto = pd.DataFrame(runeRequest.json())
perk0 = pd.DataFrame(dict(runeInfoDto["slots"]))
runeInfoDto.drop('slots', axis=1, inplace=True)
for col0 in perk0.columns:
    perk1 = pd.DataFrame(dict(perk0[col0]))
    for col1 in perk1.columns:
        perk2 = pd.DataFrame(dict(perk1[col1])).T
        for col2 in perk2.columns:
            perk3 = pd.DataFrame(dict(perk2[col2])).T
            runeInfoDto = pd.concat([runeInfoDto, perk3], axis=0, ignore_index=True)
runeRequest2 = requests.get(f"http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json")
runeInfoDto2 = pd.DataFrame(runeRequest2.json())
runeInfoDto2 = runeInfoDto2[runeInfoDto2.id <6000].rename(columns={'name':'key',"iconPath":'icon'}).drop(['majorChangePatchVersion','tooltip','endOfGameStatDescs'], axis=1)
runeInfoDto2['name'] = ['마법 저항력 +8','방어력 +6','적응형 능력치 +9','체력 +10~90 (레벨에 비례)','재사용 대기시간 감소 +1~10% (레벨에 비례)','공격 속도 +10%']
runeInfoDto = pd.concat([runeInfoDto, runeInfoDto2]) 
runeInfoDto = runeInfoDto.astype({'id':int})
# format Json 파일
with open('/home/lj/git/KTRolster/RefData/formatJson.json', "r") as loadfile:
    formatJson = json.load(loadfile)
    
def laneEdit(apikey, summoner, begintime, endtime):
    # summoner id 정보 수집
    Summoner = lol.summonerId(apikey, summoner)
    accountid = Summoner.loc[0, "accountId"]
    # summoner match 정보 수집
    Matchlist, MatchReference = lol.matchId(apikey, accountid, 13, begintime=begintime, endtime=endtime)
    Matchlist["summonerName"] = Summoner.loc[0, "name"]
    Matchlist["accountId"] = Summoner.loc[0, "accountId"]
    MatchReference = MatchReference.drop_duplicates(subset="gameId", keep="first")
    MatchReference = MatchReference.loc[MatchReference.queue==420,:]
    MatchReference.insert(1, "summonerName", [Summoner.loc[0, "name"]]*len(MatchReference))
    MatchReference.insert(2, "accountId", [Summoner.loc[0, "accountId"]]*len(MatchReference))
    MatchReference.insert(MatchReference.columns.tolist().index('timestamp'), 'matchDate', pd.to_datetime(MatchReference.timestamp, unit="ms", errors="ignore").dt.date)
#     MatchReference.drop(['role','lane'], axis=1, inplace=True)
    MatchReference.reset_index(drop=True, inplace=True)

    Match, ParticipantIdentity, TeamStats, Participant = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    MatchTimeline, MatchFrame, MatchParticipantFrame, MatchEvent = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    positionData = pd.DataFrame()
    for gameIdx in range(len(MatchReference)):
        # lane 정보 수정하기
        # MatchTemp 결과값 수집
        MatchTemp, ParticipantIdentityTemp, TeamStatsTemp, ParticipantTemp = lol.matchResult(apikey, MatchReference.loc[gameIdx, "gameId"])
        MatchTimelineTemp, MatchFrameTemp, MatchParticipantFrameTemp, MatchEventTemp = lol.matchTimeline(apikey, MatchReference.loc[gameIdx, "gameId"])
        ParticipantTemp.insert(3, "laneEdit", None) # lane 정보 수정하기
        """
        Process 1: official
        """
        ParticipantTemp.loc[(ParticipantTemp.role == "SOLO") & (ParticipantTemp.lane == "TOP"), "laneEdit"] = "TOP"
        ParticipantTemp.loc[(ParticipantTemp.role == "SOLO") & (ParticipantTemp.lane == "MIDDLE"), "laneEdit"] = "MIDDLE"
        ParticipantTemp.loc[(ParticipantTemp.role == "NONE") & (ParticipantTemp.lane == "JUNGLE"), "laneEdit"] = "JUNGLE"
        ParticipantTemp.loc[(ParticipantTemp.role == "DUO_CARRY") & (ParticipantTemp.lane == "BOTTOM"), "laneEdit"] = "BOTTOM"
        ParticipantTemp.loc[(ParticipantTemp.role == "DUO_SUPPORT") & (ParticipantTemp.lane == "BOTTOM"), "laneEdit"] = "SUPOORT"
        """
        Process 2:
        Jungle Lane
        1) 강타, 첫 구매템(잉걸불 칼:1035, 빗발칼날:1039)
        2) 2명 이상인 경우, 정글 미니언 갯수
        Support Lane
        1) 돈템(주문도둑의 검:3850, 영혼의 낫, 고대유물 방패, 강철 어깨 보호대) 구매 여부 확인
        2) 만에 하나 안 샀을 경우, 미니언이 가장 적은 사람
        """
        ## Jungle
        jungleItemId = itemInfoDto.loc[itemInfoDto.name.str.contains("잉걸불 칼|빗발칼날"), "itemId"]
        participantId = MatchEventTemp.loc[(MatchEventTemp.type == 'ITEM_PURCHASED') & (MatchEventTemp.itemId.isin(jungleItemId)), "participantId"]  # jungle item 구매한 participant Id
        ParticipantTemp.loc[ParticipantTemp.laneEdit == "JUNGLE", "laneEdit"] = None
        ParticipantTemp.loc[((ParticipantTemp.spell1Id == 11) | (ParticipantTemp.spell2Id == 11)) & ParticipantTemp.participantId.isin(participantId), "laneEdit"] = "JUNGLE"
        if sum(ParticipantTemp.laneEdit == "JUNGLE") != 2:
            jungleIndex = (
                ParticipantTemp.loc[ParticipantTemp.laneEdit == "JUNGLE", ["neutralMinionsKilled", "teamId"]]
                .groupby(by=["teamId"])
                .idxmax()["neutralMinionsKilled"]
            )
            jungleParticipantId = ParticipantTemp.loc[jungleIndex, "participantId"]
            ParticipantTemp.loc[(ParticipantTemp.laneEdit == "JUNGLE"), "laneEdit"] = None
            ParticipantTemp.loc[ParticipantTemp.participantId.isin(ParticipantTemp.loc[jungleIndex, "participantId"]), "laneEdit"] = "JUNGLE"
        ## Support
        supportItemId = itemInfoDto.loc[itemInfoDto.name.str.contains("주문도둑의 검|영혼의 낫|고대유물 방패|강철 어깨 보호대"), "itemId"]
        participantId = MatchEventTemp.loc[(MatchEventTemp.type == 'ITEM_PURCHASED') & (MatchEventTemp.itemId.isin(supportItemId)), "participantId"]  # support item 구매한 participant Id
        ParticipantTemp.loc[ParticipantTemp.laneEdit == "SUPPORT", "laneEdit"] = None
        ParticipantTemp.loc[ParticipantTemp.participantId.isin(participantId), "laneEdit"] = "SUPPORT"
        if sum(ParticipantTemp.laneEdit == "SUPPORT") != 2:
            supportDf = ParticipantTemp.loc[ParticipantTemp.laneEdit == "SUPPORT", :].copy()
            supportDf.loc[:, "totalMinionsKilledSum"] = supportDf.loc[:, "totalMinionsKilled"] + supportDf.loc[:, "neutralMinionsKilled"]
            supportIndex = (
                supportDf.loc[:, ["totalMinionsKilled", "teamId"]]
                .groupby(by=["teamId"])
                .idxmin()["totalMinionsKilled"]
            )
            supportParticipantId = ParticipantTemp.loc[supportIndex, "participantId"]
            ParticipantTemp.loc[(ParticipantTemp.laneEdit == "SUPPORT"), "laneEdit"] = None
            ParticipantTemp.loc[ParticipantTemp.participantId.isin(ParticipantTemp.loc[supportIndex, "participantId"]), "laneEdit"] = "SUPPORT"

        '''
        Procces 3:
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
        MatchParticipantFrameTemp.loc[:, ["position_xEdit"]] = scaler.transform(MatchParticipantFrameTemp.loc[:, ["position_x"]])
        scaler.fit(yRange)
        MatchParticipantFrameTemp.loc[:, ["position_yEdit"]] = scaler.transform(MatchParticipantFrameTemp.loc[:, ["position_y"]])
        # 0 ~ 10분 데이터 추출
        positionDataTemp = (
            MatchParticipantFrameTemp.loc[:, ["participantId", "position_xEdit", "position_yEdit"]]
            .groupby(by=["participantId"])
            .head(10)
            .copy()
        )
        # 0 ~ 10분 좌표를 추적하여 Lane 지정
        positionDataTemp.loc[
            ((positionDataTemp.position_xEdit >= 10)& (positionDataTemp.position_xEdit <= 70)
            & (positionDataTemp.position_yEdit >= 200)& (positionDataTemp.position_yEdit <= 340)) |
            ((positionDataTemp.position_xEdit >= 10)& (positionDataTemp.position_xEdit <= 170)
            & (positionDataTemp.position_yEdit >= 340)& (positionDataTemp.position_yEdit <= 500)) |
            ((positionDataTemp.position_xEdit >= 170)& (positionDataTemp.position_xEdit <= 310)
            & (positionDataTemp.position_yEdit >= 440)& (positionDataTemp.position_yEdit <= 500))
            ,"TOP",
        ]: int = 1
        positionDataTemp.loc[
            (positionDataTemp.position_xEdit >= 176)& (positionDataTemp.position_xEdit <= 336)
            & (positionDataTemp.position_yEdit >= 176)& (positionDataTemp.position_yEdit <= 336),
            "MIDDLE",
        ]: int = 1
        positionDataTemp.loc[
            ((positionDataTemp.position_xEdit >= 200)& (positionDataTemp.position_xEdit <= 340)
            & (positionDataTemp.position_yEdit >= 10)& (positionDataTemp.position_yEdit <= 70)) |
            ((positionDataTemp.position_xEdit >= 340)& (positionDataTemp.position_xEdit <= 500)
            & (positionDataTemp.position_yEdit >= 10)& (positionDataTemp.position_yEdit <= 170)) |
            ((positionDataTemp.position_xEdit >= 440)& (positionDataTemp.position_xEdit <= 500)
            & (positionDataTemp.position_yEdit >= 170)& (positionDataTemp.position_yEdit <= 310)),
            "BOTTOM",
        ]: int = 1
        positionDataGroup = positionDataTemp.groupby(by="participantId").sum().reset_index(drop=False)
        positionDataGroup["laneEdit"] = positionDataGroup[["TOP", "MIDDLE", "BOTTOM"]].idxmax(axis=1)
        positionDataGroup.loc[positionDataGroup[['TOP', 'MIDDLE', 'BOTTOM']].sum(axis=1) == 0, 'laneEdit'] = None
        positionDataTemp = pd.merge(positionDataTemp, positionDataGroup[["participantId", "laneEdit"]], how="left", on="participantId")
        positionDataTemp = pd.merge(positionDataTemp, ParticipantTemp[["participantId", "teamId"]], how="left", on="participantId")

        for pId in ParticipantTemp.loc[-ParticipantTemp.laneEdit.isin(["JUNGLE", "SUPPORT"]), "participantId"]:
            ParticipantTemp.loc[ParticipantTemp.participantId == pId, "laneEdit"] = positionDataTemp.loc[positionDataTemp.participantId == pId, "laneEdit"].unique()
        positionDataTemp = pd.merge(
            positionDataTemp.drop("laneEdit", axis=1),
            ParticipantTemp[["participantId", "laneEdit"]],
            how="left",
            on="participantId",
        )
        positionDataTemp.insert(0, 'gameId', MatchReference.loc[gameIdx, "gameId"])
        
        Match = pd.concat([Match, MatchTemp] , axis=0, ignore_index=True)
        ParticipantIdentity = pd.concat([ParticipantIdentity, ParticipantIdentityTemp] , axis=0, ignore_index=True)
        TeamStats = pd.concat([TeamStats, TeamStatsTemp] , axis=0, ignore_index=True)
        Participant = pd.concat([Participant, ParticipantTemp] , axis=0, ignore_index=True)
        MatchTimeline = pd.concat([MatchTimeline, MatchTimelineTemp] , axis=0, ignore_index=True)
        MatchFrame = pd.concat([MatchFrame, MatchFrameTemp] , axis=0, ignore_index=True)
        MatchParticipantFrame = pd.concat([MatchParticipantFrame, MatchParticipantFrameTemp] , axis=0, ignore_index=True)
        MatchEvent = pd.concat([MatchEvent, MatchEventTemp] , axis=0, ignore_index=True)
        positionData = pd.concat([positionData, positionDataTemp] , axis=0, ignore_index=True)
    MatchReference = pd.merge(MatchReference, Participant[["gameId","championId","laneEdit"]].rename(columns={"championId":"champion"}), how="left", on=["gameId","champion"])
        
    return Matchlist, MatchReference, Match, ParticipantIdentity, TeamStats, Participant, MatchTimeline, MatchFrame, MatchParticipantFrame, MatchEvent

def toCsv(data, directory, nameList):
    dataEdit = data.copy()
    nameEdit = pd.merge(data[['laneEdit','championId']], champInfoDto[['key','name']], how='left', left_on='championId', right_on='key')
    dataEdit['championId'] = nameEdit['name']
    # opponent가 존재하는 경우
    if dataEdit.columns.str.contains('championIdOpp').sum() >= 1:
        nameEdit2 = pd.merge(dataEdit[['laneEdit','championIdOpp']], champInfoDto[['key','name']], how='left', left_on='championIdOpp', right_on='key')
        dataEdit['championIdOpp'] = nameEdit2['name']
    # spell 관련 column이 있는 경우
    if dataEdit.columns.str.contains('spell').sum() >= 1:
        spell1Edit = pd.merge(dataEdit[['spell1Id']], spellInfoDto[['key','name']], how='left', left_on='spell1Id', right_on='key')
        spell2Edit = pd.merge(dataEdit[['spell2Id']], spellInfoDto[['key','name']], how='left', left_on='spell2Id', right_on='key')
        dataEdit['spell1Id'] = spell1Edit['name']
        dataEdit['spell2Id'] = spell2Edit['name']
    # rune 관련 column이 있는 경우
    if dataEdit.columns.str.contains('perk').sum() >= 1:
        perk0Edit = pd.merge(dataEdit[['perk0']], runeInfoDto[['id','name']], how='left', left_on='perk0', right_on='id')
        perk1Edit = pd.merge(dataEdit[['perk1']], runeInfoDto[['id','name']], how='left', left_on='perk1', right_on='id')
        perk2Edit = pd.merge(dataEdit[['perk2']], runeInfoDto[['id','name']], how='left', left_on='perk2', right_on='id')
        perk3Edit = pd.merge(dataEdit[['perk3']], runeInfoDto[['id','name']], how='left', left_on='perk3', right_on='id')
        perk4Edit = pd.merge(dataEdit[['perk4']], runeInfoDto[['id','name']], how='left', left_on='perk4', right_on='id')
        perk5Edit = pd.merge(dataEdit[['perk5']], runeInfoDto[['id','name']], how='left', left_on='perk5', right_on='id')
#         statPerk0Edit = pd.merge(dataEdit[['statPerk0']], runeInfoDto[['id','name']], how='left', left_on='statPerk0', right_on='id')
#         statPerk1Edit = pd.merge(dataEdit[['statPerk1']], runeInfoDto[['id','name']], how='left', left_on='statPerk1', right_on='id')
#         statPerk2Edit = pd.merge(dataEdit[['statPerk2']], runeInfoDto[['id','name']], how='left', left_on='statPerk2', right_on='id')
        dataEdit['perk0'] = perk0Edit['name']
        dataEdit['perk1'] = perk1Edit['name']
        dataEdit['perk2'] = perk2Edit['name']
        dataEdit['perk3'] = perk3Edit['name']
        dataEdit['perk4'] = perk4Edit['name']
        dataEdit['perk5'] = perk5Edit['name']
#         dataEdit['statPerk0'] = statPerk0Edit['name']
#         dataEdit['statPerk1'] = statPerk1Edit['name']
#         dataEdit['statPerk2'] = statPerk2Edit['name']
    # item 관련 column이 있는 경우
    if dataEdit.columns.str.contains(r'itemId|item\d+$').sum() >=1 :
        for colname in dataEdit.columns[dataEdit.columns.str.contains(r'itemId|item\d+$')]:
            itemEdit = pd.merge(dataEdit[colname], itemInfoDto[['itemId','name']], how='left', left_on=colname, right_on='itemId')
            dataEdit[colname] = itemEdit['name']
    
#     # float formatting
    name = [x for x in nameList if nameList[x] is data][0]
    formatJson['outputFormat'][name.replace('Dto','Format')].items()
    for key, value in formatJson['outputFormat'][name.replace('Dto','Format')].items():
        # dataEdit[key] = dataEdit[key].apply(value.format) # data format으로 자리 수 지정이 안됨...
        dataEdit[key] = dataEdit[key].round(4)
        dataEdit[key] = dataEdit[key].astype('string')
        dataEdit[key] = dataEdit[key].str.rstrip('0')
        dataEdit[key] = dataEdit[key].str.rstrip('.')
        
    dataEdit.to_csv(directory, index=False, encoding='utf-8-sig')