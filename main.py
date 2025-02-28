import json
import os
import random
import re
import botpy
from botpy import logging

from botpy.ext.cog_yaml import read
from PcrUtils import rank
import PcrUtils


test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()
from botpy.message import GroupMessage, Message
def matchCommod(text):
    ## 获取指令内容
    ##获取指令附带的值
    str = ""
    pattern = r"/([^#]*)\s*#?(.*)"
    pattern2 = r"#([^\s【]+)\s【([^】]+)】"
    match = re.search(pattern, text)
    if match:
        str = "\n"
        if match.group(1).strip() == "当前排名":
            data = rank(match.group(2))
            str += getRankRecord(data);
        elif match.group(1).strip() == "出刀情况":
            data = PcrUtils.attactCount();
            str += getAttack(data);
        elif match.group(1).strip() == "今日排名":
            str += getTodayRank();
        elif match.group(1).strip() == "排名查询":
            data = PcrUtils.getRankByNumber(match.group(2));
            str += getRankRecord(data);
        else:
            str = "匹配失败"
    match2 = re.search(pattern2, text)
    if match2:
        if match2.group(1).strip() == "出刀情况":
            data = PcrUtils.getattactCountByDate(match2.group(2));
            str += getAttack(data)
        if match2.group(1).strip() == "ai":
            data = getChat(match2.group(2))
            str += data;
    return str

def getRankRecord(data):
    str = ""
    if (data == []):
        str = "未查询到当前排名的公会"
    else:
        for item in data:
            str += f"排名{item.get('rank')}的公会:{item.get('clan_name')} 会长:{item.get('leader_name')} 总伤害:{item.get('damage')}\n"
    return str
def getAttack(data):
    if data == []:
        return "公会战还未开启，查询失败"
    str = "";
    killTotal = 0;
    reimburseTotal = 0
    for item in data:
        print(item)
        killCount = 0;
        reimburseCount = 0;
        # rec['name'] = item.get('name')
        for record in item.get('damage_list'):
            killCount += 1;
            reimburseCount += record.get('reimburse')
            # rec['kill'] += record.get('kill')
            # rec['reimburse'] += record.get('reimburse')
            # print(rec,"数据")
        str += f"玩家名:{item.get('name'):<20} 出刀数:{killCount:<2} 补偿刀数:{reimburseCount:<2}\n"
        killTotal += killCount;
        reimburseTotal += reimburseCount;
    str += f"总出刀人数:{len(data):<3} 出刀总数:{killTotal:<3} 补偿刀总数:{reimburseTotal:<3}"
    return str

def getTodayRank():
    ids = PcrUtils.getBattleId();
    todayRank = PcrUtils.getTodayRank(ids);
    str = ""
    if(todayRank.get('clan_name') != None):
        str = f"今日五点 公会:{todayRank.get('clan_name')} 会长:{todayRank.get('leader_name')} 排名{todayRank.get('rank')} 总伤害:{todayRank.get('damage')}"
    else:
        str = f"今日五点 公会:咖啡馆 会长:'未来' 排名:{random.randint(1,1200)} 总伤害:{random.randint(1000000,90000000)}"
    return str
class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 启动成功!")

    async def on_group_at_message_create(self, message: Message):
        # messageResult = await message._api.post_group_message(
        #     group_openid=message.group_openid,
        #     msg_type=0,
        #     msg_id=message.id,
        _log.info({message})
        # _log.info({self.robot.name})

        # _log.info(message.content.strip())
        res = matchCommod(message.content.strip());

        messageResult = await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=res
        )
        # match = re.match(r"^排名#(.+)", message.content.strip())  # 匹配 "排名#" 开头，且后面必须有内容
        # if (match):
        #     data = rank(match.group(1));
        #     messageResult = await message._api.post_group_message(
        #         group_openid=message.group_openid,
        #         msg_type=0,
        #         msg_id=message.id,
        #         content=data
        #     )
        # if
        ##回复消息
        # await message._api.post_group_message(
        #     group_openid=message.group_openid,
        #     msg_type=1,  # 7表示富媒体类型
        #     msg_id=message.id,
        #     media=message.attachments[0].url
        # )
        # message.reply("content:"+message.content +"channel_id"+ message.channel_id+"member"+message.member+"author:"+message.author)
        # _log.info(messageResult)
if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True
    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])

