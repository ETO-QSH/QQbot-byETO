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

    texts = []
    images = []
    records = []
    files = []
    ats = []

    for seg in event.message:
        if seg.type == "text":
            texts.append(seg.data.get("text", ""))
        elif seg.type == "image":
            images.append(seg.data.get("url", ""))
        elif seg.type == "record":
            records.append(seg.data.get("url") or seg.data.get("file", ""))
        elif seg.type == "file":
            files.append(seg.data.get("url") or seg.data.get("file", ""))
        elif seg.type == "at":
            ats.append(seg.data.get("qq", ""))

    hour_str = time.strftime("%H", time.localtime(tim))
    date_str = time.strftime("%Y-%m-%d", time.localtime(tim))
    timestamp = time.strftime("%H:%M:%S", time.localtime(tim))

    item = {
        "message_id": mid,
        "user_id": uid,
        "group_id": gid,
        "timestamp": timestamp,
        "text": texts,
        "images": images,
        "records": records,
        "files": files,
        "ats": ats
    }

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
