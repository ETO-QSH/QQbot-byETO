from plugins.common import *


educoder_response = True
educoder = on_command("头歌", rule=to_me())
educoder_cmd = on_command(("头歌", "启用"), rule=to_me(), aliases={("头歌", "禁用")}, permission=SUPERUSER)



@educoder_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global educoder_response
    if cmd[1] == "启用":
        educoder_response = True
    elif cmd[1] == "禁用":
        educoder_response = False
    await educoder_cmd.finish(f"**头歌插件已{cmd[1]}**")


@educoder.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if educoder_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await educoder.finish(f"头歌插件已禁用，请联系管理员：{config.superusers}")


@educoder.got("location", prompt="请给予更多信息：{理论|实践}课-第{N}章-第{n}题\n例：`实践课第三章第9题`")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    date = read_json("other\\educoder.json")
    match = re.search(r"(理论|实践)课.*第([\u4e00-\u9fa5]+)章.*第(\d+)题", location)
    try:
        msg1, msg2, msg3, file = copy.deepcopy(one_node), copy.deepcopy(one_node), copy.deepcopy(one_node), \
        date["educoder"][match.group(1)][match.group(2)][match.group(3)][0]
        msg1["data"]["content"].append(
            {"type": "at", "data": {'qq': str(event.get_user_id()), 'name': event.sender.nickname}})
        msg2["data"]["content"].append(
            {'type': 'text', 'data': {'text': f"{match.group(1)}课第{match.group(2)}章第{match.group(3)}题"}})
        msg3["data"]["content"].append({'type': 'text', 'data': {'text': read_txt(file)}})
        await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=[msg1, msg2, msg3])
    except FinishedException:
        pass
    except:
        await educoder.finish(f"没有`{location}`数据，原因不外乎我没写我没传你打错了，请先检查输入")
