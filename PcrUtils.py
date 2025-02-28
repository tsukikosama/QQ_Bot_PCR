
import os
import uuid
from datetime import datetime ,timedelta
from random import random

import requests
import json
import yaml
import logging
import time
import hashlib


"""
    基本的request请求封装了一些必要的参数
"""


pcrconfig = os.path.join(os.path.dirname(__file__), 'pcrconfig.yaml')

_log = logging.getLogger(__name__)

secret = "mNnGiylYAFXbY0gPy4Zw2nG+dz1t6TYHENz61fxR3Ic="
def read_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

class BaseRequest:
    def __init__(self):
        self.config = read_yaml(pcrconfig)
        self.name = self.config.get('name')
        self.ts = self.config.get('ts')
        self.nonce = self.config.get('nonce')
        self.appkey = self.config.get('appkey')
        self.sign = self.config.get('sign')
        self.params = {
            "name":self.name,
            "ts":self.ts,
            "nonce":self.nonce,
            "appkey":self.appkey,
            "sign":self.sign,
        }
        self.headers = {
            "User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
            'Connection':'keep-alive',
            "Cookie": "buvid3=3673CF0A-1082-6586-C4D6-C6058E39402200310infoc; b_nut=1709792100; _uuid=347D9A24-1AB4-4BEE-B7F7-CFF445DB101010B00392infoc; buvid_fp=3673CF0A-1082-6586-C4D6-C6058E39402200310infoc; buvid4=515D5D26-EDE2-A54D-6A1B-FC5F2DAD287501662-024030706-ldQSR%2BULMIQ6oJCY2Ms1KA%3D%3D; enable_web_push=DISABLE; FEED_LIVE_VERSION=V8; header_theme_version=CLOSE; home_feed_column=4; browser_resolution=450-649; CURRENT_FNVAL=4048; rpdid=|(m~RYRmluk0J'u~u)klm|l~; fingerprint=b701a029553ff3fa8fe52430954ca203; b_lsid=8A72533A_194DE6C0E93; buvid_fp_plain=undefined; SESSDATA=94bf7c9f%2C1754450457%2Cc0849%2A22CjDKOcV9hqXz7xyq9UU9i2FpmNPprTNa-OiPiz-t-bZANMKlDSJcTGmUw2dP3cXDxUQSVnBfR2VXM00tMmF6SkVBQUg4ZEl3WDZwZUFYYzNhSGRaZjBKY3hjbjRCUXhkaXQ3Ml9BbmY2UU5LZE5EbUZfVGVGLXVaeGtWMl9qamRabGVLQ2hvM05nIIEC; bili_jct=e0ef0693192fc5d4cf3da986243c50c2; DedeUserID=361428452; DedeUserID__ckMd5=531d4a820c52d3f6; sid=gdwt2a9y",
            "Bili-Status-Code":"0",
            "X-Bili-Trace-Id":'1b72650df6ab5d64211db1174066b185',
            'X-Ticket-Status':'1',
            'X-Cache-Webcdn':'BYPASS from blzone01',
            'Content-Encoding':'br'
        }
    def fetch_data(self):
        session = requests.Session()
        r = session.get('https://api.game.bilibili.com/game/player/tools/pcr/search_clan', headers=self.headers,
                            params=self.params, allow_redirects=True)
         # 尝试使用 utf-8 解码

        decoded_data = r.content.decode('utf-8', errors='replace')

        # 尝试解析为 JSON
        json_data = json.loads(decoded_data)
        print("JSON 解析成功",json_data)
        return json_data


####发送api的方法
def sendApi(url,param):
    session = requests.Session()
    base = BaseRequest()

    params = {
        "ts": int(time.time() * 1000),
        "nonce": str(uuid.uuid4()),
        "appkey": base.appkey,
    }
    params.update(param)
    # print(params)
    params["sign"] = sign(params)
    r = session.get(url, headers=base.headers,
                    params=params)
    decoded_data = r.content.decode('utf-8', errors='replace')
    json_data = json.loads(decoded_data)
    print("url",r.url)
    print("内容", json_data.get('data'))
    if(json_data.get('code') != 0):
        return 500;
    return json_data.get('data');
###搜索公会排名
def rank(name):
    print("搜索的公会名称",name)
    params = {"name": name}
    decoded_data = sendApi('https://api.game.bilibili.com/game/player/tools/pcr/search_clan',params)
    return decoded_data
##签名
def sign(params):
    sorted_keys = sorted(params.keys())
    query_string = "&".join(f"{key}={params[key]}" for key in sorted_keys)
    # 拼接密钥
    sign_string = query_string + "&secret=" + secret
    # 计算 MD5 签名
    sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    return sign

## 设置如果时间在0-5点之内就返回上一天的时间
def getData():

    current_time = datetime.now()
    today_date = datetime.today().date()
    if 0 <= current_time.hour < 5:
        data = today_date - timedelta(days=1)
    else:
        data = datetime.today().date()
    return  data ;

##查看今日出刀数据
def attactCount():
    params = {
        "date":getData(),

    }
    decoded_data = sendApi('https://api.game.bilibili.com/game/player/tools/pcr/clan_daily_report_by_member', params)

    return decoded_data
def getattactCountByDate(data):
    params = {
        "date" : data,
    }
    decoded_data = sendApi('https://api.game.bilibili.com/game/player/tools/pcr/clan_daily_report_by_member', params)

    return decoded_data
### 获取战斗id
def getBattleId():
    ids =  sendApi("https://api.game.bilibili.com/game/player/tools/pcr/clan_battle_list",{})
    print(ids[0])
    return ids[0].get('id');




def getTodayRank(id):
    # 获取今天日期
    # today = datetime.today().date()
    #
    # # 组合出今天 5 点的 datetime 对象
    # five_am = datetime.combine(today, time(5, 0, 0))
    # # 格式化输出
    # formatted_time = five_am.strftime("%Y-%m-%d %H:%M")

    params = {
        "ranking_time":datetime.today().date().__str__() + " 05:00",
        "battle_id":id
    }

    data = sendApi("https://api.game.bilibili.com/game/player/tools/pcr/my_clan_ranking",params);

    return data;
###搜索rank排名
def getRankByNumber(num):
    params = {
        "rank":num
    }
    data = sendApi("https://api.game.bilibili.com/game/player/tools/pcr/search_clan", params);

    return data;
# if __name__ == "__main__":
#     # s = BaseRequest().fetch_data()
#     # s = test()
#     # print(s.fetch_data())
#     # print(s.get('data',[]))

