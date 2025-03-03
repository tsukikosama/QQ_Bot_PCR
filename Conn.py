import sqlite3

db_path = "E:/test/test.db"




##初始化建表语句
def initDateBase():
    # 创建 user_tokens 表
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

def bindToken(openId, token):
    initConn();
    cursor.execute("INSERT INTO user_tokens (openid, token) VALUES (?, ?)", (openId, token))
    conn.commit()
    closeConn()

    return cursor.rowcount > 0 if cursor.rowcount else None

def getTokenByOpenId(openId):
    initConn();
    cursor.execute("SELECT token FROM user_tokens WHERE openid = ?", (openId,))
    result = cursor.fetchone()
    conn.commit()
    closeConn()
    return result[0] if result else None

conn = None
cursor = None


def initConn():
    global conn, cursor  # 声明全局变量
    if conn is None:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

def closeConn():
    global conn, cursor
    if cursor:
        cursor.close()
        cursor = None
    if conn:
        conn.close()
        conn = None
