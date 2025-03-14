import os
import re
import botpy
from botpy import logging
from botpy.errors import ServerError

from botpy.ext.cog_yaml import read

from Conn import getTokenByOpenId, bindToken, updateTokenByOpenId, initDateBase, getRankImgByTitle
from FileUtils import file_to_base64
from ImgUtils import getRandomImgName
from PcrUtils import rank
import PcrUtils


test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()
from botpy.message import GroupMessage, Message
def matchCommod(message: Message):
    text = message.content.strip();
    ## 判断是否是绑定token的指令 如果是 就直接返回 判定和换绑指令
    pat = r"^#(\S+)(?:【(.*?)】)?$"
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

    async def on_group_at_message_create(self, message: Message):
        _log.info({message})
        res = matchCommod(message);
        uploadMedia = None
        print(res)
        ## 图文内容
        if res.strip().startswith("获取图片"):
            comd = extract_hashtag_content(res.strip())
            max_attempts = 5
            attempts = 0
            imgName = getRandomImgName();
            content = ""
            url=""
            if comd is not None:
                res = getRankImgByTitle(comd)
                content += res[3]
                url += res[1]
            else:
                url += "http://8.138.16.124:8083/upload/" + imgName
            try:
                uploadMedia = await message._api.post_group_file(
                    group_openid=message.group_openid,
                    file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                    url=url,  # 文件Url
                )
            except ServerError as e:

                if uploadMedia is None and attempts < max_attempts:
                    while (uploadMedia is None):
                        uploadMedia = await message._api.post_group_file(
                            group_openid=message.group_openid,
                            file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
                            url=url,  # 文件Url
                        )
                        if uploadMedia is not None:
                            break  # 如果成功获得 uploadMedia，则跳出循环
            try:
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=7,
                    msg_id=message.id,
                    media=uploadMedia,
                    content=content
                )
            except Exception:
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    msg_id=message.id,
                    content="文件过大或网络异常"
                )
        ###文本内容
        else:
            try:
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    msg_id=message.id,
                    content=res
                )
            except ServerError as e:
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    msg_id=message.id,
                    content="指令错误"
                )
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

