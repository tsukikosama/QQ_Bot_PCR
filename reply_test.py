import botpy
from botpy import logging
import asyncio
from botpy.message import Message
_log = logging.get_logger()

class testReply(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        _log.info(message.author.avatar)
        if "sleep" in message.content:
            await asyncio.sleep(10)
        _log.info(message.author.username)
        await message.reply(content=f"机器人{self.robot.name}收到你的@消息了: {message.content}")