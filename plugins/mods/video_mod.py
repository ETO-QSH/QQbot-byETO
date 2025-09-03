from plugins.common import *


video_response = True
video = on_command("视频", rule=to_me())
video_cmd = on_command(("视频", "启用"), rule=to_me(), aliases={("视频", "禁用")}, permission=SUPERUSER)


@video_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global video_response
    if cmd[1] == "启用":
        video_response = True
    elif cmd[1] == "禁用":
        video_response = False
    await video_cmd.finish(f"**视频插件已{cmd[1]}**")


@video.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if video_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await video.finish(f"视频插件已禁用，请联系管理员：{config.superusers}")


@video.got("location", prompt="\n\n".join(["请提供视频序号："] + [f'Serial:{i} | name:{item["name"]} | tag:{item["tag"]}' for i, item in read_json("other\\video.json")["midishow"].items()]))
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    try:
        if "+" in location:
            locate = read_json("other\\video.json")["midishow"][location[:-1]]
            await video.send(MessageSegment.at(event.get_user_id()) + '\n' + f"更多信息：{str(locate)}")
            await video.finish(MessageSegment.video(locate["url"]))
        else:
            locate = read_json("other\\video.json")["midishow"][location]
            await video.send(MessageSegment.at(event.get_user_id()))
            await video.finish(MessageSegment.video(locate["url"]))
    except FinishedException:
        pass
    except:
        await video.finish("不是喵，怎么有人序号填不好")
