from plugins.common import *
from deepseek_api.main import ChatSystem


with open("deepseek_api\\src\\api_key", "r") as api:
    chat_system = ChatSystem(api.read())


async def ai_fallback(user_id, message, meta, data):
    more = f"工具信息: {meta}。" + f"后端接口: {data}。" \
        "如果用户对其中一些工具的用法表示困惑你就感觉工具信息以及后端接口的代码告知用户如何正确使用。" \
        "如果用户需求比较完整的功能帮助，你应该先输出工具信息的完整内容，然后根据后端接口里面的信息告诉用户你的理解。"
    response = await chat_system.handle_request(
        service_key="BOT",
        user_info=user_id,
        user_state="已认证",
        user_input=message,
        more=more
    )
    print(f"\n又亏了这么多钱: {chat_system.get_metrics()['api_usage']['total_cost']}")
    return response["response"]
