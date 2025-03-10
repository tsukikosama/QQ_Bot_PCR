import os
import re
import botpy
from botpy import logging

from botpy.ext.cog_yaml import read

from Conn import getTokenByOpenId, bindToken, updateTokenByOpenId, initDateBase
from ImgUtils import getRandomImgName
from PcrUtils import rank
import PcrUtils


test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()
from botpy.message import GroupMessage, Message
def matchCommod(message: Message):
    text = message.content.strip();
    ## 判断是否是绑定token的指令 如果是 就直接返回 判定和换绑指令
    pat = r"^#(绑定|换绑)【(.*?)】$"
    ma = re.search(pat, text)
    str = ""
    if ma:
        action, token = ma.groups()
        if action == "绑定":
           str +=  bindToken(message.group_openid, token)
        elif action == "换绑":
            str += updateTokenByOpenId(message.group_openid, token)
        return str
    ## 获取指令内容
    ##获取指令附带的值
    pattern = r"/([^#]*)\s*#?(.*)"
    match = re.search(pattern, text)
    ### QQ机器人自带指令 先不动
    if match:
        str = "\n"
        if match.group(1).strip() == "当前排名":
            data = rank(match.group(2))
            str += PcrUtils.getRankRecord(data);
        elif match.group(1).strip() == "出刀情况":
            data = PcrUtils.attactCount();
            str += PcrUtils.getAttack(data);
        elif match.group(1).strip() == "今日排名":
            str += PcrUtils.getTodayRank();
        elif match.group(1).strip() == "排名查询":
            data = PcrUtils.getRankByNumber(match.group(2));
            str += PcrUtils.getRankRecord(data);
        else:
            str = "匹配失败"
    pattern2 = r"^#pcr\s*【\s*(.*?)\s*】$"
    match2 = re.match(pattern2, text)
    ## 判断指令是否是#pcr开头
    if match2:
        ## 判断发送消息的账号是否绑定了token
        user = getTokenByOpenId(message.group_openid)
        print(user ,"是否存在")
        if user is None:
            str += "当前群未绑定token,请重新绑定token后再使用功能"
        else:
            PcrUtils.changeToken(message.author.member_openid)
            ### 出刀情况 【日期】
            if match2.group(1).strip() == "出刀情况":
                data = PcrUtils.getattactCountByDate(match2.group(3));
                str += PcrUtils.getAttack(data)
            elif match2.group(1).strip() == "公会总表":
                data = PcrUtils.getAllAttactCount();
                str += data
            ### 当前排名 【公会名】
            elif match2.group(1).strip() == "当前排名":
                data = rank(match.group(3))
                str += PcrUtils.getRankRecord(data);
            elif match2.group(1).strip() == "今日出刀情况":
                data = PcrUtils.attactCount();
                str += PcrUtils.getAttack(data);
            elif match2.group(1).strip() == "今日排名":
                str += PcrUtils.getTodayRank();
            ### 排名情况 【数字排名】 用处不大
            elif match2.group(1).strip() == "排名查询":
                data = PcrUtils.getRankByNumber(match.group(3));
                str += PcrUtils.getRankRecord(data);
            elif match2.group(1).strip() == "获取图片":
                str += "获取图片"
    ### 旧指令
    # if match2:
    #     if match2.group(1).strip() == "出刀情况":
    #         data = PcrUtils.getattactCountByDate(match2.group(2));
    #         str += PcrUtils.getAttack(data)
    #     if match2.group(1).strip() == "ai":
    #         # data = getChat(match2.group(2))
    #         # str += data;
    #         str += "暂停服务"
    #     if match2.group(1).strip() == "公会总表":
    #         data = PcrUtils.getAllAttactCount();
    #         str += data
    #     if match2.group(1).strip() == "帮助":
    #         str = "帮助文档:"
    return str

class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 启动成功!")

    async def on_group_at_message_create(self, message: Message):
        _log.info({message})
        res = matchCommod(message);
        print(res,"内容")
        if res.strip() == "获取图片":
            imgName = getRandomImgName();
            uploadMedia = await message._api.post_group_file(
                group_openid=message.group_openid,
                file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                url="http://8.138.16.124:8083/upload/"+imgName # 文件Url
            )
            print(uploadMedia)
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=7,
                msg_id=message.id,
                media=uploadMedia
            )
        else:
            await message._api.post_group_message(
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
    db_path = os.path.join(os.path.expanduser("~"), "pcr", "pcr.db")
    print(db_path)
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
    initDateBase()



