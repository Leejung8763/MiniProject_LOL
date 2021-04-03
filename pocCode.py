import pandas as pd
import time, datetime
import pocLoLapi as lol
import pocModule as poc
import requests, json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

###########
# API Key #
###########
with open("/home/lj/git/KTRolster/APIData/product_keys.txt") as f:
    lines = f.readlines()
apikey = lines[0].replace("\n", "")

#############
# Data Type #
#############
with open('/home/lj/git/KTRolster/RefData/formatJson.json', "r") as loadfile:
    formatJson = json.load(loadfile)
    
########################
# ddragon Data Loading #
########################
# version data 확인
verRequest = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
current_version = verRequest.json()[0]
# Champion Info DataFrame
champRequest = requests.get(
    f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/champion.json"
)
champInfo = pd.DataFrame(champRequest.json())
champInfoDto = (pd.DataFrame(dict(champInfo["data"])).T).reset_index(drop=False)
champInfoDto = champInfoDto.astype(formatJson['referenceDtype']['champInfoDtype'])
# Champion Info DataFrame
itemRequest = requests.get(
    f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/item.json"
)
itemInfoDto = pd.DataFrame(itemRequest.json()["data"]).T
itemInfoDto.reset_index(drop=False, inplace=True)
itemInfoDto.rename(columns={"index": "itemId"}, inplace=True)
itemInfoDto = itemInfoDto.astype(formatJson['referenceDtype']['itemInfoDtype'])
# Spell Info DataFrame
spellRequest = requests.get(
    f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/summoner.json"
)
spellInfo = pd.DataFrame(spellRequest.json())
spellInfoDto = pd.concat([spellInfo, pd.DataFrame(dict(spellInfo["data"])).T], axis=1)
spellInfoDto = spellInfoDto.drop(["data"], axis=1)
spellInfoDto = spellInfoDto.reset_index(drop=True)
spellInfoDto = spellInfoDto.astype(formatJson['referenceDtype']['spellInfoDtype'])
# Summoner's Rift DataFrame
mapUrl = f"https://ddragon.leagueoflegends.com/cdn/10.18.1/img/map/map11.png"
lolMap = plt.imread(mapUrl)
# Rune Info DataFrame
runeRequest = requests.get(
    f"http://ddragon.leagueoflegends.com/cdn/{current_version}/data/ko_KR/runesReforged.json"
)
runeInfoDto = pd.DataFrame(runeRequest.json())
perk0 = pd.DataFrame(dict(runeInfoDto["slots"]))
runeInfoDto.drop("slots", axis=1, inplace=True)
for col0 in perk0.columns:
    perk1 = pd.DataFrame(dict(perk0[col0]))
    for col1 in perk1.columns:
        perk2 = pd.DataFrame(dict(perk1[col1])).T
        for col2 in perk2.columns:
            perk3 = pd.DataFrame(dict(perk2[col2])).T
            runeInfoDto = pd.concat([runeInfoDto, perk3], axis=0, ignore_index=True)
runeRequest2 = requests.get(
    f"http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
)
runeInfoDto2 = pd.DataFrame(runeRequest2.json())
runeInfoDto2 = (
    runeInfoDto2[runeInfoDto2.id < 6000]
    .rename(columns={"name": "key", "iconPath": "icon"})
    .drop(["majorChangePatchVersion", "tooltip", "endOfGameStatDescs"], axis=1)
)
runeInfoDto2["name"] = [
    "마법 저항력 +8",
    "방어력 +6",
    "적응형 능력치 +9",
    "체력 +10~90 (레벨에 비례)",
    "재사용 대기시간 감소 +1~10% (레벨에 비례)",
    "공격 속도 +10%",
]
runeInfoDto = pd.concat([runeInfoDto, runeInfoDto2])
runeInfoDto = runeInfoDto.astype(formatJson['referenceDtype']['runeInfoDtype'])
# Item Info DataFrame
itemList = pd.read_csv("/home/lj/git/KTRolster/RefData/itemlist.csv")
itemList = itemList.astype(formatJson['referenceDtype']['itemListDtype'])
legendaryItem = itemList.loc[itemList.category == "전설", "name_Kor"].tolist()
legendaryItem = itemInfoDto[itemInfoDto.name.isin(legendaryItem)].copy()
mythicItem = itemList.loc[itemList.category == "신화", "name_Kor"].tolist()
mythicItem = itemInfoDto[itemInfoDto.name.isin(mythicItem)].copy()

####################
# API Data Loading # 
####################
MatchReference, ParticipantIdentity, Participant, MatchParticipantFrame, MatchEvent = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
for summoner in ["어리고싶다","liiiiliiiiiill"]:
    MatchlistTmp, MatchReferenceTmp, MatchTmp, ParticipantIdentityTmp, TeamStatsTmp, ParticipantTmp, MatchTimelineTmp, MatchFrameTmp, MatchParticipantFrameTmp, MatchEventTmp = poc.laneEdit(apikey, summoner, "2021-02-03 00:00:00", "2021-02-18 00:00:00")
    MatchReference = pd.concat([MatchReference, MatchReferenceTmp], ignore_index=True)
    ParticipantIdentity = pd.concat([ParticipantIdentity, ParticipantIdentityTmp], ignore_index=True)
    Participant = pd.concat([Participant, ParticipantTmp], ignore_index=True)
    MatchParticipantFrame = pd.concat([MatchParticipantFrame, MatchParticipantFrameTmp], ignore_index=True)
    MatchEvent = pd.concat([MatchEvent, MatchEventTmp], ignore_index=True)

# Changing Dtype
MatchReference = MatchReference.astype(formatJson['inputDtype']['MatchReferenceDtype'])
ParticipantIdentity = ParticipantIdentity.astype(formatJson['inputDtype']['ParticipantIdentityDtype'])
Participant = Participant.astype(formatJson['inputDtype']['ParticipantDtype'])
MatchParticipantFrame = MatchParticipantFrame.astype(formatJson['inputDtype']['MatchParticipantFrameDtype'])
MatchEvent = MatchEvent.astype(formatJson['inputDtype']['MatchEventDtype'])
# saving Data
MatchReference.to_csv("/home/lj/git/KTRolster/APIData/MatchReference.csv", index=False, encoding="utf-8-sig", )
ParticipantIdentity.to_csv("/home/lj/git/KTRolster/APIData/ParticipantIdentity.csv", index=False, encoding="utf-8-sig")
Participant.to_csv("/home/lj/git/KTRolster/APIData/Participant.csv", index=False, encoding="utf-8-sig")
MatchParticipantFrame.to_csv("/home/lj/git/KTRolster/APIData/MatchParticipantFrame.csv", index=False, encoding="utf-8-sig")
MatchEvent.to_csv("/home/lj/git/KTRolster/APIData/MatchEvent.csv", index=False, encoding="utf-8-sig")

############################
# Creating & Saving Output #
############################
# Creating Data
specificSummonerId = ParticipantIdentity.loc[
    ParticipantIdentity.accountId.isin(["4JPUF_1QjMTx1CyWQ4nVyk278N5iMSnV9AnlbFCWcF6-lhKogzsz7YUF", "gxsNkvhW4I7y8UDgEtrhNUXskkH8m5zy9z-Hu5f_8UM8xsc"]),
    ["gameId", "participantId"]
]
specificSummonerDto = pd.merge(
    Participant, 
    specificSummonerId, 
    how="inner", 
    on=["gameId", "participantId"]
)
for window in [10, 15, 20, 25, 30]:
    tmp = MatchParticipantFrame[
        (MatchParticipantFrame.timestamp >= window * 60 * 1000 - 10000)
        & (MatchParticipantFrame.timestamp <= window * 60 * 1000 + 10000)
    ]
    tmp = tmp[["gameId", "participantId", "totalGold", "xp", "minionsKilled", "jungleMinionsKilled"]]
    tmp[["totalGold", "xp", "minionsKilled", "jungleMinionsKilled"]] = tmp[["totalGold", "xp", "minionsKilled", "jungleMinionsKilled"]].astype(int)
    specificSummonerDto = pd.merge(
        specificSummonerDto, 
        tmp, 
        how="left", 
        on=["gameId", "participantId"]
    )
    specificSummonerDto.rename(
        columns={
            "totalGold": f"totalGold{window}",
            "xp": f"xp{window}",
            "minionsKilled": f"minionsKilled{window}",
            "jungleMinionsKilled": f"jungleMinionsKilled{window}"
        },
        inplace=True,
    )
specificSummonerId = set(
    zip(specificSummonerId.gameId, specificSummonerId.participantId)
)
specificLaneSummonerDto = pd.merge(
    Participant,
    specificSummonerDto[["gameId", "laneEdit"]],
    how="inner",
    on=["gameId", "laneEdit"],
)
specificLaneSummonerId = set(
    zip(specificLaneSummonerDto.gameId, specificLaneSummonerDto.participantId)
)
opponentSummonerId = specificLaneSummonerId - specificSummonerId
opponentSummonerDto = pd.merge(
    Participant,
    pd.DataFrame(opponentSummonerId, columns=["gameId", "participantId"]),
    how="inner",
    on=["gameId", "participantId"],
)
for window in [10, 15, 20, 25, 30]:
    tmp = MatchParticipantFrame[
        (MatchParticipantFrame.timestamp >= window * 60 * 1000 - 10000)
        & (MatchParticipantFrame.timestamp <= window * 60 * 1000 + 10000)
    ]
    tmp = tmp[["gameId", "participantId", "totalGold", "xp", "minionsKilled", "jungleMinionsKilled"]]
    tmp[["totalGold", "xp", "minionsKilled", "jungleMinionsKilled"]] = tmp[["totalGold", "xp", "minionsKilled", "jungleMinionsKilled"]].astype(int)
    opponentSummonerDto = pd.merge(
        opponentSummonerDto, 
        tmp, 
        how="left", 
        on=["gameId", "participantId"]
    )
    opponentSummonerDto.rename(
        columns={
            "totalGold": f"totalGold{window}",
            "xp": f"xp{window}",
            "minionsKilled": f"minionsKilled{window}",
            "jungleMinionsKilled": f"jungleMinionsKilled{window}",
        },
        inplace=True,
    )
vsDto = pd.merge(
    specificSummonerDto,
    opponentSummonerDto,
    how="left",
    on=["gameId", "laneEdit"],
    suffixes=("", "Opp"),
)
for i in ["totalGold10","xp10","minionsKilled10","jungleMinionsKilled10","totalGold15","xp15","minionsKilled15","jungleMinionsKilled15","totalGold20","xp20","minionsKilled20","jungleMinionsKilled20","totalGold25","xp25","minionsKilled25","jungleMinionsKilled25","totalGold30","xp30","minionsKilled30","jungleMinionsKilled30"]:
    vsDto[f"{i}Diff"] = vsDto[i] - vsDto[f"{i}Opp"]
    vsDto[f"{i}Sup"] = vsDto[i] - vsDto[f"{i}Opp"] > 0

# Output 1-1
champLaneGroupDto = vsDto.groupby(["laneEdit", "championId"]).agg(
    winRate=("win", "mean"), champCount=("championId", "count")
)
champLaneGroupDto.winRate = champLaneGroupDto.winRate * 100
champLaneCountDto = champLaneGroupDto.reset_index(drop=False).copy()
champLanePerDto = (
    (
        champLaneGroupDto.champCount
        / champLaneGroupDto.groupby("laneEdit").agg(champProp=("champCount", "sum")).champProp
        * 100
    )
    .reset_index(drop=False)
    .copy()
)
champLanePerDto.rename(
    columns={
        0: "champProp"
    }, inplace=True
)
champLaneDto = pd.merge(
    champLaneCountDto, 
    champLanePerDto, 
    how="left",
    on=["laneEdit", "championId"]
)
champLaneDto.sort_values(
    by=["champCount"], inplace=True, ascending=False, ignore_index=True
)

varList = ["laneEdit", "championId",
           "win", "champLevel", "kills", "deaths", "assists", "largestKillingSpree", "largestMultiKill", "firstBloodKill", "firstBloodAssist", "firstTowerKill", "firstTowerAssist", "firstInhibitorKill", "firstInhibitorAssist", "killingSprees", "doubleKills", "tripleKills", "quadraKills", "pentaKills", "turretKills", "inhibitorKills", "longestTimeSpentLiving", "totalTimeCrowdControlDealt", "timeCCingOthers", 
           "totalDamageDealtToChampions", "physicalDamageDealtToChampions", "magicDamageDealtToChampions", "trueDamageDealtToChampions", "totalDamageDealt", "magicDamageDealt", "physicalDamageDealt", "trueDamageDealt", "largestCriticalStrike", "damageDealtToObjectives", "damageDealtToTurrets", 
           "totalHeal", "totalUnitsHealed", "damageSelfMitigated", "totalDamageTaken", "physicalDamageTaken", "magicalDamageTaken", "trueDamageTaken", 
           "visionScore", "wardsPlaced", "wardsKilled", "visionWardsBoughtInGame", "sightWardsBoughtInGame", 
           "goldEarned", "goldSpent", "totalMinionsKilled", "neutralMinionsKilled", "neutralMinionsKilledTeamJungle", "neutralMinionsKilledEnemyJungle"]
varListVs = varList + [x+"Opp" for x in varList[1:]] + ["totalGold10Diff","xp10Diff","minionsKilled10Diff","jungleMinionsKilled10Diff","totalGold15Diff","xp15Diff","minionsKilled15Diff","jungleMinionsKilled15Diff","totalGold20Diff","xp20Diff","minionsKilled20Diff","jungleMinionsKilled20Diff","totalGold25Diff","xp25Diff","minionsKilled25Diff","jungleMinionsKilled25Diff","totalGold30Diff","xp30Diff","minionsKilled30Diff","jungleMinionsKilled30Diff"]
varlistDiff = ["totalGold10Diff","xp10Diff","minionsKilled10Diff","jungleMinionsKilled10Diff","totalGold15Diff","xp15Diff","minionsKilled15Diff","jungleMinionsKilled15Diff","totalGold20Diff","xp20Diff","minionsKilled20Diff","jungleMinionsKilled20Diff","totalGold25Diff","xp25Diff","minionsKilled25Diff","jungleMinionsKilled25Diff","totalGold30Diff","xp30Diff","minionsKilled30Diff","jungleMinionsKilled30Diff"]
varListSup = ["totalGold10Sup","xp10Sup","minionsKilled10Sup","jungleMinionsKilled10Sup","totalGold15Sup","xp15Sup","minionsKilled15Sup","jungleMinionsKilled15Sup","totalGold20Sup","xp20Sup","minionsKilled20Sup","jungleMinionsKilled20Sup","totalGold25Sup","xp25Sup","minionsKilled25Sup","jungleMinionsKilled25Sup","totalGold30Sup","xp30Sup","minionsKilled30Sup","jungleMinionsKilled30Sup"]
varList += varlistDiff

champLaneGroupDto = (
    vsDto.loc[:, varList]
    .groupby(["laneEdit", "championId"], as_index=False)
    .mean()
    .drop(["win"], axis=1)
)
champLaneStatsDto = pd.merge(
    champLaneDto, 
    champLaneGroupDto, 
    how="left",
    on=["laneEdit", "championId"]
)

champSupGroupDto = vsDto.loc[:, ["laneEdit", "championId"]+varListSup].groupby(["laneEdit", "championId"], as_index=False).sum()
champSupPerDto = vsDto.loc[:, ["laneEdit", "championId"]+varlistDiff].groupby(["laneEdit", "championId"], as_index=False).count()
champSupPerDto.columns = champSupGroupDto.columns
champSupPerDto = champSupGroupDto.iloc[:,2:].divide(champSupPerDto.iloc[:,2:]) * 100
champSupGroupDto.columns = ["laneEdit", "championId"]+[x+'Count' for x in champSupGroupDto.columns.tolist()[2:]]
champSupPerDto.columns = [x+'Prop' for x in champSupPerDto.columns]
champSupDto = pd.concat([champSupGroupDto, champSupPerDto], axis=1)
champLaneStatsDto = pd.merge(
    champLaneStatsDto[champLaneStatsDto.champCount>=3], 
    champSupDto, 
    how="left",
    on=["laneEdit", "championId"]
)
champLaneStatsDto = champLaneStatsDto.astype(formatJson['outputDtype']['champLaneStatsDtype'])

# Output 1-2
champSpellGroupDto = vsDto.groupby(["laneEdit", "championId", "spell1Id", "spell2Id"]).agg(spellWinRate=("win", "mean"), spellCount=("spell1Id", "count"))
champSpellGroupDto.spellWinRate = champSpellGroupDto.spellWinRate * 100
champSpellCountDto = champSpellGroupDto.reset_index(drop=False).copy()
champSpellPerDto = (
    (
        champSpellGroupDto.spellCount
        / champSpellGroupDto.groupby(["laneEdit", "championId"]).agg(spellProp=("spellCount", "sum")).spellProp
        * 100
    )
    .reset_index(drop=False)
    .copy()
)
champSpellPerDto.rename(columns={0: "spellProp"}, inplace=True)
champSpellDto = pd.merge(
    champSpellCountDto,
    champSpellPerDto,
    how="left",
    on=["laneEdit", "championId", "spell1Id", "spell2Id"],
)
champSpellDto = (
    champSpellDto.sort_values(by="spellCount", ascending=False)
    .groupby(["laneEdit", "championId"])
    .head(3)
)
champSpellDto = pd.merge(
    champLaneDto.loc[champLaneDto.champCount>=3],
    champSpellDto,
    how="left",
    on=["laneEdit", "championId"],
)
champSpellDto = champSpellDto.astype(formatJson['outputDtype']['champSpellDtype'])

# Output 1-3
champRuneDto = vsDto.loc[:, ["laneEdit","championId","win","perk0","perk1","perk2","perk3","perk4","perk5"]]
champRuneGroupDto = champRuneDto.groupby(
    ["laneEdit", "championId", "perk0", "perk1", "perk2", "perk3", "perk4", "perk5"]
).agg(perkWinRate=("win", "mean"), perkCount=("perk0", "count"))
champRuneGroupDto.perkWinRate = champRuneGroupDto.perkWinRate * 100
champRuneCountDto = champRuneGroupDto.reset_index(drop=False).copy()
champRunePerDto = (
    (
        champRuneGroupDto.perkCount
        / champRuneGroupDto.groupby(["laneEdit", "championId"]).agg(perkProp=("perkCount", "sum")).perkProp
        * 100
    )
    .reset_index(drop=False)
    .copy()
)
champRunePerDto.rename(columns={0: "perkProp"}, inplace=True)
champRuneDto = pd.merge(
    champRuneCountDto,
    champRunePerDto,
    how="left",
    on=["laneEdit", "championId", "perk0", "perk1", "perk2", "perk3", "perk4", "perk5"],
)
champRuneDto.sort_values(
    by=["perkCount"], inplace=True, ascending=False, ignore_index=True
)
champRuneDto = pd.merge(
    champLaneDto.loc[champLaneDto.champCount>=3],
    champRuneDto,
    how="left",
    on=["laneEdit", "championId"],
)
champRuneDto = champRuneDto.astype(formatJson['outputDtype']['champRuneDtype'])

# Output 1-4
champMatchEvent = pd.merge(
    MatchEvent,
    vsDto[["gameId", "participantId"]],
    how="inner",
    on=["gameId", "participantId"],
)
champPurchased = champMatchEvent[
    (champMatchEvent.type == "ITEM_PURCHASED")
    & ((champMatchEvent.itemId.isin(legendaryItem.itemId)) | (champMatchEvent.itemId.isin(mythicItem.itemId)))
].copy()

champPurchased_1st = (
    champPurchased.groupby("gameId").head(1).loc[:, ["gameId", "itemId"]]
)
champPurchased_1st = pd.merge(
    vsDto[["gameId", "laneEdit", "championId", "win"]],
    champPurchased_1st,
    how="left",
    on=["gameId"],
)
champPurchasedGroupDto = champPurchased_1st.groupby(
    ["laneEdit", "championId", "itemId"]
).agg(itemWinRate=("win", "mean"), itemCount=("itemId", "count"))
champPurchasedGroupDto.itemWinRate = champPurchasedGroupDto.itemWinRate * 100
champPurchasedCountDto = champPurchasedGroupDto.reset_index(drop=False).copy()
champPurchasedPerDto = (
    (
        champPurchasedGroupDto.itemCount
        / champPurchasedGroupDto.groupby(["laneEdit", "championId"])
        .agg(itemProp=("itemCount", "sum"))
        .itemProp
        * 100
    )
    .reset_index(drop=False)
    .copy()
)
champPurchasedPerDto.rename(
    columns={
        0: "itemProp"
    }, inplace=True
)
champPurchasedDto = pd.merge(
    champPurchasedCountDto,
    champPurchasedPerDto,
    how="left",
    on=["laneEdit", "championId", "itemId"],
)
champPurchasedDto.sort_values(
    by=["itemCount"], inplace=True, ascending=False, ignore_index=True
)
champPurchasedDto = pd.merge(
    champLaneDto.loc[champLaneDto.champCount>=3],
    champPurchasedDto,
    how="left",
    on=["laneEdit", "championId"],
)
champPurchasedDto = champPurchasedDto.astype(formatJson['outputDtype']['champPurchasedDtype'])

# Output 2-1
vsLaneGroupDto = (
    vsDto.loc[:, varListVs]
    .groupby(["laneEdit", "championId", "championIdOpp"])
    .agg(winRateEach=("win", "mean"), champCountEach=("championId", "count"))
)
vsLaneGroupDto.winRateEach = vsLaneGroupDto.winRateEach * 100
vsLaneCountDto = vsLaneGroupDto.reset_index(drop=False).copy()
vsLanePerDto = (
    (
        vsLaneGroupDto.champCountEach
        / vsLaneGroupDto.groupby(["laneEdit", "championId"]).agg(champPropEach=("champCountEach", "sum")).champPropEach
        * 100
    )
    .reset_index(drop=False)
    .copy()
)
vsLanePerDto.rename(
    columns=
    {
        0: "champPropEach"
    }, inplace=True
)
vsLaneDto = pd.merge(
    vsLaneCountDto,
    vsLanePerDto,
    how="left",
    on=["laneEdit", "championId", "championIdOpp"],
)
vsLaneDto.sort_values(
    by="champCountEach", inplace=True, ascending=False, ignore_index=True
)
vsLaneDto = pd.merge(
    champLaneDto,
    vsLaneDto,
    how="left",
    on=["laneEdit", "championId"],
    suffixes=("", "Each"),
)

vsGroupDto = (
    vsDto.loc[:, varListVs]
    .groupby(["laneEdit", "championId", "championIdOpp"], as_index=False)
    .mean()
    .drop(["win","winOpp"], axis=1)
)
vsLaneStatsDto = pd.merge(
    vsLaneDto, 
    vsGroupDto, 
    how="left", 
    on=["laneEdit", "championId", "championIdOpp"]
)

vsSupGroupDto = vsDto.loc[:, ["laneEdit", "championId", "championIdOpp"]+varListSup].groupby(["laneEdit", "championId", "championIdOpp"], as_index=False).sum()
vsSupPerDto = vsDto.loc[:, ["laneEdit", "championId", "championIdOpp"]+varlistDiff].groupby(["laneEdit", "championId", "championIdOpp"], as_index=False).count()
vsSupPerDto.columns = vsSupGroupDto.columns
vsSupPerDto = vsSupGroupDto.iloc[:,3:].divide(vsSupPerDto.iloc[:,3:]) * 100
vsSupGroupDto.columns = ["laneEdit", "championId", "championIdOpp"]+[x+'Count' for x in vsSupGroupDto.columns.tolist()[3:]]
vsSupPerDto.columns = [x+'Prop' for x in vsSupPerDto.columns]
vsSupDto = pd.concat([vsSupGroupDto, vsSupPerDto], axis=1)
vsLaneStatsDto = pd.merge(
    vsLaneStatsDto[vsLaneStatsDto.champCount>=3], 
    vsSupDto, 
    how="left",
    on=["laneEdit", "championId", "championIdOpp"]
)
vsLaneStatsDto = vsLaneStatsDto.astype(formatJson['outputDtype']['vsLaneStatsDtype'])

# Output 2-2
vsSpellGroupDto = vsDto.groupby(
    ["laneEdit", "championId", "championIdOpp", "spell1Id", "spell2Id"]
).agg(spellWinRateEach=("win", "mean"), spellCountEach=("spell1Id", "count"))
vsSpellGroupDto.spellWinRateEach = vsSpellGroupDto.spellWinRateEach * 100
vsSpellCountDto = vsSpellGroupDto.reset_index(drop=False).copy()
vsSpellPerDto = (
    (
        vsSpellGroupDto.spellCountEach
        / vsSpellGroupDto.groupby(["laneEdit", "championId", "championIdOpp"]).agg(spellPropEach=("spellCountEach", "sum")).spellPropEach
        * 100
    )
    .reset_index(drop=False)
    .copy()
)
vsSpellPerDto.rename(
    columns={
        0: "spellPropEach"
    }, inplace=True
)
vsSpellDto = pd.merge(
    vsSpellCountDto,
    vsSpellPerDto,
    how="left",
    on=["laneEdit", "championId", "championIdOpp", "spell1Id", "spell2Id"],
)
vsSpellDto.sort_values(
    by="spellCountEach", inplace=True, ascending=False, ignore_index=True
)
vsSpellDto = pd.merge(
    vsLaneDto[vsLaneDto.champCount>=3], 
    vsSpellDto, 
    how="left",
    on=["laneEdit", "championId", "championIdOpp"]
)
vsSpellDto = vsSpellDto.astype(formatJson['outputDtype']['vsSpellDtype'])

# Output 2-3
vsRuneDto = vsDto.loc[:, ["laneEdit","championId","win","championIdOpp","perk0","perk1","perk2","perk3","perk4","perk5"]]
vsRuneGroupDto = vsRuneDto.groupby(
    ["laneEdit", "championId", "championIdOpp", "perk0", "perk1", "perk2", "perk3", "perk4", "perk5"]
).agg(perkWinRateEach=("win", "mean"), perkCountEach=("perk0", "count"))
vsRuneGroupDto.perkWinRateEach = vsRuneGroupDto.perkWinRateEach * 100
vsRuneCountDto = vsRuneGroupDto.reset_index(drop=False).copy()
vsRunePerDto = (
    (
        vsRuneGroupDto.perkCountEach
        / vsRuneGroupDto.groupby(["laneEdit", "championId", "championIdOpp"])
        .agg(perkPropEach=("perkCountEach", "sum")).perkPropEach
        * 100
    )
    .reset_index(drop=False)
    .copy()
)
vsRunePerDto.rename(columns={0: "perkPropEach"}, inplace=True)
vsRuneDto = pd.merge(
    vsRuneCountDto,
    vsRunePerDto,
    how="left",
    on=["laneEdit", "championId", "championIdOpp", "perk0", "perk1", "perk2", "perk3", "perk4", "perk5"]
)
vsRuneDto.sort_values(
    by=["perkCountEach"], inplace=True, ascending=False, ignore_index=True
)
vsRuneDto = pd.merge(
    vsLaneDto[vsLaneDto.champCount>=3], 
    vsRuneDto, 
    how="left",
    on=["laneEdit", "championId", "championIdOpp"]
)
vsRuneDto = vsRuneDto.astype(formatJson['outputDtype']['vsRuneDtype'])

# Output 2-4
opponentMatchEvent = pd.merge(
    MatchEvent.astype({"participantId": float}),
    pd.DataFrame(opponentSummonerId, columns=["gameId", "participantId"]),
    how="inner",
    on=["gameId", "participantId"],
)
opponentPurchased = opponentMatchEvent[
    (opponentMatchEvent.type == "ITEM_PURCHASED")
    & (
        (opponentMatchEvent.itemId.isin(legendaryItem.itemId)) | (opponentMatchEvent.itemId.isin(mythicItem.itemId))
    )
].copy()
opponentPurchased_1st = (
    opponentPurchased.groupby("gameId").head(1).loc[:, ["gameId", "itemId"]]
)
opponentPurchased_1st = pd.merge(
    opponentSummonerDto[["gameId", "laneEdit", "championId"]],
    opponentPurchased_1st,
    how="left",
    on=["gameId"],
)
vsPurchased_1st = pd.merge(
    champPurchased_1st,
    opponentPurchased_1st,
    how="inner",
    on=["gameId", "laneEdit"],
    suffixes=["", "Opp"],
)
vsPurchasedGroupDto = vsPurchased_1st.groupby(
    ["laneEdit", "championId", "championIdOpp", "itemId"]
).agg(itemWinRateEach=("win", "mean"), itemCountEach=("itemId", "count"))
vsPurchasedGroupDto.itemWinRateEach = vsPurchasedGroupDto.itemWinRateEach * 100
vsPurchasedCountDto = vsPurchasedGroupDto.reset_index(drop=False).copy()
vsPurchasedPerDto = (
    (
        vsPurchasedGroupDto.itemCountEach
        / vsPurchasedGroupDto.groupby(["laneEdit", "championId", "championIdOpp"]).agg(itemPropEach=("itemCountEach", "sum")).itemPropEach
        * 100
    )
    .reset_index(drop=False)
    .copy()
)
vsPurchasedPerDto.rename(columns={0: "itemPropEach"}, inplace=True)
vsPurchasedDto = pd.merge(
    vsPurchasedCountDto,
    vsPurchasedPerDto,
    how="left",
    on=["laneEdit", "championId", "championIdOpp", "itemId"],
)
vsPurchasedDto.sort_values(
    by=["itemCountEach"], inplace=True, ascending=False, ignore_index=True
)
vsPurchasedDto = pd.merge(
    vsLaneDto[vsLaneDto.champCount>=3], 
    vsPurchasedDto, 
    how="left",
    on=["laneEdit", "championId", "championIdOpp"]
)
vsPurchasedDto = vsPurchasedDto.astype(formatJson['outputDtype']['vsPurchasedDtype'])

#################
# Output Saving #
#################
poc.toCsv(champLaneStatsDto, '/home/lj/git/KTRolster/Output/champLaneStatsDto.csv', globals())
poc.toCsv(champSpellDto, '/home/lj/git/KTRolster/Output/champSpellDto.csv', globals())
poc.toCsv(champRuneDto, '/home/lj/git/KTRolster/Output/champRuneDto.csv', globals())
poc.toCsv(champPurchasedDto, '/home/lj/git/KTRolster/Output/champPurchasedDto.csv', globals())
poc.toCsv(vsLaneStatsDto, '/home/lj/git/KTRolster/Output/vsLaneStatsDto.csv', globals())
poc.toCsv(vsSpellDto, '/home/lj/git/KTRolster/Output/vsSpellDto.csv', globals())
poc.toCsv(vsRuneDto, '/home/lj/git/KTRolster/Output/vsRuneDto.csv', globals())
poc.toCsv(vsPurchasedDto, '/home/lj/git/KTRolster/Output/vsPurchasedDto.csv', globals())
