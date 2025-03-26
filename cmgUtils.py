import json
import re
import urllib
from datetime import datetime

import requests

from Conn import saveBoxItem, getHomeWorkName, getBossInfo, clearBossInfo
from pojo.RedisUtils import saveValueByKey, saveBossInfo

params = {
    'lang': 'zh-cn',
    'region': 'cn'  # 可能有效
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Connection": "keep-alive",
    "Host": "www.caimogu.cc",
    "Referer": "https://www.caimogu.cc/gzlj.html",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
    "X-Requested-With": "XMLHttpRequest"
}
url = 'https://www.caimogu.cc/gzlj/data'

url2 = 'https://www.caimogu.cc/gzlj/data/icon'

def getBox_Item():
    response = requests.get(url2, params=params, headers=headers)
    str = urllib.parse.unquote(response.content)
    clearBossInfo()
    jsondata = json.loads(str)
    for item in jsondata.get('data'):
        saveBoxItem(item)
keywords = ["一王", "二王", "三王","四王","五王"]
def getBossId():
    response = requests.get(url, params=params, headers=headers)
    arr = []
    strs = urllib.parse.unquote(response.content)
    jsondata = json.loads(strs)
    for item in jsondata.get('data'):
        arr.append(item.get('id'))
    unique_ids = list(dict.fromkeys(arr))
    for i in range(5):
        saveBossInfo(keywords[i],unique_ids[i])

def getHomeWork(stage,id,flag):
    print(stage,id,flag)
    response = requests.get(url, params=params, headers=headers)
    arr = []
    strs = urllib.parse.unquote(response.content)
    jsondata = json.loads(strs)
    for item in jsondata.get('data'):
        print(item.get('id') , str(id))
        if item.get('id') == str(id):
            for items in item.get('homework'):
                print(items)
                print(item.get('stage') == int(stage),items.get('auto') == int(flag))
                if(item.get('stage') == int(stage) and items.get('auto') == int(flag) ):
                    role = getHomeWorkName(items.get('unit'))
                    damage = items.get('damage')
                    for index,sp in enumerate(items.get('video', [])):
                        title = sp.get('text')
                        urls = sp.get('url')
                        remain=''
                        if(items.get('remain') == 1):
                            remain='--(尾刀)'
                        arr.append({
                            'id': str(items.get('id')) + '-' + str(index),
                            'role': role,
                            'damage': damage,
                            'title': title,
                            'url': urls,
                            'stage':stage,
                            'remain':remain
                        })
    return arr

def getUrlByID(id):

    parts = id.split('-')
    response = requests.get(url, params=params, headers=headers)
    strs = urllib.parse.unquote(response.content)
    jsondata = json.loads(strs)
    for item in jsondata.get('data'):
        for items in item.get('homework'):
            if(items.get('id')== int(parts[0])):
                match = re.search(r"BV\w+",items.get('video')[int(parts[1])].get('url'))
                if match:
                    bv_number = match.group()
    return bv_number;
        # for data in item:
        #     print(data)
def get_sn_type(sn):
    """判断 sn 是 'et'、'ew' 还是 'e' 类型"""
    if sn.startswith("et"):
        return 1
    elif sn.startswith("ew"):
        return 2
    elif sn.startswith("e"):
        return 3
    else:
        return "未知类型"
if __name__ == '__main__':
     getBossId()

    # getBox_Item()