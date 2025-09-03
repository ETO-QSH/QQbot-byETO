from plugins.common import *
from plugins.PixivByETO.main import *


image_response = True
image = on_command("图片", rule=to_me())
image_cmd = on_command(("图片", "启用"), rule=to_me(), aliases={("图片", "禁用")}, permission=SUPERUSER)


def organize_pixiv_data(paths):
    H2C = lambda s: re.sub(r'`0x([0-9a-fA-F]{2})`', lambda match: chr(int(match.group(1), 16)), s)
    grouped_paths, paths = {}, list(set(paths))
    for path in paths:
        group_key = H2C("画师：" + os.path.basename(os.path.dirname(os.path.dirname(os.path.normpath(path)))))
        if group_key not in grouped_paths.keys():
            grouped_paths[group_key] = []
        dir = os.listdir(path)
        for Json in dir:
            if Json.endswith('.json'):
                with open(os.path.join(path, Json), 'r', encoding='utf-8') as file:
                    data = json.load(file)
                json_files = H2C(f"{'插画' if os.path.basename(os.path.dirname(os.path.normpath(path))) == 'illust' else '漫画'}：{os.path.splitext(Json)[0]}✙{list(data.keys())[0]}")
        other_files = [os.path.abspath(os.path.join(path, file)) for file in dir if not file.endswith('.json')]
        grouped_paths[group_key].append({json_files: other_files})
    return grouped_paths


# 双层合并转发版本，未生效
def structure_node_2f(data_structure, one_node, event):
    msgs = []
    msg = copy.deepcopy(one_node)
    msg["data"]["content"].append({'type': 'at', 'data': {'qq': str(event.get_user_id()), 'name': event.sender.nickname}})
    msgs.append(copy.deepcopy(msg))
    for artist, illustrations in data_structure.items():
        msg = copy.deepcopy(one_node)
        msg["data"]["content"].append({'type': 'text', 'data': {'text': artist}})
        msgs.append(copy.deepcopy(msg))
        msg = copy.deepcopy(one_node)
        msg_node = []
        for illustration in illustrations:
            msg_data = copy.deepcopy(one_node)
            for illustrate, images in illustration.items():
                msg_data["data"]["content"].append({'type': 'text', 'data': {'text': illustrate}})
                for image in images:
                    msg_data["data"]["content"].append({'type': 'image', 'data': {'file': image}})
            msg_node.append(copy.deepcopy(msg_data))
        msg["data"]["content"].append({'type': 'forward', 'data': {'node': copy.deepcopy(msg_node)}})
        msgs.append(copy.deepcopy(msg))
    return msgs


def structure_node(data_structure, one_node, event):
    msgs = []
    msg = copy.deepcopy(one_node)
    msg["data"]["content"].append({'type': 'at', 'data': {'qq': str(event.get_user_id()), 'name': event.sender.nickname}})
    msgs.append(copy.deepcopy(msg))
    for artist, illustrations in data_structure.items():
        for illustration in illustrations:
            msg = copy.deepcopy(one_node)
            msg_data = copy.deepcopy(one_node)
            for illustrate, images in illustration.items():
                msg["data"]["content"].append({'type': 'text', 'data': {'text': f'{artist}\n\n{illustrate}'}})
                for image in images:
                    msg_data["data"]["content"].append({'type': 'image', 'data': {'file': image}})
            msgs.append(copy.deepcopy(msg))
            msgs.append(copy.deepcopy(msg_data))
    return msgs


def structure_node_t(data_structure, event):
    msgs = [{'type': 'at', 'data': {'qq': str(event.get_user_id()), 'name': event.sender.nickname}}]
    for artist, illustrations in data_structure.items():
        for illustration in illustrations:
            for illustrate, images in illustration.items():
                msgs.append({'type': 'text', 'data': {'text': f'\n\n{artist}\n\n{illustrate}\n\n'}})
                for image in images:
                    msgs.append({'type': 'image', 'data': {'file': image}})
    return msgs


@image_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global image_response
    if cmd[1] == "启用":
        image_response = True
    elif cmd[1] == "禁用":
        image_response = False
    await image_cmd.finish(f"**图片插件已{cmd[1]}**")


@image.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if image_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await image.finish(f"图片插件已禁用，请联系管理员：{config.superusers}")


@image.got("location", prompt="目前开放图片源：[ 本地 | pixiv ]")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    try:
        if location == '本地':
            await image.finish(MessageSegment.at(event.get_user_id()) + MessageSegment.image(
                random_file([r"D:\Images\图片", r"D:\Desktop\Desktop\new-pic"])))
        elif location == "pixiv":
            if event.get_user_id() in config.superusers:
                matcher.got("mode")
            else:
                # await image.send("悠着点用，接口那边也是我写的，纲领是能跑就行，暂时不支持异步，而且因为需要代理，以及使用我的账号，可能出现一些问题。如果需要良好的下载环境，可以在我的github中找到独立的pixiv接口")
                # await image.finish("测试阶段权限还未开启")
                await image.finish("刚禁的别想了的说")
                matcher.got("mode")
        else:
            raise "Exception: 未知源"
    except FinishedException:
        await image.finish()
    except:
        await image.finish("不是喵，这那么难选吗的说")


@image.got("mode", prompt="请输入功能序号：\n\nS1. 插画信息\n\nS2. 用户作品\n\nS3. 榜单查询\n\nS4. 用户查找\n\nS5. 标签查询\n\nD1. 下载单个插画\n\nD2. 下载用户所有作品\n\nD3. 下载匹配用户名最新作品\n\nD4. 下载指定榜单所有作品\n\nD5. 下载标签下指定页作品")
async def got_artist_id(bot: Bot, event: Event, matcher: Matcher, mode: str = ArgPlainText()):
    if mode in ['S1', 'S2', 'S3', 'S4', 'S5', 'D1', 'D2', 'D3', 'D4', 'D5']:
        Dict = {"S1": "***必要参数***\n\n'pid': [pid]",
                "S2": "***必要参数***\n\n'uid': [uid]",
                "S3": "***非必要参数***\n\n'mode': [`day`|week|month|(.etc)]\n'date': [20**-**-**|`ytd.`]\n'filter': [True|`False`]\n\n***隐藏参数***\n\n'offset': [int]\n'req_auth': [bool]",
                "S4": "***必要参数***\n\n'name': [name]\n\n***非必要参数***\n\n'target': [`exact`|partial]\n'duration': [day|week|`month`]\n'sort': [old|`new`|vip]\n\n***隐藏参数***\n\n'offset': [int]\n'req_auth': [bool]",
                "S5": "***必要参数***\n\n'tag': [tag]\n\n***非必要参数***\n\n'target': [`exact`|partial|caption]\n'duration': [day|week|`month`]\n'sort': [old|`new`|vip]\n'ai': [`True`|False]\n'start_date': [20**-**-**|`ytd.`]\n'end_date': [20**-**-**|`ytd.`]\n'page': [int|`0`]\n\n***隐藏参数***\n\n'offset': [int]\n'req_auth': [bool]",
                "D1": "***必要参数***\n\n'pid': [pid]\n\n***非必要参数***\n\n'zip': [True|`False`]",
                "D2": "***必要参数***\n\n'uid': [uid]\n\n***非必要参数***\n\n'zip': [`True`|False]",
                "D3": "***必要参数***\n\n'name': [name]\n\n***非必要参数***\n\n'zip': [True|`False`]",
                "D4": "***非必要参数***\n\n'mode': [`day`|week|month|(.etc)]\n'date': [20**-**-**|`ytd.`]\n'filter': [True|`False`]\n'zip': [`True`|False]\n\n***隐藏参数***\n\n'offset': [int]\n'req_auth': [bool]",
                "D5": "***必要参数***\n\n'tag': [tag]\n\n***非必要参数***\n\n'zip': [`True`|False]\n'target': [`exact`|partial|caption]\n'duration': [day|week|`month`]\n'sort': [old|`new`|vip]\n'ai': [`True`|False]\n'start_date': [20**-**-**|`ytd.`]\n'end_date': [20**-**-**|`ytd.`]\n'page': [int|`0`]\n\n***隐藏参数***\n\n'offset': [int]\n'req_auth': [bool]"}
        await image.send(MessageSegment.text(f"请输入相关参数：\n\n{Dict[mode]}\n\n请按照格式传参！"))
        await image.send(MessageSegment.text(f"格式参考：\n\n#(必要参数value)# #(非必要参数key):(非必要参数value)# #(非必要参数key):(非必要参数value)#\n\n格式示例：\n\nD4 | ## \nD1 | #96348927# \nD3 | #_Quan# #zip:True# \nS3 | #mode:day# #date:2024-10-01# #filter:True#"))
        matcher.got("args")
    else:
        await image.finish("不是喵，怎么有人序号填不好")


@image.got("args")
async def got_work_id(bot: Bot, event: Event, matcher: Matcher, args: str = ArgPlainText()):
    mode = str(matcher.get_arg("mode"))
    args = str(matcher.get_arg("args")).strip()
    mod = {
      "S1": "插画信息", "S2": "用户作品", "S3": "榜单查询", "S4": "用户查找", "S5": "标签查询", "D1": "下载单个插画",
      "D2": "下载用户所有作品", "D3": "下载匹配用户名最新作品", "D4": "下载指定榜单所有作品",
      "D5": "下载标签下指定页作品"}[mode]
    matches, args_dict = re.findall(r'#(.*?)#', args), {}

    for match in matches:
        if ':' in match:
            key, value = match.split(':', 1)
            args_dict[key] = value
        else:
            args_dict["main"] = match

    try:
        if not args_dict:
            raise "Exception: 没有参数"
        elif mode in ["S3", "D4"]:
            if not args_dict:
                raise "Exception: 参数错误"
        UUID, args_save = uuid.uuid4(), copy.deepcopy(args_dict)

        if mode == 'S1' and set(args_dict.keys()).issubset({"main"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}")
            text, msg = get_illust_details(pid=args_dict["main"]), copy.deepcopy(one_node)
            msg["data"]["content"].append({'type': 'text', 'data': {'text': str(text)}})
            await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=[msg])

        elif mode == 'S2' and set(args_dict.keys()).issubset({"main"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}")
            text, msg = get_user_all_illusts_information(uid=args_dict["main"]), copy.deepcopy(one_node)
            msg["data"]["content"].append({'type': 'text', 'data': {'text': str(text)}})
            await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=[msg])

        elif mode == 'S3' and set(args_dict.keys()).issubset({"main", "mode", "date", "filter", "offset", "req_auth"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}")
            text, msgs = get_illust_ranking(**{key: value for key, value in args_dict.items() if key != "main"}), []
            for QQlen in range((len(text) + 2) // 3):
                if QQlen < 10:
                    msg = copy.deepcopy(one_node)
                    td = {}
                    for i, j in enumerate(text[QQlen * 3:(QQlen + 1) * 3]):
                        if i < 3:
                            td[f'{(QQlen + 1) * 3 + (i + 1)}st'] = j
                    msg["data"]["content"].append({'type': 'text', 'data': {'text': str(td)}})
                    msgs.append(copy.deepcopy(msg))
            await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=msgs)

        elif mode == 'S4' and set(args_dict.keys()).issubset({"main", "target", "duration", "sort"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}")
            text, msg = search_information(search="name", word=args_dict.pop("main"), **args_dict), copy.deepcopy(one_node)
            msg["data"]["content"].append({'type': 'text', 'data': {'text': str(text)}})
            await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=[msg])

        elif mode == 'S5' and set(args_dict.keys()).issubset({"main", "target", "duration", "sort", "ai", "start_date", "end_date", "page"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}")
            text, msg = search_information(search="tag", word=args_dict.pop("main"), **args_dict), copy.deepcopy(one_node)
            msg["data"]["content"].append({'type': 'text', 'data': {'text': str(text)}})
            await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=[msg])

        elif mode == 'D1' and set(args_dict.keys()).issubset({"main", "zip"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}\n\n" + "文件过多可能较慢，请耐心等待")
            paths = download_one_illust(pid=args_dict["main"], dirs=f'.\\data\\pixiv\\{UUID}')
            msgs = structure_node_t(organize_pixiv_data(paths), event)
            await bot.send_msg(message_type="group", group_id=event.group_id, message=msgs)

        elif mode == 'D2' and set(args_dict.keys()).issubset({"main", "zip"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}\n\n" + "文件过多可能较慢，请耐心等待")
            args_dict["zip"] = [True if "zip" not in args_dict.keys() else eval(args_dict["zip"])][0]
            paths = download_user_all_illusts(uid=args_dict["main"], dirs=f'.\\data\\pixiv\\{UUID}')
            if not args_dict["zip"]:
                msgs = structure_node(organize_pixiv_data(paths), one_node, event)
                await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=msgs)
            else:
                z_name = f".\\data\\{event.get_user_id()}.zip"
                create_zip(paths, z_name)
                await bot.send_msg(message_type="group", group_id=event.group_id, message=[{"type": "file", "data": {"url": os.path.abspath(z_name)}}])
                os.remove(z_name)

        elif mode == 'D3' and set(args_dict.keys()).issubset({"main", "zip"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}\n\n" + "文件过多可能较慢，请耐心等待")
            paths = download_users_news_illusts_by_name(name=args_dict["main"], dirs=f'.\\data\\pixiv\\{UUID}')
            msgs = structure_node_t(organize_pixiv_data(paths), event)
            await bot.send_msg(message_type="group", group_id=event.group_id, message=msgs)

        elif mode == 'D4' and set(args_dict.keys()).issubset({"main", "mode", "zip", "date", "filter", "offset", "req_auth"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}\n\n" + "文件过多可能较慢，请耐心等待")
            args_dict["zip"] = [True if "zip" not in args_dict.keys() else eval(args_dict["zip"])][0]
            paths = download_all_illusts_for_ranking(dirs=f'.\\data\\pixiv\\{UUID}', **{key: value for key, value in args_dict.items() if key != "main"})
            if not args_dict["zip"]:
                msgs = structure_node(organize_pixiv_data(paths), one_node, event)
                await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=msgs)
            else:
                z_name = f".\\data\\{event.get_user_id()}.zip"
                create_zip(paths, z_name)
                await bot.send_msg(message_type="group", group_id=event.group_id, message=[{"type": "file", "data": {"url": os.path.abspath(z_name)}}])
                os.remove(z_name)

        elif mode == 'D5' and set(args_dict.keys()).issubset({"main", "zip", "target", "duration", "sort", "ai", "start_date", "end_date", "page"}):
            await image.send(MessageSegment.at(event.get_user_id()) + f"\n\n调用功能：{mod}\n捕获参数：{args_save}\n\n" + "文件过多可能较慢，请耐心等待")
            args_dict["zip"] = [True if "zip" not in args_dict.keys() else eval(args_dict["zip"])][0]
            paths = download_page_illusts_for_tag(tag=args_dict.pop("main"), dirs=f'.\\data\\pixiv\\{UUID}', **args_dict)
            if not args_dict["zip"]:
                msgs = structure_node(organize_pixiv_data(paths), one_node, event)
                await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=msgs)
            else:
                z_name = f".\\data\\{event.get_user_id()}.zip"
                create_zip(paths, z_name)
                await bot.send_msg(message_type="group", group_id=event.group_id, message=[{"type": "file", "data": {"url": os.path.abspath(z_name)}}])
                os.remove(z_name)

        else:
            raise "Exception: 参数错误"
        shutil.rmtree(f'.\\data\\pixiv\\{UUID}')

    except FileNotFoundError:
        pass

    except FinishedException:
        traceback.print_exc()

    except:
        traceback.print_exc()
        await image.finish(MessageSegment.at(event.get_user_id()) + MessageSegment.text(" 看得出来你格式没填对啊"))
