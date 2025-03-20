import json
import urllib

import requests

from Conn import saveBoxItem

params = {
    'date': '2025-02',
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
    jsondata = json.loads(str)
    for item in jsondata.get('data'):
        saveBoxItem(item)