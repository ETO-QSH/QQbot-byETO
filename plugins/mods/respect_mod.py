from plugins.common import *


respect_response = True
respect = on_command("问候", rule=to_me())
respect_cmd = on_command(("问候", "启用"), rule=to_me(), aliases={("问候", "禁用")}, permission=SUPERUSER)


@respect_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global respect_response
    if cmd[1] == "启用":
        respect_response = True
    elif cmd[1] == "禁用":
        respect_response = False
    await respect_cmd.finish(f"**问候插件已{cmd[1]}**")


@respect.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if respect_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
        else:
            await respect.finish(MessageSegment.record("https://torappu.prts.wiki/assets/audio/voice/char_180_amgoat/cn_042.wav"))
    else:
        await respect.finish(f"问候插件已禁用，请联系管理员：{config.superusers}")


@respect.got("location", prompt="格式参考：[干员[行为&语言]]")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    link, data = None, read_json("PRTS/prts.json")
    loc = location.split()
    if loc[0] in data:
        for index, item in data[loc[0]].items():
            if len(loc) == 1:
                if item['title'] == '问候':
                    link = 'https:' + item['voice_link']['日语'].split('?')[0]
                    break
            elif len(loc) == 2:
                if item['title'] == loc[1]:
                    link = 'https:' + item['voice_link']['日语'].split('?')[0]
                    break
                elif loc[1] in item['voice_link'].keys():
                    link = 'https:' + item['voice_link'][loc[1]].split('?')[0]
                    break
            elif len(loc) == 3:
                if item['title'] in loc[1:]:
                    if item['title'] == loc[1] and loc[2] in item['voice_link'].keys():
                        link = 'https:' + item['voice_link'][loc[2]].split('?')[0]
                        break
                    elif item['title'] == loc[2] and loc[1] in item['voice_link'].keys():
                        link = 'https:' + item['voice_link'][loc[1]].split('?')[0]
                        break
            else:
                break
        if link:
            await respect.finish(MessageSegment.record(link))
        else:
            await respect.finish(f"参数`{loc[1:]}`错误捏~")
    else:
        await respect.finish(f"没有`{loc[0]}`干员哦~")
