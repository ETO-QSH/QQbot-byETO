import ast, copy, copy, cv2, json, os, random, re, requests, shutil, traceback, uuid, zipfile

import numpy as np
from curl_cffi import requests
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Tuple


import nonebot
from nonebot import on_command, on_message, on_notice, on_fullmatch
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import MessageSegment, Message, Bot
from nonebot.exception import FinishedException, NetworkError
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg, Command
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

config = nonebot.get_driver().config
one_node = {"type": "node", "data": {"user_id": "3078491964", "nickname": "ETO", "content": []}}


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
    paths = [os.path.dirname(os.path.dirname(path)) + '.zip' for path in paths]
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
    # response = requests.get(url, verify=False)
    # if response.status_code == 200:
    #     with open(os.path.abspath(file_path), 'wb') as file:
    #         file.write(response.content)
    #     print(f"文件已保存到 {os.path.abspath(file_path)}")
    # else:
    #     print(f"请求失败，状态码：{response.status_code}")
    os.system(f'curl -k "{url}" -o "{os.path.abspath(file_path)}"')
