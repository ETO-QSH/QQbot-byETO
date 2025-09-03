from plugins.common import *


file_response = True
file = on_command("文件", rule=to_me())
file_cmd = on_command(("文件", "启用"), rule=to_me(), aliases={("文件", "禁用")}, permission=SUPERUSER)

file_path = "D:\\Images\\文件"


@file_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global file_response
    if cmd[1] == "启用":
        file_response = True
    elif cmd[1] == "禁用":
        file_response = False
    await file_cmd.finish(f"**文件插件已{cmd[1]}**")


@file.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if file_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await file.finish(f"文件插件已禁用，请联系管理员：{config.superusers}")


@file.got("location", prompt='文件列表（很大!=很慢）：\n\n'+"\n\n".join([f"{i+1}. {file}" for i, file in enumerate(work_paths(file_path).keys())]))
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    data = work_paths(file_path)
    try:
        if int(location) in range(1, len(data)+1):
            await bot.send_msg(message_type="group", group_id=event.group_id, message=[{"type": "file", "data": {"url": data[list(data.keys())[int(location)-1]]}}])
        else:
            raise "Exception: 未知文件"
    except FinishedException:
        pass
    except NetworkError:
        pass
    except:
        await file.finish(f"不是喵，怎么有人序号填不好")
