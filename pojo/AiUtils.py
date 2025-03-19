import uuid
from urllib import response

import json
import requests

from pojo.RedisUtils import getValueByKey, saveValueByKey, delFailValue


def getChat(msg):
    session = requests.Session()
    data = {
            "model":"deepseek-r1:70b",
            "messages":[{"role":"user","content":msg}],
            "stream":False
            }
    response = session.post('http://3.21.49.152:8434/api/chat',json=data)
    print(response.text)
    try:
        data = response.json()  # 使用 .json() 方法直接解析 JSON
        content = data['message']['content']
        print(content)
    except json.JSONDecodeError:
        print("无法解析 JSON 响应")
    except KeyError:
        print("无法找到 'message' 或 'content' 字段")

	
    return content

def get_session_id():
    return str(uuid.uuid4())

# 用于存储每个 session 的上下文数据
session_data = {}

def chatAi(msg, session_id):
    print(msg)

    ##保存本次回复
    saveValueByKey(session_id,{"role": "user", "content": msg})

    ## 获取历史回复
    session_data = getValueByKey(session_id)

    print(session_data)
    # 构建请求数据
    data = {
        "model": "deepseek-r1-70b-16k",
        "messages": session_data,  # 使用 session_id 获取历史消息
        "temperature": 0.1,
        "stream": False
    }

    # 使用 requests 会话发送请求
    session = requests.Session()
    try:
        response = session.post('http://3.21.49.152:8434/api/chat', json=data)
        print(response.text)
        response.raise_for_status()  # 如果响应状态码不是 200，会抛出异常
        response_json = response.json()  # 获取响应的 JSON 数据
        # 获取 AI 回复
        ai_reply = response_json.get('message', {}).get('content', 'No response content')
        ##把ai的回复也保存进来
        saveValueByKey(session_id,response_json.get('message', {}))
        print(session_data ,"当前的历史记录")
        # 返回整个对话历史
        return ai_reply
    except requests.exceptions.RequestException as e:
        ## 移除末尾的一条数据
        delFailValue(session_id)
        return "请求失败"  # 如果请求失败，仍然返回历史消息


