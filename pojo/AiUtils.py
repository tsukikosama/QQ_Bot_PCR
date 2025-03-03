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
