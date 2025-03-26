import redis
import json

from pojo.Constant import QQ_AI_CHAT_CONSTANT, QQ_Ai_STATUS, BOSS_INFO_CONSTANT

r = redis.Redis(host='8.138.16.124', port=6379,password='2270398619', decode_responses=True)
## redis key 有效时间 一个小时
VALID_TIME = 60 * 60 * 24 * 7

## 通过key来获取对应的value
def getValueByKey(key):
    history = json.loads(r.get(QQ_AI_CHAT_CONSTANT+key) or "[]")
    return history;

## 保存value
def saveValueByKey(key, value):
    history = getValueByKey(key)
    history.append(value)
    r.set(QQ_AI_CHAT_CONSTANT+key, json.dumps(history), ex=VALID_TIME)


### 通过key删除value最后一条数据
def delFailValue(key):
    # 获取历史记录
    history = json.loads(r.get(QQ_AI_CHAT_CONSTANT+key) or "[]")
    # 移除最后一条数据
    if history:
        history.pop()  # 移除列表中的最后一个元素

    # 将更新后的历史记录保存回 Redis
    r.set(key, json.dumps(history))

### 通过key清除全部的值
def clearVluae(key):
     r.delete(QQ_AI_CHAT_CONSTANT+key)

## 判断key中是否包含某个值
def isExistValueByKey(key,value):
    if value in r.lrange("PCR_USER",0,-1):
        return True
    return False

def saveList(key,value):
    ## 判断是否存在 如果存在就返回false
    if isExistValueByKey(key,value):
        return False
    r.rpush(key, value)
    return True

def removeValueFromList(key, value):
    # 使用 LREM 删除指定的值
    # 0 表示删除所有匹配的元素，如果只想删除第一个匹配的元素，可以将 0 改为 1
    r.lrem(key, 0, value)

def isExistValue(key,value):
    if value in r.lrange(key,0,-1):
        return True
    return False

def saveBossInfo(key,value):

    r.set(BOSS_INFO_CONSTANT + key, value, ex=VALID_TIME)

def getBossId(id):
    value = r.get(BOSS_INFO_CONSTANT + str(id))
    return value