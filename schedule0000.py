import argparse
import time, datetime
import lolApi, dataPull
import os, requests

# 인자값을 받을 수 있느 인스턴스 생성
parser = argparse.ArgumentParser(description='Riot api data pulling')
# parameter default value
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
today  = datetime.datetime.now().date().strftime("%Y%m%d")
# 입력 받을 인자값 등록
parser.add_argument('--begin', required=False, default=yesterday, help='시작일자 작성')
parser.add_argument('--end', required=False, default=today, help='종료일자 작성')
# 입력 받은 인자값을 args에 저장 (type: namespace)
args = parser.parse_args()
# 입력 받은 시작 날짜가 어제가 아닌 경우, 끝 날짜를 다음 날로 지정
if (args.begin != yesterday) & (args.end == today):
    args.end = (datetime.datetime.strptime(args.begin, '%Y%m%d') + datetime.timedelta(1)).strftime("%Y%m%d")

# start tiem check
startTime = time.time()
# load api key
apikey = lolApi.loadKey("/home/lj/git/MiniProject_LOL/APIData/product_keys.txt")
# create folder
savePath = "/data1/lolData/cgLeague/API_csv"
dataPull.createFolder(f"{savePath}/{args.begin[2:]}")
# pulling challenger, grandmaster league summoner list
summonerList = dataPull.summonerPull(apikey)
# save summoner list data
summonerList.to_csv(f"{savePath}/{args.begin[2:]}/summonerList_{args.begin[2:]}.csv", index=False, encoding='utf-8-sig')
print(f"Start: {datetime.datetime.fromtimestamp(startTime)}, End: {datetime.datetime.fromtimestamp(time.time())}, Total: {time.time()-startTime}")