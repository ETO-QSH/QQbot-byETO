from plugins.common import *


gaoshu_response = True
reaction = on_message(rule=to_me())
gaoshu = on_command("高数", rule=to_me())
gaoshu_cmd = on_command(("高数", "启用"), rule=to_me(), aliases={("高数", "禁用")}, permission=SUPERUSER)


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
        else:
            rtr = cv2.resize(target_roi, (w, h), interpolation=cv2.INTER_AREA)
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(rtr.shape) == 3:
            rtr = cv2.cvtColor(rtr, cv2.COLOR_BGR2GRAY)
        max_i = np.max(cv2.matchTemplate(image, rtr, cv2.TM_CCOEFF_NORMED))
        if max_i > max_s:
            max_s, max_p = max_i, image_path
    return max_s, max_p


def search_TM(image_path):
    Information = read_json(r'理工学堂\高等数学.json')
    files = find_paths(r'理工学堂\高等数学 (ID_42)', 'png')
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
                if result:
                    return f'\n相似度: {max_s*100:.2f}%\n编号: {info}  答案: {result}'
        else:
            return '相似度过低，未成功匹配结果！'
    except Exception as e:
        return '相似度过低，未成功匹配结果！'


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
                file_path = f'data\\reaction_temp\\{event.group_id}_{event.get_user_id()}_{datetime.now().strftime("%H%M%S")}.jpg'
                try:
                    download_image(url, file_path)
                except Exception as e:
                    await reaction.finish('图片下载失败。。。')
                c = search_TM(file_path)
                os.remove(file_path)
                await reaction.finish(MessageSegment.at(event.get_user_id()) + c)
        await reaction.finish('看不懂喵 ฅ( ̳• · • ̳ฅ)')
    await reaction.finish()


@gaoshu_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global gaoshu_response
    if cmd[1] == "启用":
        gaoshu_response = True
    elif cmd[1] == "禁用":
        gaoshu_response = False
    await gaoshu_cmd.finish(f"**高数插件已{cmd[1]}**")


@gaoshu.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if gaoshu_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await gaoshu.finish(f"高数插件已禁用，请联系管理员：{config.superusers}")


@gaoshu.got("location", prompt="")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    data, result = read_json(r'理工学堂\高等数学.json'), None
    for chapter_key, chapter_data in data.items():
        for question_key, question_data in chapter_data.items():
            if question_data[0] == location:
                result = question_data[1]
                break
        if result:
            break
    if gaoshu_response:
        if result:
            await gaoshu.finish(MessageSegment.at(event.get_user_id()) + f"\n高数 {location}：{result}")
        else:
            await gaoshu.finish(f"好好复制喵 ~")
