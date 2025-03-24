import base64
import json
import os
import re
import uuid

import botpy
from PIL import Image
from botpy import logging
from botpy.errors import ServerError

from botpy.ext.cog_yaml import read
from botpy.manage import C2CManageEvent

from Conn import getTokenByOpenId, bindToken, updateTokenByOpenId, initDateBase, getRankImgByTitle, getBoxIcon
from FileUtils import file_to_base64, base64_to_file
from ImgUtils import getRandomImgName
from PcrUtils import rank
import PcrUtils
from cmgUtils import getBox_Item, getHomeWork
from pojo.AiUtils import chatAi, get_session_id
from pojo.ConmmonUtils import generate_unique_id
from pojo.Constant import PRC_RANK_STATUS, QQ_Ai_STATUS, GROUP_USER
from pojo.MessageUtils import sendTemplate, sendGroupMessage
from pojo.RedisUtils import clearVluae, saveList, isExistValue, removeValueFromList

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()
from botpy.message import GroupMessage, Message
def matchCommod(message: Message):

    text = message.content.strip();
    ## 判断是否是绑定token的指令 如果是 就直接返回 判定和换绑指令
    pat = r"^#(\S+)\s*(?:【(.*?)】)?$"
    ma = re.search(pat, text)
    str = ""
    if ma:
        action, token = ma.groups()
        if action == "绑定":
           str +=  bindToken(message.group_openid, token)
        elif action == "换绑":
            str += updateTokenByOpenId(message.group_openid, token)
        elif action == "获取图片":
            str += "获取图片"
        elif action == "帮助文档":
            str += ""
        elif action == "彩星神":
           ##获取uuid5作为唯一的id
           openid = generate_unique_id(message.author.member_openid , message.group_openid)
           str += chatAi(token,openid)
        elif action == '重置彩星神':
            openid = generate_unique_id(message.author.member_openid, message.group_openid)
            clearVluae(openid)
            str += "上下文清空成功";
        elif action == "关闭功能":
            openid = generate_unique_id(message.author.member_openid, message.group_openid)

            str += "功能关闭成功,需要使用请重新开启";
        else:
            str += "匹配失败"
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
            str += "匹配失败"
    pattern2 = r"^#pcr\s*【\s*(.*?)\s*】$"
    match2 = re.match(pattern2, text)
    ## 判断指令是否是#pcr开头
    if match2:
        ## 判断发送消息的账号是否绑定了token
        user = getTokenByOpenId(message.group_openid)
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
            elif match2.group(1).strip() == "刷图推荐":
                str += "获取图片 #刷图推荐"
            elif match2.group(1).strip() == "自动rank表":
                str += "获取图片 #自动rank表"
            elif match2.group(1).strip() == "手动rank表":
                str += "获取图片 #手动rank表"
            elif match2.group(1).strip() == "rank表":
                str += "获取图片 #rank表"
            else:
                str = "匹配失败"

    return str
def extract_hashtag_content(text):
    match = re.search(r"#([\w\u4e00-\u9fff]+)", text.strip())
    return match.group(1) if match else None  # 如果匹配不到，返回 None


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 启动成功!")

    async def on_friend_add(self, event: C2CManageEvent):
        _log.info("用户添加机器人：" + str(event))

        await self.api.post_c2c_message(
            openid=event.openid,
            msg_type=0,
            event_id=event.event_id,
            content="我是彩星喵 一个超级无敌的公主连接公会战查询工具 还有其他的功能请自己探索",
        )
    # async def on_friend_del(self, event: C2CManageEvent):
    #     _log.info("用户删除机器人：" + str(event))
    #
    # async def on_c2c_msg_reject(self, event: C2CManageEvent):
    #     _log.info("用户关闭机器人主动消息：" + str(event))
    ### 私信
    async def on_c2c_message_create(self, event: C2CManageEvent):
        str = chatAi(event.content.strip(), event.author.user_openid)
        # 获取用户的id 然后进行chat回复
        await self.api.post_c2c_message(
            openid=event.author.user_openid,
            msg_type=0,
            content=str,
            msg_id=event.id
        )

    # async def on_group_at_message_create(self, message: Message):
    #     _log.info({message})
    #     res = matchCommod(message);
    #     uploadMedia = None
    #     ## 图文内容
    #     if res.strip().startswith("获取图片"):
    #         comd = extract_hashtag_content(res.strip())
    #         max_attempts = 5
    #         attempts = 0
    #         imgName = getRandomImgName();
    #         content = ""
    #         url=""
    #         if comd is not None:
    #             res = getRankImgByTitle(comd)
    #             content += res[3]
    #             url += res[1]
    #         else:
    #             url += "http://8.138.16.124:8083/upload/" + imgName
    #         uploadMedia = await message._api.post_group_file(
    #             group_openid=message.group_openid,
    #             file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
    #             url=url,  # 文件Url
    #         )
    #         try:
    #             await message._api.post_group_message(
    #                 group_openid=message.group_openid,
    #                 msg_type=7,
    #                 msg_id=message.id,
    #                 media=uploadMedia,
    #                 content=content
    #             )
    #         except Exception:
    #             await message._api.post_group_message(
    #                 group_openid=message.group_openid,
    #                 msg_type=0,
    #                 msg_id=message.id,
    #                 content="文件过大或网络异常"
    #             )
    #     ###文本内容
    #     else:
    #         try:
    #             await message._api.post_group_message(
    #                 group_openid=message.group_openid,
    #                 msg_type=0,
    #                 msg_id=message.id,
    #                 content=res
    #             )
    #         except ServerError as e:
    #             await message._api.post_group_message(
    #                 group_openid=message.group_openid,
    #                 msg_type=0,
    #                 msg_id=message.id,
    #                 content="指令错误"
    #             )

    async def on_group_at_message_create(self, message: Message):
        _log.info({message})
        str = matchCommodV2(message);
        openid = generate_unique_id(message.author.member_openid, message.group_openid)
        text = message.content.strip();
        pat = r"^#(\S+)\s*(?:【(.*?)】)?$"
        ma = re.search(pat, text)
        keywords = ["刷图推荐", "自动rank表", "手动rank表","rank表"]
        if ma:
            await sendTemplate(message, str)
        else:
            ## 判断用户启用了哪种状态
            if isExistValue(GROUP_USER, message.group_openid) :
                str = chatAi(message.content.strip(), message.group_openid)
                await sendTemplate(message, str)
            if isExistValue(PRC_RANK_STATUS, message.group_openid):
                PcrUtils.getToken(message.group_openid);
                if "出刀情况" in message.content:
                    pattern = r"\d{4}-\d{2}-\d{2}"
                    re.findall(pattern, message.content)
                    match = re.search(pattern, message.content)
                    data = PcrUtils.getattactCountByDate(match.group(0));
                    str += PcrUtils.getAttack(data)
                if "公会总表" in message.content:
                    data = PcrUtils.getAllAttactCount();
                    result = []
                    for entry in data.get('data'):
                        result.append(
                            f"成员:{entry['username']} 出刀数:{entry['number']} 伤害:{entry['damage']}")
                    # 输出所有格式化后的字符串
                    str = "\n".join(result)
                if "当前排名" in message.content:
                    parts = text.split("当前排名")
                    data = rank(parts[1].strip())
                    str += PcrUtils.getRankRecord(data);
                if "今日出刀" in message.content:
                    data = PcrUtils.attactCount();
                    str += PcrUtils.getAttack(data);
                if "今日排名" in message.content:
                    str += PcrUtils.getTodayRank();
                if any(keyword in message.content for keyword in keywords):
                    res = getRankImgByTitle(message.content.strip())
                    content = res[3]
                    url = res[1]

                    uploadMedia = await message._api.post_group_filebase64(
                        group_openid=message.group_openid,
                        file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                        data=url,  # 文件Url
                    )

                    await message._api.post_group_message(
                                        group_openid=message.group_openid,
                                        msg_type=7,
                                        msg_id=message.id,
                                        media=uploadMedia,
                                        content=content
                    )
                    return
                await sendTemplate(message, str)
                # res = getHomeWork(1);
                # urls = getBoxIcon(res)
                # print(urls)
                # list = []
                # for url in urls:
                #     uploadMedia = await message._api.post_group_file(
                #         group_openid=message.group_openid,
                #         file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                #         url=url,  # 文件Url
                #     )
                #     list.append(uploadMedia)
                # await sendGroupMessage(message,1,"公会战作业",list)
def matchCommodV2(message: Message):
    text = message.content.strip();
    pat = r"^#(\S+)\s*(?:【(.*?)】)?$"
    ma = re.search(pat, text)
    str = ""
    if ma:
        action, token = ma.groups()
        if action == "绑定":
            str += bindToken(message.group_openid, token)
        elif action == "公主连接":
            saveList(PRC_RANK_STATUS,message.group_openid)
            str += "开启公主连接功能"
        elif action == "关闭公主连接":
            removeValueFromList(PRC_RANK_STATUS,message.group_openid)
            str += "关闭公主连接功能"
        elif action == "彩星神":
            saveList(GROUP_USER, message.group_openid)
            str += "开启群回复功能"
        elif action == "关闭彩星神":
            removeValueFromList(GROUP_USER,message.group_openid)
            str += "关闭群回复功能"
        elif action == "重置彩星神":
            clearVluae(message.group_openid)
            str += "彩星神重启完毕 需要重新开启彩星神"
        elif action == "获取会战数据":
            getBox_Item()
            str += "保存角色数据完毕"

        else:
            str += "匹配失败"
    return str
if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True
    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.http.timeout = 30
    client.run(appid=test_config["appid"], secret=test_config["secret"])



