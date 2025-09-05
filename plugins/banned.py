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
    qq_list: List[str] = []

    for seg in args["at"]:
        qq_list.append(str(seg.data["qq"]))

    for seg in args.extract_plain_text().split():
        seg = seg.strip()
        if seg.isdigit():
            qq_list.append(seg)

    if not qq_list:
        await banned.finish(MessageSegment.at(event.get_user_id()) + "请至少 @ 一位用户或输入 QQ 号")

    matcher.set_arg("location", " ".join(qq_list))


@banned.got("location")
async def got_location(location: str = Arg(), cmd: tuple = Command()):
    action = cmd[0]
    qq_list = location.split()

    ban_list = await load_ban()
    ok_users = []

    for qq in qq_list:
        if action == "封禁":
            ban_list[qq] = True
        else:
            ban_list.pop(qq, None)
        ok_users.append(qq)

    await save_ban(ban_list)
    await banned.finish(f"已{action}用户：{'、'.join(ok_users)}")
