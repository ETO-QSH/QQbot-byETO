from nonebot import on_message
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message


log_json = on_message(priority=1, block=False)

@log_json.handle()
async def _(event: MessageEvent):
    logger.opt(raw=True, colors=True).info(
        f"完整 raw_message:\n{event.raw_message}\n"
    )
