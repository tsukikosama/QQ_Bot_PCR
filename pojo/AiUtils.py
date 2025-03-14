from urllib import response

import requests

def getChat(msg):
    session = requests.Session()
    data = {
            "model":"deepseek-r1:70b",
            "messages":{"role":"user","content":msg},
            "stream":False
            }
    response = session.post('http://3.21.49.152:8434/api/chat',json=data)
    print(response.text)

    return response.text
