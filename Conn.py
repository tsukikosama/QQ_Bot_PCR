import sqlite3
import os

db_path = os.path.join(os.getcwd(), "pcr.db")

db_dir = os.path.dirname(db_path)


##初始化建表语句
def initDateBase():
    # 创建 user_tokens 表
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增ID
            openid TEXT UNIQUE NOT NULL,           -- 唯一标识
            token TEXT NOT NULL,                   -- 认证令牌
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 记录创建时间
        )
    """)
    # 提交更改
    conn.commit()
    print(f"数据库文件已创建: {db_path}")
# 如果目录不存在，创建该目录

def bindToken(openId, token):
    initConn();
    cursor.execute("SELECT * FROM user_tokens WHERE openid = ?", (openId,))
    result = cursor.fetchone()
    if result:
        cursor.execute("UPDATE user_tokens SET token = ? WHERE openid = ?", (token, openId))
        str = "更新成功"
    else:
        cursor.execute("INSERT INTO user_tokens (openid, token) VALUES (?, ?)", (openId, token))
        str = "绑定成功"
    conn.commit()
    closeConn()

    return str

def getTokenByOpenId(openId):
    initConn();
    cursor.execute("SELECT token FROM user_tokens WHERE openid = ?", (openId,))
    result = cursor.fetchone()
    conn.commit()
    closeConn()
    return result

def updateTokenByOpenId(openId, token):
    initConn();
    cursor.execute("UPDATE user_tokens SET token =? WHERE openid =?", (token, openId))
    if cursor.rowcount > 0 :
        str = "绑定成功"
    else:
        str = "添加数据失败"
    conn.commit()
    closeConn()
    return str

conn = None
cursor = None



def initConn():
    global conn, cursor  # 声明全局变量
    if conn is None:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()  # 这里需要使用全局的 cursor
        ## 获取到了之后更新cookie


def closeConn():
    global conn, cursor  # 声明全局变量
    if cursor:
        cursor.close()
        cursor = None
    if conn:
        conn.close()
        conn = None

########## pcrrank表相关sql

def getRankImgByTitle(title):

    initConn()
    cursor.execute("SELECT * FROM pcr_rank_img WHERE title = ?",(title,))
    result = cursor.fetchone()
    closeConn()
    return result

def getRankImgByTitleId(titleId):
    initConn()
    cursor.execute("SELECT COUNT(*) FROM pcr_rank_img WHERE title_id = ?",(titleId,))
    result = cursor.fetchone()
    closeConn()
    return result[0]



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
    conn.commit()

def saveBoxItem(data):
    initConn()
    cursor.executemany("INSERT OR REPLACE INTO box_item (id, iconValue, iconFilePath) VALUES (:id, :iconValue, :iconFilePath)", data)
    conn.commit()


def delBox():
    initConn()
    cursor.execute("DELETE FROM box_item")
    conn.commit()
    conn.close()

def getBoxIcon(ids):
    initConn()
    if isinstance(ids, int):  # 确保 ids 是一个列表
        ids = [ids]
    query = "SELECT * FROM box_item WHERE id IN ({})".format(",".join("?" * len(ids)))
    cursor.execute(query, ids)
    results = cursor.fetchall()
    return results;


def getHomeWorkName(ids):

    initConn()
    if isinstance(ids, int):  # 确保 ids 是一个列表
        ids = [ids]
    query = "SELECT iconValue FROM box_item WHERE id IN ({})".format(",".join("?" * len(ids)))
    cursor.execute(query, ids)
    results = cursor.fetchall()
    return results;

def getBossInfo():
    initConn()
    query = "SELECT * FROM box_item WHERE id  < 100"
    cursor.execute(query)
    results = cursor.fetchall()
    print(results)
    return results