from plugins.common import *


help_ai = on_command("帮助", rule=to_me(), aliases={"-h", "help"})


@help_ai.handle()
async def help_eto(event: Event):
    help_msg = f'''
欢迎使用我搭建的群机器人！
目前，我实现了以下的功能：

1. [文件]--发送列表中的本地文件
2. [图片]--本地图片以及pixiv接口
3. [视频]--发送列表中的本地视频
4. [一言]--发送本地库中的语句
5. [头歌]--发送py编程作业的答案
6. [形政]--发送形政考试答案
7. [高数]--发送高数作业答案
8. [搜题]--理工学堂题库以图搜题
9. [问候]--arknights问候

你可以通过这些关键字访问功能
例如：`ETO 一言`
如此会返回更详细的信息
(此外还连接了戳一戳互动什么的)

项目的管理者为 {config.superusers}
如有需求和或者bug都可以反馈'''
    await help_ai.finish(MessageSegment.at(event.get_user_id()) + help_msg)
