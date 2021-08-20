import pandas as pd
import numpy as np
import requests, json, urllib
import matplotlib.pyplot as plt
import PIL, time

class Ref:
    def __init__(self):
        while True:
            try:
                # version data 확인
                verRequest = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
                self.current_version = verRequest.json()[0]
                # Champion Info DataFrame
                champRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{self.current_version}/data/ko_KR/champion.json")
                champInfo = pd.DataFrame(champRequest.json())
                self.champInfoDto = (pd.DataFrame(dict(champInfo["data"])).T).reset_index(drop=False)
                self.champInfoDto = self.champInfoDto.astype({"index":"string", "version":"string", "id":"string", "key":"string", "name":"string", "title":"string", "blurb":"string", "info":"string", "image":"string", "tags":"string", "partype":"string", "stats":"string"})
                # Champion Info DataFrame
                itemRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{self.current_version}/data/ko_KR/item.json")
                self.itemInfoDto = pd.DataFrame(itemRequest.json()["data"]).T
                self.itemInfoDto.reset_index(drop=False, inplace=True)
                self.itemInfoDto.rename(columns={"index":"itemId"}, inplace=True)
                self.itemInfoDto = self.itemInfoDto.astype(str)
                # Spell Info DataFrame
                spellRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{self.current_version}/data/ko_KR/summoner.json")
                spellInfo = pd.DataFrame(spellRequest.json())
                self.spellInfoDto = pd.concat([spellInfo, pd.DataFrame(dict(spellInfo["data"])).T], axis=1)
                self.spellInfoDto = self.spellInfoDto.drop(["data"], axis=1)
                self.spellInfoDto = self.spellInfoDto.reset_index(drop=True)
                self.spellInfoDto = self.spellInfoDto.astype({"type":"string", "version":"string", "id":"string", "name":"string", "description":"string", "tooltip":"string", "maxrank":"string", "cooldown":"string", "cooldownBurn":"string", "cost":"string", "costBurn":"string", "datavalues":"string", "effect":"string", "effectBurn":"string", "vars":"string", "key":"string", "summonerLevel":"int8", "modes":"string", "costType":"string", "maxammo":"string", "range":"string", "rangeBurn":"string", "image":"string", "resource":"string"})
                # Summoner"s Rift DataFrame
                mapUrl = f"https://ddragon.leagueoflegends.com/cdn/10.18.1/img/map/map11.png"
                self.lolMap = np.asarray(PIL.Image.open(urllib.request.urlopen(mapUrl)))
                # Rune Info DataFrame
                runeRequest = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{self.current_version}/data/ko_KR/runesReforged.json")
                self.runeInfoDto = pd.DataFrame(runeRequest.json())
                perk0 = pd.DataFrame(dict(self.runeInfoDto["slots"]))
                self.runeInfoDto.drop("slots", axis=1, inplace=True)
                for col0 in perk0.columns:
                    perk1 = pd.DataFrame(dict(perk0[col0]))
                    for col1 in perk1.columns:
                        perk2 = pd.DataFrame(dict(perk1[col1])).T
                        for col2 in perk2.columns:
                            perk3 = pd.DataFrame(dict(perk2[col2])).T
                            self.runeInfoDto = pd.concat([self.runeInfoDto, perk3], axis=0, ignore_index=True)
                runeRequest2 = requests.get(f"http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json")
                runeInfoDto2 = pd.DataFrame(runeRequest2.json())
                runeInfoDto2 = runeInfoDto2[runeInfoDto2.id <6000].rename(columns={"name":"key","iconPath":"icon"}).drop(["majorChangePatchVersion","tooltip","endOfGameStatDescs"], axis=1)
                runeInfoDto2["name"] = ["마법 저항력 +8","방어력 +6","적응형 능력치 +9","체력 +10~90 (레벨에 비례)","재사용 대기시간 감소 +1~10% (레벨에 비례)","공격 속도 +10%"]
                self.runeInfoDto = pd.concat([self.runeInfoDto, runeInfoDto2]) 
                self.runeInfoDto = self.runeInfoDto.astype({"id":"string", "key":"string", "icon":"string", "name":"string", "longDesc":"string", "shortDesc":"string"})
                # format Json 파일
                with open("/home/lj/git/MiniProject_LOL/RefData/formatJsonV3.json", "r") as loadfile:
                    self.formatJson = json.load(loadfile)
                break
            except:
                time.sleep(10)
            
