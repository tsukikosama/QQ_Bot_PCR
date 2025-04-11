import base64
import json
import os
import re
import uuid
from typing import List

import botpy
from PIL import Image
from botpy import logging
from botpy.errors import ServerError

from botpy.ext.cog_yaml import read
from botpy.manage import C2CManageEvent
from botpy.types.message import Ark, ArkKv

from Conn import getTokenByOpenId, bindToken, updateTokenByOpenId, initDateBase, getRankImgByTitle, getBoxIcon, \
    getBossInfo
from FileUtils import file_to_base64, base64_to_file
from ImgUtils import getRandomImgName
from PcrUtils import rank
import PcrUtils
from cmgUtils import getBox_Item, getHomeWork, getUrlByID
from pojo.AiUtils import chatAi, get_session_id
from pojo.ConmmonUtils import generate_unique_id
from pojo.Constant import PRC_RANK_STATUS, QQ_Ai_STATUS, GROUP_USER
from pojo.MessageUtils import sendTemplate, sendGroupMessage
from pojo.RedisUtils import clearVluae, saveList, isExistValue, removeValueFromList, getBossId

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
        strs = matchCommodV2(message);
        openid = generate_unique_id(message.author.member_openid, message.group_openid)
        text = message.content.strip();
        pat = r"^#(\S+)\s*(?:【(.*?)】)?$"
        ma = re.search(pat, text)
        keywords = ["刷图推荐1","刷图推荐2", "自动rank表", "手动rank表","rank表"]
        if ma:
            await sendTemplate(message, strs)
        else:
            ## 判断用户启用了哪种状态
            if isExistValue(GROUP_USER, message.group_openid) :
                strs = chatAi(message.content.strip(), message.group_openid)
                await sendTemplate(message, strs)
            if isExistValue(PRC_RANK_STATUS, message.group_openid):
                PcrUtils.getToken(message.group_openid);
                if "help" in message.content:
                    strs += ("\n*******公主连接功能功能介绍*******\n"
                             "①出刀情况 输入公会战日期来查询出刀情况 例如 出刀情况 2025-02-22 \n"
                             "②工会总表 查看公会成员的出刀数\n"
                             "③当前排名 查看公会的当前排名 例如 当前排名 咖啡馆 \n"
                             "④今日出刀 查看公会今日的出刀情况 \n"
                             "⑤今日排名 查询公会今日五点的排名情况 \n"
                             "⑥作业 查看对应的boss作业 例如 作业 1-5 36 1|2  1-5表示abcde 36表示boss编号 可以用boss查询到boss编号 1代表auto刀2表示手动刀\n"
                             "⑥视频 查看对应的boss作业的视频 例如 作业 25452-1 这个编号可以从作业功能中获取\n"
                             "⑦boss信息 获取当期的boss信息\n"
                             "⑧刷图推荐|自动rank表|手动rank表 可以获取花舞组当期的刷图推荐|自动rank表|手动rank表\n"
                             "⑨作业 查询对应的boss作业 例如 1-5周目 一到五王 1|2 1-5表示abcde 一到五王表示对应的王 1代表auto刀2表示手动刀")
                if "出刀情况" in message.content:
                    pattern = r"\d{4}-\d{2}-\d{2}"
                    re.findall(pattern, message.content)
                    match = re.search(pattern, message.content)
                    data = PcrUtils.getattactCountByDate(match.group(0));
                    strs += PcrUtils.getAttack(data)
                if "公会总表" in message.content:
                    data = PcrUtils.getAllAttactCount();
                    result = []
                    for entry in data.get('data'):
                        result.append(
                            f"成员:{entry['username']} 出刀数:{entry['number']} 伤害:{entry['damage']}")
                    # 输出所有格式化后的字符串
                    strs = "\n".join(result)
                if "当前排名" in message.content:
                    parts = text.split("当前排名")
                    data = rank(parts[1].strip())
                    strs += PcrUtils.getRankRecord(data);
                if "今日出刀" in message.content:
                    data = PcrUtils.attactCount();
                    strs += PcrUtils.getAttack(data);
                if "今日排名" in message.content:
                    strs += PcrUtils.getTodayRankStr();
                if "作业" in message.content:
                    parts = text.split("作业")
                    pattern = r'(\d+)\s+([\u4e00-\u9fa5]+)\s+(\d+)|(\d+)\s+(\d+)\s+(\d+)'  # 匹配 "数字" 或 "数字+汉字"（可选）
                    matches = re.findall(pattern, parts[1])
                    zm = None
                    id = None
                    lx = None;
                    for match in matches:
                        if match[1]:  # 匹配到数字-汉字-数字格式
                            zm = match[0]
                            id = getBossId(match[1])
                            lx = match[2]
                        else:  # 匹配到数字-数字-数字格式
                            zm = match[3]
                            id = match[4]
                            lx = match[5]
                    # parts = text.split("作业")
                    # numbers = re.findall(r'\d+', parts[1].strip())  # 提取所有数字

                    list = getHomeWork(zm,id,lx)
                    print(list)
                    try:
                        for item in list:
                            temp = f"作业编号:{item.get('id')} 标题:{item.get('title')}\n角色:"
                            role_str = ' '.join(' '.join(role) for role in item.get('role'))
                            temp += role_str
                            temp += f"伤害 {item.get('damage')}"
                            temp += f"{item.get('remain')}"
                            strs += "\n" + temp + "\n"
                    except Exception as e:
                        strs += "没有符合的作业"
                if "视频" in message.content:
                    parts = text.strip().split("视频")
                    strs += getUrlByID(parts[1].strip());
                if "boss信息" in message.content:
                    list = getBossInfo()
                    strs = "".join(f"\n boss编号:{item[0]} boss名称:{item[2].strip()}" for item in list if item[2].strip());
                if "更新会战数据" in message.content:
                    getBox_Item();
                    strs += "会战数据更新成功"
                if any(keyword in message.content for keyword in keywords):
                    res = getRankImgByTitle(message.content.strip())
                    content = res[3]
                    url = res[1]
                    uploadMedia = await message._api.post_group_file(
                        group_openid=message.group_openid,
                        file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                        url=url,  # 文件Url
                    )
                    await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=7,
                        msg_id=message.id,
                        media=uploadMedia,
                        content=content
                    )
                    return

                await sendTemplate(message, strs)
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
        elif action == "帮助":

            str += ""
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
