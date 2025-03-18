import uuid
from urllib import response

import json
import requests

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
    # 如果 session_id 不在 session_data 中，初始化空列表
    if session_id not in session_data:
        session_data[session_id] = []

    # 添加用户的消息到会话历史
    role = {"role": "user", "content": msg}
    session_data[session_id].append(role)

    # 构建请求数据
    data = {
        "model": "deepseek-r1:70b",
        "messages": session_data[session_id],  # 使用 session_id 获取历史消息
        "stream": False
    }

    # 使用 requests 会话发送请求
    session = requests.Session()
    try:
        response = session.post('http://3.21.49.152:8434/api/chat', json=data)
        response.raise_for_status()  # 如果响应状态码不是 200，会抛出异常
        response_json = response.json()  # 获取响应的 JSON 数据
        print(session_data)

        # 返回模型的回答内容
        return response_json.get('message', {}).get('content', 'No response content')

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None  # 如果请求失败，返回 None
