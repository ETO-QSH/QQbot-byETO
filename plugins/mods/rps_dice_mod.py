from plugins.common import *


rps_dict = {}
dice_dict = {}
rps_ed = False
dice_ed = False

ing = on_message()
recall = on_notice()
stop = on_command("安静", rule=to_me())

rps_response = True
dice_response = True
rps = on_command("猜拳", rule=to_me())
dice = on_command("骰子", rule=to_me())
rps_cmd = on_command(("猜拳", "启用"), rule=to_me(), aliases={("猜拳", "禁用")}, permission=SUPERUSER)
dice_cmd = on_command(("骰子", "启用"), rule=to_me(), aliases={("骰子", "禁用")}, permission=SUPERUSER)


@stop.handle()
async def control():
    global rps_ed, dice_ed
    rps_ed = False
    dice_ed = False
    await stop.finish(f"**猜拳骰子已关闭**")


@recall.handle()
async def sbRecall(bot: Bot, event: Event):
    try:
        msg_id = str(ast.literal_eval(event.get_event_description())['message_id'])
        if msg_id in rps_dict:
            if rps_dict[msg_id]:
                await bot.delete_msg(message_id=rps_dict[msg_id])
            del rps_dict[msg_id]
        if msg_id in dice_dict:
            if dice_dict[msg_id]:
                await bot.delete_msg(message_id=dice_dict[msg_id])
            del dice_dict[msg_id]
        await recall.finish()
    except Exception as e:
        await recall.finish()


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
                # image_url = "https://i.pixiv.cat/img-master/img/2020/03/25/00/00/08/80334602_p0_master1200.jpg"
                # xml = f"""<?xml version="1.0" encoding="UTF-8"?>
                #           <msg>
                #               <type>
                #                   image
                #               </type>
                #               <image>
                #                   <file>{image_url}</file>
                #               </image>
                #           </msg>"""
                #
                # send_msg_data = {
                #     "type": "xml",
                #     "data": {
                #         "data": xml
                #     }
                # }
                #
                # await bot.call_api(api="send_msg", group_id=event.group_id, **send_msg_data)

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
                await ing.finish()

    # 这里懒得改了，写法和上面一样
    if dice_ed:
        text = event.get_log_string()
        if "<le>[dice:result=" in text:
            match = re.search(r'<le>\[dice:result=(\d+)', text)
            print(match.group(1))
            if match:
                dice_segment = MessageSegment.dice()
                dice_segment.data = {'result': '6'}
                await ing.finish(dice_segment)
