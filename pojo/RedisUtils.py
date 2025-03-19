import redis
import json

r = redis.Redis(host='8.138.16.124', port=6379,password='2270398619', decode_responses=True)
## redis key 有效时间 一个小时
VALID_TIME = 60 * 60

## 通过key来获取对应的value
def getValueByKey(key):
    history = json.loads(r.get(key) or "[]")
    return history;

## 保存value
def saveValueByKey(key, value):
    history = getValueByKey(key)
    history.append(value)
    r.set(key, json.dumps(history), ex=VALID_TIME)

def delFailValue(key):
    # 获取历史记录
    history = json.loads(r.get(key) or "[]")
    # 移除最后一条数据
    if history:
        history.pop()  # 移除列表中的最后一个元素

    # 将更新后的历史记录保存回 Redis
    r.set(key, json.dumps(history))

def clearVluae(key):
    deleted_count = r.delete(key)