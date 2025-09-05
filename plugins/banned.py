from plugins.common import *


banned = on_command("封禁", rule=to_me(), aliases={"解封"}, permission=SUPERUSER)


async def load_ban():
    async with aiofiles.open(BAN_FILE, "r", encoding="utf-8") as f:
        return json.loads(await f.read())


async def save_ban(data):
    async with aiofiles.open(BAN_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2))


@banned.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    at_seg = args["at"]

    if at_seg:
        matcher.set_arg("location", at_seg[0].data["qq"])
        return

    text = args.extract_plain_text().strip()
    if text.isdigit():
        matcher.set_arg("location", text)
    else:
        await banned.finish(MessageSegment.at(event.get_user_id()) + "参数错误")


@banned.got("location")
async def got_location(location: str = Arg(), cmd: tuple = Command()):
    try:
        ban_list = await load_ban()
        cmd, user = cmd[0], location

        if cmd == "封禁":
            ban_list[user] = True
        else:
            ban_list.pop(user, None)

        await save_ban(ban_list)
        await banned.finish(f"已{cmd}用户：{user}")

    except FinishedException:
        pass

    except Exception as e:
        await banned.finish(f"操作失败：{e}")
