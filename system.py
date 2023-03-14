import os.path

import AI
import _thread
import net
import console
import config
import json
from typing import List

AI_list: List[AI.AI] = []   # 或许应该加上本地文件备份功能

server_run = True


def add_AI(user: str, name="", owner_name="", prompt="", temperature=config.default_temperature) -> bool:
    for i in AI_list:
        if i.user == user:
            return False
    if prompt == "" and name == "":
        return False
    AI_list.append(AI.AI(user, name, owner_name, prompt, temperature))
    return True


def get_AI_index(user: str) -> int:
    for i in range(len(AI_list)):
        if AI_list[i].user == user:
            return i
    return -1


# 数据存读功能

def save_AI():
    for i in AI_list:
        data: dict = {"prompt": i.prompt, "messages": i.messages, "name": i.name, "owner_name": i.owner_name,
                      "user": i.user, "used_tokens": i.used_tokens, "temperature": i.temperature}
        data_str: str = json.dumps(data)
        f = open(config.data_path + "/" + i.user + ".ai", "w", encoding=config.coding_format)
        f.write(data_str)
        f.close()


def read_AI():
    files = os.listdir(config.data_path)
    for file in files:
        f = open(config.data_path + "/" + file, "r", encoding=config.coding_format)
        data_str = f.read()
        data = json.loads(data_str)
        ai = AI.AI()
        ai.prompt = data["prompt"]
        ai.messages = data["messages"]
        ai.name = data["name"]
        ai.owner_name = data["owner_name"]
        ai.user = data["user"]
        ai.used_tokens = data["used_tokens"]
        ai.temperature = data["temperature"]
        AI_list.append(ai)


# 初始化服务端
def init():
    if not os.path.exists(config.data_path):
        os.mkdir(config.data_path)
    read_AI()
    _thread.start_new_thread(net.start_server, ())
    console.start_console()
    save_AI()
