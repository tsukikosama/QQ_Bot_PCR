from botpy.manage import C2CManageEvent
from botpy.message import Message

def sendGroupMessage(message: Message,type,content : str,media):
    message._api.post_group_message(
        group_openid=message.group_openid,
        msg_type=type,
        msg_id=message.id,
        content=content,
        media=media
    )


def sendPresonalMessage(message: C2CManageEvent,type):
     message._api.post_c2c_message(
        openid=message.author.user_openid,
        msg_type=type,
        content="hello",
        msg_id=message.id
    )

async def sendTemplate(message: Message,content):
     await message._api.post_group_message(
        group_openid=message.group_openid,
        msg_type=0,
        msg_id=message.id,
        content=content,
    )
