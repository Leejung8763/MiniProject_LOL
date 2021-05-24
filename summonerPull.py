import argparse
import pandas as pd
import time, datetime
import lolApi
import os, requests
import numpy as np

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

# save 
createFolder(f"/data1/lolData/cgLeague/API_csv/{args.begin.replace('2021','').replace('-','')}")

summonerList.to_csv(f"/data1/lolData/cgLeague/API_csv/{args.begin.replace('2021','').replace('-','')}/summonerList{args.begin.replace('2021','').replace('-','')}.csv", index=False, encoding='utf-8-sig')

print(f"Start: {datetime.datetime.fromtimestamp(startTime)}, End: {datetime.datetime.fromtimestamp(time.time())}, Total: {time.time()-startTime}")