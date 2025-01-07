import ast
import copy
import json
import os
import cv2
import random
import re
import shutil
import traceback
import uuid
from itertools import chain
from typing import Tuple

import numpy as np
import requests

from plugins.PixivByETO.main import *

import nonebot
from nonebot import on_command, on_message, on_notice, on_fullmatch
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import MessageSegment, Message, Bot
from nonebot.exception import FinishedException
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg, Command
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from nonebot.exception import NetworkError

rps_dict = {}
dice_dict = {}
rps_ed = False
dice_ed = False
ing = on_message()
recall = on_notice()

rps_response = True
dice_response = True
file_response = True
video_response = True
image_response = True
gaoshu_response = True
hitokoto_response = True
educoder_response = True
xingzheng_response = True

at_me = on_message(rule=to_me())
dance = on_message(rule=to_me())
reaction = on_message(rule=to_me())
poke_notice = on_notice(rule=to_me())
rps = on_command("猜拳", rule=to_me())
dice = on_command("骰子", rule=to_me())
stop = on_command("安静", rule=to_me())
file = on_command("文件", rule=to_me())
image = on_command("图片", rule=to_me())
video = on_command("视频", rule=to_me())
hitokoto = on_command("一言", rule=to_me())
xingzheng = on_command("形政", rule=to_me())
educoder = on_command("头歌", rule=to_me())
gaoshu = on_command("高数", rule=to_me())

help = on_command("帮助", rule=to_me(), aliases={"-h", "help"})

rps_cmd = on_command(("猜拳", "启用"), rule=to_me(), aliases={("猜拳", "禁用")}, permission=SUPERUSER)
dice_cmd = on_command(("骰子", "启用"), rule=to_me(), aliases={("骰子", "禁用")}, permission=SUPERUSER)
file_cmd = on_command(("文件", "启用"), rule=to_me(), aliases={("文件", "禁用")}, permission=SUPERUSER)
image_cmd = on_command(("图片", "启用"), rule=to_me(), aliases={("图片", "禁用")}, permission=SUPERUSER)
video_cmd = on_command(("视频", "启用"), rule=to_me(), aliases={("视频", "禁用")}, permission=SUPERUSER)
hitokoto_cmd = on_command(("一言", "启用"), rule=to_me(), aliases={("一言", "禁用")}, permission=SUPERUSER)
educoder_cmd = on_command(("头歌", "启用"), rule=to_me(), aliases={("头歌", "禁用")}, permission=SUPERUSER)
xingzheng_cmd = on_command(("形政", "启用"), rule=to_me(), aliases={("形政", "禁用")}, permission=SUPERUSER)
gaoshu_cmd = on_command(("高数", "启用"), rule=to_me(), aliases={("高数", "禁用")}, permission=SUPERUSER)

config = nonebot.get_driver().config
one_node = {"type": "node", "data": {"user_id": "3078491964", "nickname": "ETO", "content": []}}


@at_me.handle()
async def at_bot(event: Event):
    if '<le>[at:qq=3078491964' in str(event.get_log_string()) and str(event.get_message()) == '' and 'reply:id=' not in str(event.get_log_string()):
        await at_me.finish("꒰ঌ( ⌯' '⌯)໒꒱")

@recall.handle()
async def sbRecall(bot: Bot, event: Event):
    try:
        msg_id = str(ast.literal_eval(event.get_event_description())['message_id'])
        if msg_id in rps_dict:
            if rps_dict[msg_id] != None:
                await bot.delete_msg(message_id=rps_dict[msg_id])
            del rps_dict[msg_id]
        if msg_id in dice_dict:
            if dice_dict[msg_id] != None:
                await bot.delete_msg(message_id=dice_dict[msg_id])
            del dice_dict[msg_id]
        await recall.finish()
    except Exception as e:
        await recall.finish()

@poke_notice.handle()
async def send_emoji(bot: Bot, event: Event):
    if event.notice_type == 'notify' and event.sub_type == 'poke':
        if str(event.group_id) in ["797784653", "981535936"] and gaoshu_response:
            Information = read_json(r'理工学堂\高等数学.json')
            files = find_paths(r'D:\Desktop\Desktop\高等数学 (ID_42)', 'png')
            file = random.choice(files)
            file_name = os.path.basename(file).split('.')[0]
            path_name = os.path.basename(os.path.dirname(os.path.dirname(file))).split()[0]
            info = Information[path_name][file_name][0]
            await poke_notice.finish(MessageSegment.image(file) + f"发送 `ETO 高数 {info}` 获取答案")
        else:
            custom_faces = await bot.call_api("fetch_custom_face")
            await bot.send_group_msg(group_id=event.group_id, message=MessageSegment.image(file=custom_faces[0]))

@reaction.handle()
async def reply(bot: Bot, event: Event):
    if '<le>[reply:id=' in event.get_log_string():
        ID = re.search(r'reply:id=(\d+)', event.get_log_string()).group(1)
        # 这里这个api存在问题，下次再改
        # await bot.set_group_reaction(group_id=event.group_id, message_id=ID, code='2', is_add=True)
        if str(event.get_message()).strip() == '搜题':
            get_msg = await bot.get_msg(message_id=ID)
            if len(get_msg['message']) == 1 and get_msg['message'][0]['type'] == 'image':
                url = get_msg['message'][0]['data']['url']
                file_path = f'reaction_temp\\{event.group_id}_{event.get_user_id()}_{datetime.now().strftime("%H%M%S")}.jpg'
                try: download_image(url, file_path)
                except Exception as e: await reaction.finish('图片下载失败。。。')
                c = search_TM(file_path)
                os.remove(file_path)
                await reaction.finish(MessageSegment.at(event.get_user_id()) + c)
        await reaction.finish('看不懂喵 ฅ( ̳• · • ̳ฅ)')
    await reaction.finish()

@dance.handle()
async def send_emoji(bot: Bot, event: Event):
    if '跳舞' in str(event.get_message()):
        custom_faces = await bot.call_api("fetch_custom_face")
        await bot.send_group_msg(group_id=event.group_id, message=MessageSegment.image(file=custom_faces[1]))

@stop.handle()
async def control():
    global rps_ed, dice_ed
    rps_ed = False
    dice_ed = False
    await stop.finish(f"**猜拳骰子已关闭**")

@help.handle()
async def help_eto(event: Event):
    help_msg = f'''
欢迎使用我搭建的群机器人！
目前，我实现了以下的功能：

1. [文件]--发送列表中的本地文件
2. [图片]--本地图片以及pixiv接口
3. [视频]--发送列表中的本地视频
4. [一言]--发送本地库中的语句
5. [头歌]--发送py编程作业的答案
6. [形政]--发送形政考试答案
7. [高数]--发送高数作业答案

你可以通过这些关键字访问功能
例如：`ETO 一言`
如此会返回更详细的信息
(此外还连接了戳一戳互动什么的)

项目的管理者为 {config.superusers}
如有需求和或者bug都可以反馈'''
    await help.finish(MessageSegment.at(event.get_user_id())+help_msg)


@rps_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global rps_response
    if cmd[1] == "启用":
        rps_response = True
    elif cmd[1] == "禁用":
        rps_response = False
    await rps_cmd.finish(f"**猜拳插件已{cmd[1]}**")

@dice_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global dice_response
    if cmd[1] == "启用":
        dice_response = True
    elif cmd[1] == "禁用":
        dice_response = False
    await dice_cmd.finish(f"**骰子插件已{cmd[1]}**")

@file_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global file_response
    if cmd[1] == "启用":
        file_response = True
    elif cmd[1] == "禁用":
        file_response = False
    await file_cmd.finish(f"**文件插件已{cmd[1]}**")

@image_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global image_response
    if cmd[1] == "启用":
        image_response = True
    elif cmd[1] == "禁用":
        image_response = False
    await image_cmd.finish(f"**图片插件已{cmd[1]}**")

@video_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global video_response
    if cmd[1] == "启用":
        video_response = True
    elif cmd[1] == "禁用":
        video_response = False
    await video_cmd.finish(f"**视频插件已{cmd[1]}**")

@hitokoto_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global hitokoto_response
    if cmd[1] == "启用":
        hitokoto_response = True
    elif cmd[1] == "禁用":
        hitokoto_response = False
    await hitokoto_cmd.finish(f"**一言插件已{cmd[1]}**")

@educoder_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global educoder_response
    if cmd[1] == "启用":
        educoder_response = True
    elif cmd[1] == "禁用":
        educoder_response = False
    await educoder_cmd.finish(f"**头歌插件已{cmd[1]}**")

@xingzheng_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global xingzheng_response
    if cmd[1] == "启用":
        xingzheng_response = True
    elif cmd[1] == "禁用":
        xingzheng_response = False
    await xingzheng_cmd.finish(f"**形政插件已{cmd[1]}**")

@gaoshu_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global gaoshu_response
    if cmd[1] == "启用":
        gaoshu_response = True
    elif cmd[1] == "禁用":
        gaoshu_response = False
    await gaoshu_cmd.finish(f"**高数插件已{cmd[1]}**")


def random_file(DIRS):
    files = list(chain(*[[os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))] for dir in DIRS]))
    return random.choice(files)

def read_json(JSON):
    with open(JSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def read_txt(TXT):
    with open(TXT, 'r', encoding='utf-8') as file:
        data = file.read()
    return data

def cv_imread(filePath):
    cv_img = cv2.imdecode(np.fromfile(filePath, dtype=np.uint8), -1)
    return cv_img

def create_zip(paths, z_name):
    paths = [os.path.dirname(os.path.dirname(path))+'.zip' for path in paths]
    with zipfile.ZipFile(z_name, 'w') as zipf:
        for path in paths:
            abs_path = os.path.abspath(path)
            zipf.write(abs_path, os.path.basename(abs_path))

def work_paths(PATH):
    data = {}
    for root, dirs, files in os.walk(PATH):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            data[file_name] = file_path
    return data

def find_paths(directory, endswith):
    lst = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(endswith):
                lst.append(os.path.join(root, file))
    return lst

def download_image(url, file_path):
    os.system(f'curl -k "{url}" -o "{os.path.abspath(file_path)}"')

def organize_pixiv_data(paths):
    def H2C(s):
        return re.sub(r'`0x([0-9a-fA-F]{2})`', lambda match: chr(int(match.group(1), 16)), s)
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

def find_max_similarity_TM(image_path, folder_lst):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 0, 251]), np.array([255, 4, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    target_roi = image[y:y+h, x:x+w]
    max_s, max_p = 0, None
    for image_path in folder_lst:
        image = cv_imread(image_path)
        image_height, image_width = image.shape[:2]
        if w > image_width or h > image_height:
            scale = min(image_width / w, image_height / h)
            rtr = cv2.resize(target_roi, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        else: rtr = cv2.resize(target_roi, (w, h), interpolation=cv2.INTER_AREA)
        if len(image.shape) == 3: image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(rtr.shape) == 3: rtr = cv2.cvtColor(rtr, cv2.COLOR_BGR2GRAY)
        max_i = np.max(cv2.matchTemplate(image, rtr, cv2.TM_CCOEFF_NORMED))
        if max_i > max_s: max_s, max_p = max_i, image_path
    return max_s, max_p

def search_TM(image_path):
    Information = read_json(r'理工学堂\高等数学.json')
    files = find_paths(r'D:\Desktop\Desktop\高等数学 (ID_42)', 'png')
    try:
        max_s, max_p = find_max_similarity_TM(image_path, files)
        if max_s > 0.5:
            file_name = os.path.basename(max_p).split('.')[0]
            path_name = os.path.basename(os.path.dirname(os.path.dirname(max_p))).split()[0]
            info = Information[path_name][file_name][0]
            Information, result = read_json(r'理工学堂\高等数学.json'), None
            for chapter_key, chapter_data in Information.items():
                for question_key, question_data in chapter_data.items():
                    if question_data[0] == info: result = question_data[1]; break
                if result: return f'\n相似度: {max_s*100:.2f}%\n编号: {info}  答案: {result}'
        else: return '相似度过低，未成功匹配结果！'
    except Exception as e:
        return '相似度过低，未成功匹配结果！'


@educoder.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if educoder_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await educoder.finish(f"头歌插件已禁用，请联系管理员：{config.superusers}")

@educoder.got("location", prompt="请给予更多信息：{理论|实践}课-第{N}章-第{n}题\n例：`实践课第三章第9题`")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    date = read_json("educoder.json")
    match = re.search(r"(理论|实践)课.*第([\u4e00-\u9fa5]+)章.*第(\d+)题", location)
    try:
        msg1, msg2, msg3, file = copy.deepcopy(one_node), copy.deepcopy(one_node), copy.deepcopy(one_node), date["educoder"][match.group(1)][match.group(2)][match.group(3)][0]
        msg1["data"]["content"].append({"type": "at", "data": {'qq': str(event.get_user_id()), 'name': event.sender.nickname}})
        msg2["data"]["content"].append({'type': 'text', 'data': {'text': f"{match.group(1)}课第{match.group(2)}章第{match.group(3)}题"}})
        msg3["data"]["content"].append({'type': 'text', 'data': {'text': read_txt(file)}})
        await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=[msg1, msg2, msg3])
    except FinishedException:
        pass
    except:
        await educoder.finish(f"没有`{location}`数据，原因不外乎我没写我没传你打错了，请先检查输入")


@xingzheng.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if xingzheng_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await xingzheng.finish(f"形政插件已禁用，请联系管理员：{config.superusers}")

@xingzheng.got("location", prompt="请给予题干片段")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    date = read_json("形式与政策.json")
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


@gaoshu.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if gaoshu_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await gaoshu.finish(f"高数插件已禁用，请联系管理员：{config.superusers}")

@gaoshu.got("location", prompt="请给予更多信息：{理论|实践}课-第{N}章-第{n}题\n例：`实践课第三章第9题`")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    data, result = read_json(r'理工学堂\高等数学.json'), None
    for chapter_key, chapter_data in data.items():
        for question_key, question_data in chapter_data.items():
            if question_data[0] == location:
                result = question_data[1]
                break
        if result: break
    if gaoshu_response:
        if result:
            await gaoshu.finish(MessageSegment.at(event.get_user_id()) + f"\n高数 {location}：{result}")
        else:
            await gaoshu.finish(f"好好复制喵 ~")

@hitokoto.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if hitokoto_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await hitokoto.finish(f"一言插件已禁用，请联系管理员：{config.superusers}")

@hitokoto.got("location", prompt=f'请选择句子类型：{list(read_json("hitokoto.json")["sentences"].keys())}')
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    date = read_json("hitokoto.json")
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


@rps.handle()
async def handle_function():
    global rps_ed
    if rps_response:
        rps_ed = True
        await rps.finish("拥有败者食尘，喵喵是不会输的！")
    else:
        await rps.finish(f"猜拳插件已禁用，请联系管理员：{config.superusers}")

@dice.handle()
async def handle_function():
    global dice_ed
    if dice_response:
        dice_ed = True
        await dice.finish("拥有败者食尘，喵喵是不会输的！")
    else:
        await dice.finish(f"骰子插件已禁用，请联系管理员：{config.superusers}")

@ing.handle()
async def handle_ing(bot: Bot, event: Event):
    if rps_ed:
        text = event.get_log_string()
        if "<le>[rps:result=" in text:
            match = re.search(r'<le>\[rps:result=(\d+)', text)
            if match:
                #image_url = "https://i.pixiv.cat/img-master/img/2020/03/25/00/00/08/80334602_p0_master1200.jpg"
                #xml = f"""<?xml version="1.0" encoding="UTF-8"?>
                #          <msg>
                #              <type>
                #                  image
                #              </type>
                #              <image>
                #                  <file>{image_url}</file>
                #              </image>
                #          </msg>"""
                #
                #send_msg_data = {
                #    "type": "xml",
                #    "data": {
                #        "data": xml
                #    }
                #}
                #
                #await bot.call_api(api="send_msg", group_id=event.group_id, **send_msg_data)

                ID = re.search(r'Message (\d+)', text).group(1)
                ddd = {'1': '2', '2': '3', '3': '1'}
                result = match.group(1)
                rps_dict[ID] = None

                while ID in rps_dict:
                    rps_segment = Message(MessageSegment.rps())
                    msg_id = await bot.send_msg(message_type="group", group_id=event.group_id, message=rps_segment)
                    get_msg = await bot.get_msg(message_id=msg_id['message_id'])
                    true_result = get_msg['message'][0]['data']['result']
                    if true_result == ddd[result]:
                        rps_dict[ID] = msg_id['message_id']
                        break
                    else:
                        await bot.delete_msg(message_id=msg_id['message_id'])
                await hitokoto.finish()

    # 这里懒得改了，写法和上面一样
    if dice_ed:
        text = event.get_log_string()
        if "<le>[dice:result=" in text:
            match = re.search(r'<le>\[dice:result=(\d+)', text)
            print(match.group(1))
            if match:
                dice_segment = MessageSegment.dice()
                dice_segment.data = {'result': '6'}
                await hitokoto.finish(dice_segment)


@video.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if video_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await video.finish(f"视频插件已禁用，请联系管理员：{config.superusers}")

@video.got("location", prompt="\n\n".join(["请提供视频序号："] + [f'Serial:{i} | name:{item["name"]} | tag:{item["tag"]}' for i, item in read_json("video.json")["midishow"].items()]))
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    try:
        if "+" in location:
            locate = read_json("video.json")["midishow"][location[:-1]]
            await video.send(MessageSegment.at(event.get_user_id()) + '\n' + f"更多信息：{str(locate)}")
            await video.finish(MessageSegment.video(locate["url"]))
        else:
            locate = read_json("video.json")["midishow"][location]
            await video.send(MessageSegment.at(event.get_user_id()))
            await video.finish(MessageSegment.video(locate["url"]))
    except FinishedException:
        pass
    except:
        await video.finish("不是喵，怎么有人序号填不好")


@file.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if file_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await file.finish(f"文件插件已禁用，请联系管理员：{config.superusers}")

@file.got("location", prompt='文件列表（很大!=很慢）：\n\n'+"\n\n".join([f"{i+1}. {file}" for i, file in enumerate(work_paths("D:\Images\文件").keys())]))
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    data = work_paths("D:\Images\文件")
    try:
        if int(location) in range(1, len(data)+1):
            await bot.send_msg(message_type="group", group_id=event.group_id, message=[{"type": "file", "data": {"url": data[list(data.keys())[int(location)-1]]}}])
        else:
            raise ("Exception: 未知文件")
    except FinishedException:
        pass
    except NetworkError:
        pass
    except:
        await file.finish(f"不是喵，怎么有人序号填不好")


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
            await image.finish(MessageSegment.at(event.get_user_id()) + MessageSegment.image(random_file([r"D:\Images\图片", r"D:\Desktop\Desktop\new-pic"])))
        elif location == "pixiv":
            if event.get_user_id() in config.superusers:
                matcher.got("mode")
            else:
                # await image.send("悠着点用，接口那边也是我写的，纲领是能跑就行，暂时不支持异步，而且因为需要代理，以及使用我的账号，可能出现一些问题。如果需要良好的下载环境，可以在我的github中找到独立的pixiv接口")
                # await image.finish("测试阶段权限还未开启")
                await image.finish("刚禁的别想了的说")
                matcher.got("mode")
        else:
            raise ("Exception: 未知源")
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
    mod = {"S1": "插画信息", "S2": "用户作品", "S3": "榜单查询", "S4": "用户查找", "S5": "标签查询", "D1": "下载单个插画", "D2": "下载用户所有作品", "D3": "下载匹配用户名最新作品", "D4": "下载指定榜单所有作品", "D5": "下载标签下指定页作品"}[mode]
    matches, args_dict = re.findall(r'#(.*?)#', args), {}
    for match in matches:
        if ':' in match:
            key, value = match.split(':', 1)
            args_dict[key] = value
        else:
            args_dict["main"] = match
    try:
        if not args_dict:
            raise ("Exception: 没有参数")
        elif mode in ["S3", "D4"]:
            if not args_dict:
                raise ("Exception: 参数错误")
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
            for QQlen in range((len(text)+2)//3):
                if QQlen < 10:
                    msg = copy.deepcopy(one_node)
                    td = {}
                    for i, j in enumerate(text[QQlen*3:(QQlen+1)*3]):
                        if i < 3:
                            td[f'{(QQlen+1)*3+(i+1)}st'] = j
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
            if args_dict["zip"] == False:
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
            if args_dict["zip"] == False:
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
            if args_dict["zip"] == False:
                msgs = structure_node(organize_pixiv_data(paths), one_node, event)
                await bot.call_api(api="send_group_forward_msg", group_id=event.group_id, messages=msgs)
            else:
                z_name = f".\\data\\{event.get_user_id()}.zip"
                create_zip(paths, z_name)
                await bot.send_msg(message_type="group", group_id=event.group_id, message=[{"type": "file", "data": {"url": os.path.abspath(z_name)}}])
                os.remove(z_name)
        else:
            raise ("Exception: 参数错误")
        shutil.rmtree(f'.\\data\\pixiv\\{UUID}')
    except FileNotFoundError:
        pass
    except FinishedException:
        traceback.print_exc()
    except:
        traceback.print_exc()
        await image.finish(MessageSegment.at(event.get_user_id()) + MessageSegment.text(" 看得出来你格式没填对啊"))

