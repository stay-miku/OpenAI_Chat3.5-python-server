import os
import time
from typing import List

try:
    import openai
except ModuleNotFoundError:
    os.system("pip install openai")     # 自动配置库
    import openai

import config

# 基本变量的初始化
openai.api_key = config.api_key
select_model = config.select_model
default_temperature = config.default_temperature


class AI:
    prompt: str  # 设定提示词                             需要可被修改和获取 √ √
    messages: List[dict]  # 历史消息,第一条为提示词         可以被间接操作
    name: str  # ai名字,用于生成提示词,自定义提示词此条无效     需要可被修改和获取 √ √
    owner_name: str  # 主人名字,同name                    需要可被修改和获取 √ √
    user: str  # 唯一关键字,判断ai所有者
    used_tokens: int  # 已使用的token                     需要可被获取 √
    temperature: float  # 温度,用于设定回答与提问的相关度,越大越不相关,值为0-2           需要可被修改和获取 √ √
    operable: bool

    # 在等待ai回复时所有操作(除了get型)都会被锁住(防止奇怪的问题出现)
    def pre_operable(self):
        while self.operable:
            time.sleep(0.05)

    def get_name(self) -> str:                   # client发送user  server发送name     所有返回变量的协议都可能因user错误而返回false
        return self.name

    def set_name(self, name):                    # client发送user和name  server发送成功
        self.pre_operable()
        self.name = name
        self.set_default_prompt()

    def get_owner_name(self) -> str:            # client发送user   server返回owner_name
        return self.owner_name

    def set_owner_name(self, owner_name):        # client发送user和owner_name  server返回成功
        self.pre_operable()
        self.owner_name = owner_name
        self.set_default_prompt()

    def get_used_token(self) -> int:             # client发送user  server返回str的used_tokens
        return self.used_tokens

    def get_temperature(self) -> float:          # client发送user  server发送str的temperature
        return self.temperature

    # 不填及使用默认值,prompt为默认值时name不可为默认值,反之亦然                   (直接客户端给限制死了,能填的就只有name和owner_name)
    def __init__(self, user="", name="", owner_name="", prompt="", temperature=default_temperature):  # create  client依次发送user name owner_name(懒~) 空参数发空字符串  server返回是否成功
        self.operable = False
        if user == "":  # 代表空的构造函数,用于从文件恢复对象
            return

        # 底下才是真正的构造函数内容
        self.user = user
        self.name = name
        self.owner_name = owner_name
        self.temperature = temperature
        self.messages = []
        if prompt == "":
            self.set_default_prompt()
        else:
            self.set_prompt(prompt)
        self.used_tokens = 0

    # 清除超过长度限制的对话
    def clear_extre_message(self):
        while True:
            if len(self.messages) - 1 <= config.max_message_length:
                break
            else:
                self.messages.pop(1)

    # 清除所有对话记录  *
    def clear(self):                                                                                   # clear   client发送user  server返回成功
        self.pre_operable()
        self.messages = []
        self.messages.append({"role": "user", "content": self.prompt})

    # 修改prompt,会调用clear  **
    def set_prompt(self, prompt):                                                                      # set_prompt   client发送user和prompt  server返回成功
        self.pre_operable()
        self.prompt = prompt
        self.clear()

    # 重设为默认prompt,name需存在(客户端不允许给定空的name,所以问题不大),会调用clear  *
    def set_default_prompt(self):                                                                      # set_default_prompt    client发送user  server返回成功
        self.pre_operable()
        self.set_prompt(config.get_neko_prompt(self.name, self.owner_name))

    # 重设温度
    def set_temperature(self, temperature: float):                                                     # set_temperature   client发送user和str型temperature  server返回成功
        self.pre_operable()
        self.temperature = temperature

    # 获取历史消息数组
    def get_messages(self) -> List[str]:                                                               # none
        if len(self.messages) <= 1:
            return []
        else:
            re = []
            temp = True
            for message in self.messages:
                if temp:
                    temp = False
                    continue
                re.append(message["content"])
            return re

    def get_prompt(self) -> str:                                                                      # get_prompt  client发送user server返回prompt
        return self.prompt

    # 让ai"听"说的话
    def listen(self, question: str):                                                                  # listen  client发送user和question   server返回成功
        self.pre_operable()
        self.messages.append({"role": "user", "content": question})
        self.clear_extre_message()

    # 撤销上一个语句,不论是ai说的还是用户说的,返回撤销的值
    def revoke(self) -> dict:                                                                         # revoke  client发送user  server返回role和content
        self.pre_operable()
        if len(self.messages) > 1:
            return self.messages.pop()
        return {}

    # 让ai说话  注意返回值是否error  一个速度限制error 一个网络错误error
    def speak(self) -> str:                                                                           # speak  client发送user  server返回answer  error也会返回,需client自行判断error
        self.pre_operable()
        self.operable = True
        try:
            resp = openai.ChatCompletion.create(model=select_model, messages=self.messages,
                                                temperature=self.temperature)
        except openai.error.RateLimitError:     # 需要单独判断是否触发api速度限制
            self.operable = False
            return "error: limit error"
        except Exception as e:
            print(e)
            self.operable = False
            return "error: network error"
        message = resp["choices"][0]["message"]["content"]
        self.used_tokens = self.used_tokens + resp["usage"]["total_tokens"]
        self.messages.append({"role": "assistant", "content": message})
        self.clear_extre_message()
        self.operable = False
        return message

    # 输入问题,给出答案   error同speak
    def chat(self, question: str) -> str:                                                            # chat  client发送user和question  server返回answer  error同speak
        self.pre_operable()
        self.listen(question)
        message = self.speak()
        if message.startswith("error"):
            self.revoke()
            return message
        else:
            return message

    # 手动设置一个回答 预设一个想要的回答要比设置提示词的效果好得多
    def set_speak(self, answer: str):                                                               # set_speak  client发送user和answer  server返回成功
        self.pre_operable()
        self.messages.append({"role": "assistant", "content": answer})
        self.clear_extre_message()

    # 手动设置一个问答
    def set_chat(self, question: str, answer: str):                                                 # set_chat   client发送user、question和answer   server返回成功
        self.pre_operable()
        self.listen(question)
        self.set_speak(answer)

    # 重新生成对话  比speak多一个非assistant error
    def re_chat(self) -> str:                                                                       # re_chat   client发送user  server返回answer  error同speak
        self.pre_operable()
        if self.messages[len(self.messages) - 1]["role"] != "assistant":
            return "error: is not assistant"
        last = self.revoke()
        messages = self.speak()
        if messages.startswith("error"):
            self.messages.append(last)
            return messages
        else:
            return messages
