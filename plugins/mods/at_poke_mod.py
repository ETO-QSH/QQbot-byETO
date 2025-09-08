from plugins.common import *


at_me = on_message(rule=to_me())
poke_notice = on_notice(rule=to_me())


@at_me.handle()
async def at_bot(bot: Bot, event: Event):
    if '<le>[at:qq=3078491964' in str(event.get_log_string()) and str(event.get_message()) == '' and 'reply:id=' not in str(event.get_log_string()):
        """
            audio = "https://raw.githubusercontent.com/ETO-QSH/QQbot-byETO/refs/heads/main/links/水瀬いのり%20久保ユリカ%20-%20Endless%20Journey.flac"
            image = "https://raw.githubusercontent.com/ETO-QSH/QQbot-byETO/refs/heads/main/links/少女终末旅行_1x1.jpg"
            cq = (
                '[CQ:music,type=custom,'
                'url=https://github.com/ETO-QSH/QQbot-byETO,'
                'audio={},'
                'title=Endless Journey,'
                'content=少女終末旅行-EP,'
                'image={}]'.format(audio, image)
            )
            await at_me.finish(Message(cq))
        """
        await at_me.finish("꒰ঌ( ⌯' '⌯)໒꒱")


@poke_notice.handle()
async def send_emoji(bot: Bot, event: Event):
    if event.notice_type == 'notify' and event.sub_type == 'poke':
        """
        if str(event.group_id) in ["797784653", "981535936"] and gaoshu_response:
            Information = read_json(r'理工学堂\\高等数学.json')
            files = find_paths(r'理工学堂\\高等数学 (ID_42)', 'png')
            file = random.choice(files)
            file_name = os.path.basename(file).split('.')[0]
            path_name = os.path.basename(os.path.dirname(os.path.dirname(file))).split()[0]
            info = Information[path_name][file_name][0]
            await poke_notice.finish(MessageSegment.image(os.path.abspath(file)) + f"发送 `ETO 高数 {info}` 获取答案")
        else:
            custom_faces = await bot.call_api("fetch_custom_face")
            await bot.send_group_msg(group_id=event.group_id, message=MessageSegment.image(file=custom_faces[0]))
        """
        custom_faces = await bot.call_api("fetch_custom_face")
        await bot.send_group_msg(group_id=event.group_id, message=MessageSegment.image(file=custom_faces[0]))
