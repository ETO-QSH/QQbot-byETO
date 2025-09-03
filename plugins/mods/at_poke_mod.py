from plugins.common import *


at_me = on_message(rule=to_me())
poke_notice = on_notice(rule=to_me())


@at_me.handle()
async def at_bot(bot: Bot, event: Event):
    if '<le>[at:qq=3078491964' in str(event.get_log_string()) and str(
            event.get_message()) == '' and 'reply:id=' not in str(event.get_log_string()):
        # 音乐卡片 await at_me.finish(MessageSegment.music_custom(url="https://www.midishow.com/u/Dr.ETO", audio="https://torappu.prts.wiki/assets/audio/voice/char_180_amgoat/cn_042.wav", title="Endless Journey", content="少女終末旅行-EP",
        # 音乐卡片                                                img_url="https://a1.qpic.cn/psc?/V12Kat591VDTdC/TmEUgtj9EK6.7V8ajmQrEJ0d2fTNbbZT0OkScIYmdH7XloC6xCxrhrUWckUAxAT1UrSveoRSIKCAozqgGJw5Lv3yiFAsIF.eEFS4qBxfyhU!/b&"
        # 音乐卡片                                                        "ek=1&kp=1&pt=0&bo=AAQABAAEAAQDd1I!&tl=1&vuin=2373204754&tm=1736996400&dis_t=1736999214&dis_k=35ed510366a2e5871531674719dd0bb2&sce=60-2-2&rf=viewer_4"))
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
