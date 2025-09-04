from plugins.common import *


LOCK = asyncio.Lock()
DATA_DIR = Path("data/group_msg")
DATA_DIR.mkdir(parents=True, exist_ok=True)
is_group_msg = lambda event: event.message_type == "group"
group_msg = on_message(rule=Rule(is_group_msg), block=False)


@group_msg.handle()
async def recorder(bot: Bot, event: MessageEvent, matcher: Matcher):
    gid = str(event.group_id)
    mid = str(event.message_id)
    uid = str(event.user_id)
    tim = int(time.time())

    text_parts = []
    img_urls = []
    for seg in event.message:
        if seg.type == "text":
            text_parts.append(seg.data["text"])
        elif seg.type == "image":
            img_urls.append(seg.data.get("url", ""))
    content = "".join(text_parts).strip()

    item = {
        "message_id": mid,
        "user_id": uid,
        "group_id": gid,
        "timestamp": tim,
        "content": content,
        "images": img_urls
    }

    hour_str = time.strftime("%H", time.localtime(tim))
    date_str = time.strftime("%Y-%m-%d", time.localtime(tim))

    dir_path = DATA_DIR / gid / date_str
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"{hour_str}.json"

    async with LOCK:
        if file_path.exists():
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                data = json.loads(await f.read())
        else:
            data = []
        data.append(item)
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
