import re
from bs4 import BeautifulSoup
import requests
import time
import json
import sqlite3
import os

from ImgUtils import download_image_to_jpg
from constant import ONE_RANK_IMG, rank_item

# 目标 UP 主 UID
UP_UID = "549739"  # 替换成你要监控的 UP 主 UID

# B 站获取动态的 API
API_URL = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/feed/space?host_mid={UP_UID}&page=1&offset=&type=all"

db_path = os.path.join(os.getcwd(), "pcr.db")

db_dir = os.path.dirname(db_path)

conn = None
cursor = None

# 记录最新的动态 ID
latest_dynamic_id = None


def initConn():
    global conn, cursor  # 声明全局变量
    if conn is None:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()  # 这里需要使用全局的 cursor


def getRankImgByTitleId(titleId):
    initConn()
    cursor.execute("SELECT COUNT(*) FROM pcr_rank_img WHERE title_id = ?", (titleId,))
    result = cursor.fetchone()
    closeConn()
    return result[0]


def closeConn():
    global conn, cursor  # 声明全局变量
    if cursor:
        cursor.close()
        cursor = None
    if conn:
        conn.close()
        conn = None


def saveRankImg(data):
    initConn()
    deleteRankImg()
    ## 保存新的数据之前先清空之前旧的数据
    cursor.executemany("insert INTO pcr_rank_img (title,img_url,title_id,web_title) values (?,?,?,?)", (data))
    # 提交事务
    conn.commit()
    # 关闭连接
    conn.close()


def deleteRankImg():
    cursor.execute("DELETE FROM pcr_rank_img")


def get_latest_dynamic():
    global latest_dynamic_id
    try:
        # 发送请求获取动态数据
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "cookie": "buvid3=AE09648C-CF72-37F5-71FD-F7D77779514B42578infoc; b_nut=1719299642; _uuid=56A8BF15-61B2-1DB2-D847-107110110BF6710D59470infoc; buvid4=479D55A2-9D53-B118-2776-E516BA9E19DC46532-024062507-8/6s5hoxYaFIq/A7T00gkg%3D%3D; buvid_fp_plain=undefined; fingerprint=677795e34848007142a9128dcc51cfa7; SESSDATA=49e21bd3%2C1754360428%2C176b2%2A21CjCkK40Z67u8B0VqBOPfYGsgY8c-Lq0oc2HKHhq_AgAoFTQObu100wXqnpERfmMMT0QSVjRPVjNBenlPb3J2MDI0by1EZWQ2dnhiNjBJcF9KeDNJZUhnSmtpMUYyaXFqUEpERV90NVpCZmYtYmZUR3gzU1l6UmhnQXhXVHZSVVVMY21XRVV0d2N3IIEC; bili_jct=4a49358449b754abde02f1b41a4d1325; DedeUserID=361428452; DedeUserID__ckMd5=531d4a820c52d3f6; buvid_fp=677795e34848007142a9128dcc51cfa7; rpdid=|(JlulYmkYRu0J'u~JmkY|~|u; b_lsid=573A215C_1957E9072A9; bsource=search_google; header_theme_version=CLOSE; enable_web_push=DISABLE; enable_feed_channel=DISABLE; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDE4NDQzNTEsImlhdCI6MTc0MTU4NTA5MSwicGx0IjotMX0.LSfuKi0PXT8gGI6_jWlTbOLMPKXjb1PsiWI53KHIXwY; bili_ticket_expires=1741844291; CURRENT_FNVAL=2000; sid=o8vuu5qb; browser_resolution=1614-150; bp_t_offset_361428452=1042591787706744832"
        }
        response = requests.get(API_URL, headers=headers)
        data = response.json()
        # print(data.get('data'))
        pattern = r"\d{2}[上下]半刷图攻略＆\d{2}-\dRANK表"

        for item in data.get('data').get('items'):
            if re.match(pattern, item.get('content')):
                ## 这边取匹配到的第一个数据即可
                clean_url = item.get('jump_url').lstrip("/")
                response = requests.get("https://" + clean_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                # 查找所有 <img> 标签
                images = soup.find_all('img')
                image_urls = [img['src'] for img in images if img.get('src')]
                regex = r"i0\.hdslb\.com/bfs/new_dyn/[^@]+"
                matchtext = re.match(r"\d+", item.get('content'))
                ### 判断数据库中中是否存在相关数据
                res = getRankImgByTitleId(matchtext.group(0))
                rank_item_set = set()
                if res == 0:
                    i = 0;
                    for url in image_urls:
                        ### 如果没有获取到相同的编号的id就是新的数据保存到数据库中
                        match = re.search(regex, url)
                        if match:
                            ##获取压缩后图片的路径
                            view_url = download_image_to_jpg("https://" + match.group(0))
                            rank_item_set.add((rank_item[i], view_url, matchtext.group(0), item.get('content')))
                            i += 1
                        if i > 3:
                            break
                        ### 匹配到了图片把图片下载到本地
                        # print("https://"+match.group(0))
                        # download_image_to_jpg("https://"+match.group(0))
                break;

        saveRankImg(rank_item_set)
    except Exception as e:
        print("获取动态失败:", str(e))


# 定时检查
def monitor():
    get_latest_dynamic()


if __name__ == "__main__":
    monitor()
