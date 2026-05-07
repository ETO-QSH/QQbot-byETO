from plugins.common import *

import httpx
import re

biliq_response = True
biliq = on_command("封面", rule=to_me())
biliq_cmd = on_command(("封面", "启用"), rule=to_me(), aliases={("封面", "禁用")}, permission=SUPERUSER)

CLEAN_HEADERS = {
    'sec-ch-ua-platform': '"Windows"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'content-type': 'application/json;charset=UTF-08',
    'sec-ch-ua-mobile': '?0',
    'accept': '*/*',
    'origin': 'https://www.bilibili.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.bilibili.com/',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'priority': 'u=1, i',
}


def bilibiliq(share_link):
    share_link = share_link.strip()
    if "BV" in share_link:
        ori_url = share_link.split("?")[0]
    else:
        short_url = re.search(r'https?://\S+', share_link)
        if not short_url:
            raise Exception("链接格式错误")
        with httpx.Client(follow_redirects=True, timeout=10, verify=False) as client:
            response = client.get(short_url.group(), headers=CLEAN_HEADERS)
            print(response.text)
            if response.status_code != 200:
                raise Exception("链接请求失败")
            ori_url = str(response.url).split("?")[0]

    bv_match = re.search(r'BV\w+', ori_url)
    if not bv_match:
        raise Exception("链接提取失败")
    bvid = bv_match.group()

    api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    with httpx.Client(follow_redirects=True, timeout=10, verify=False) as client:
        api_response = client.get(api_url, headers=CLEAN_HEADERS)
        data = api_response.json()

    if data.get("code") != 0:
        raise Exception("图片请求失败")
    return data["data"]["pic"]


@biliq_cmd.handle()
async def control(cmd: Tuple[str, str] = Command()):
    global biliq_response
    if cmd[1] == "启用":
        biliq_response = True
    elif cmd[1] == "禁用":
        biliq_response = False
    await biliq_cmd.finish(f"**封面插件已{cmd[1]}**")


@biliq.handle()
async def handle_function(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if biliq_response:
        if args.extract_plain_text():
            matcher.set_arg("location", args)
    else:
        await biliq.finish(f"封面插件已禁用，请联系管理员：{config.superusers}")


@biliq.got("location", prompt="请提供B站视频分享链接")
async def got_location(bot: Bot, event: Event, matcher: Matcher, location: str = ArgPlainText()):
    try:
        image_url = bilibiliq(location)
        await biliq.finish(MessageSegment.image(image_url))
    except FinishedException:
        pass
    except Exception as e:
        await biliq.finish(str(e))
