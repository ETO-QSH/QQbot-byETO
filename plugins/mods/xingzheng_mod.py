from plugins.common import *


xingzheng_response = True
xingzheng = on_command("形政", rule=to_me())
xingzheng_cmd = on_command(("形政", "启用"), rule=to_me(), aliases={("形政", "禁用")}, permission=SUPERUSER)


@xingzheng_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global xingzheng_response
    if cmd[1] == "启用":
        xingzheng_response = True
    elif cmd[1] == "禁用":
        xingzheng_response = False
    await xingzheng_cmd.finish(f"**形政插件已{cmd[1]}**")


@xingzheng.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if xingzheng_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await xingzheng.finish(f"形政插件已禁用，请联系管理员：{config.superusers}")


@xingzheng.got("location", prompt="请给予题干片段")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    date = read_json("other\\形式与政策.json")
    found_dictionaries = []
    for key, items in date.items():
        for item in items:
            for i in items[item]:
                if location in i["Body"]:
                    found_dictionaries.append({item: i})
    try:
        messages = []
        msg = copy.deepcopy(one_node)
        msg["data"]["content"].append({"type": "at", "data": {'qq': str(event.get_user_id()), 'name': event.sender.nickname}})
        messages.append(msg)
        msg = copy.deepcopy(one_node)
        msg["data"]["content"].append({'type': 'text', 'data': {'text': location}})
        messages.append(msg)
        for item in found_dictionaries:
            msg = copy.deepcopy(one_node)
            msg["data"]["content"].append({'type': 'text', 'data': {'text': str(item)}})
            messages.append(msg)
        await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=messages)
    except FinishedException:
        pass
    except:
        await xingzheng.finish(f"没有`{location}`数据，原因不外乎我没写我没传你打错了，请先检查输入")
