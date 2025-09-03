from plugins.common import *


hitokoto_response = True
hitokoto = on_command("一言", rule=to_me())
hitokoto_cmd = on_command(("一言", "启用"), rule=to_me(), aliases={("一言", "禁用")}, permission=SUPERUSER)


@hitokoto_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global hitokoto_response
    if cmd[1] == "启用":
        hitokoto_response = True
    elif cmd[1] == "禁用":
        hitokoto_response = False
    await hitokoto_cmd.finish(f"**一言插件已{cmd[1]}**")


@hitokoto.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if hitokoto_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await hitokoto.finish(f"一言插件已禁用，请联系管理员：{config.superusers}")


@hitokoto.got("location", prompt='请选择句子类型：' + str(list(read_json("other\\hitokoto.json")["sentences"].keys())))
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    date = read_json("other\\hitokoto.json")
    try:
        if "+" in location:
            await hitokoto.finish(MessageSegment.at(event.get_user_id()) + '\n\n' + str(random.choice(date["sentences"][location[:-1]])))
        else:
            c = random.choice(date["sentences"][location])
            await hitokoto.finish(MessageSegment.at(event.get_user_id()) + '\n\n' + f'{c["hitokoto"]}\n\nFrom：{c["from"]}')
    except FinishedException:
        pass
    except:
        await hitokoto.finish("不是喵，这就单选题的说")
