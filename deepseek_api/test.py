from datetime import datetime
from openai import OpenAI
import json

api_key = "sk-0fe275a9ac124cc3a39196707db9c205"
user_info = "2373204754"
user_state = "已认证"
service_key = "WUT"

def read_json_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data


client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

Search_Json = {
    "Type": "[课程安排|考试安排|成绩查询], 根据用户需求可以多选, 以列表形式",
    "Time": "{当前时间}, 按照'%Y-%m-%d %H:%M:%S'格式的时间",
    "Update": "{数据更新需要[true|false]}, 默认不更新"
}

Service = {
    "WUT": "为已认证用户提供简单的个人信息查询服务，以及基础知识的问答，"
           "回答应该简短并且礼貌，执行查询服务时，从用户的信息中理解用户的需求"
           "整理为以下Json格式: {}".format(str(Search_Json)),
           "而后我会请求文件，你再依照内容进行回复"
    "BOT": "陪用户闲聊，依照用户需求进行互动，回答应该简短并且礼貌",
    "ETO": "尽可能帮助用户解决问题，做到详细清晰"
}

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system",
         "content": f"""当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                        你的身份: 由 'Dr.ETO' 搭建的 'deepseek v3' 语言模型接口
                        交流语言: 默认中文，如果用户有特殊要求，可以依照需求
                        你的工作: {Service[service_key]}
                        用户状态: {user_state}
                        用户信息: {user_info}"""},
        {"role": "user", "content": "Hello"},
    ],
    max_tokens=1024,
    temperature=0.7,
    stream=False
)

print(response.choices[0].message.content)
