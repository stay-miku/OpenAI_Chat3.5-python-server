import config
import _thread

import immerse
import system
import socket

# 双端通信协议(应该设个类的,太傻了)


def log(addr: str, error: str):
    print("[log]: " + addr + " " + error)


def get_int(server: socket.socket) -> int:
    i = server.recv(4)
    return int.from_bytes(i, byteorder=config.byteorder)


def get_string(server: socket.socket) -> str:
    length = get_int(server)
    content = server.recv(length)
    return content.decode(config.coding_format)


def send_int(server: socket.socket, i: int):
    server.send(i.to_bytes(4, byteorder=config.byteorder))


def send_string(server: socket.socket, i: str):
    b_i = i.encode(config.coding_format)
    send_int(server, len(b_i))
    server.send(b_i)


def send_true(server: socket.socket):   # 客户端封装个判断成功失败的函数
    send_string(server, "true")


def send_false(server: socket.socket):
    send_string(server, "false")


def connect_hello(server: socket.socket) -> bool:
    if server.recv(9) != b'gpt_hello':
        return False
    server.send(b'gpt_hello')
    return True


# 相应的处理函数,相关流程见AI.py        应该预处理user的!我是傻子   后悔没写成一个类了,手动填server填到麻
# 让可以被get的参数的内容不允许为false
# 给了最大限度的自定义权就不需要delete功能了

def type_create(server: socket.socket, user: str):  # ok
    name = get_string(server)
    owner_name = get_string(server)
    if system.add_AI(user, name, owner_name):
        send_true(server)  # 虽然true false type啥的可以用一个数字代替 但我就要用字符串!
    else:
        send_false(server)


def type_clear(server: socket.socket, index: int):   # ok
    system.AI_list[index].clear()
    send_true(server)


def type_set_prompt(server: socket.socket, index: int):   # ok
    prompt = get_string(server)
    system.AI_list[index].set_prompt(prompt)
    send_true(server)


def type_set_default_prompt(server: socket.socket, index: int):   # ok
    system.AI_list[index].set_default_prompt()
    send_true(server)


def type_set_temperature(server: socket.socket, index: int):   # ok
    temperature = get_string(server)
    system.AI_list[index].set_temperature(float(temperature))
    send_true(server)


def type_get_prompt(server: socket.socket, index: int):   # ok
    send_string(server, system.AI_list[index].get_prompt())


def type_listen(server: socket.socket, index: int):   # ok
    question = get_string(server)
    system.AI_list[index].listen(question)
    send_true(server)


def type_revoke(server: socket.socket, index: int):   # ok
    r = system.AI_list[index].revoke()
    if r == {}:
        send_string(server, "empty")    # 注意判断
        send_string(server, "empty")
    else:
        send_string(server, r["role"])
        send_string(server, r["content"])


def type_speak(server: socket.socket, index: int):   # ok
    send_string(server, system.AI_list[index].speak())  # 需判断error


def type_chat(server: socket.socket, index: int):  # 这里就不复用代码了(毕竟流程会多一步返回)    # ok
    question = get_string(server)
    send_string(server, system.AI_list[index].chat(question))  # 需判断error


def type_set_speak(server: socket.socket, index: int):   # ok
    answer = get_string(server)
    system.AI_list[index].set_speak(answer)
    send_true(server)


def type_set_chat(server: socket.socket, index: int):   # ok
    question = get_string(server)
    answer = get_string(server)
    system.AI_list[index].set_chat(question, answer)
    send_true(server)


def type_re_chat(server: socket.socket, index: int):   # ok
    send_string(server, system.AI_list[index].re_chat())


def type_get_name(server: socket.socket, index: int):   # ok
    send_string(server, system.AI_list[index].get_name())


def type_set_name(server: socket.socket, index: int):   # ok
    name = get_string(server)
    system.AI_list[index].set_name(name)
    send_true(server)


def type_get_owner_name(server: socket.socket, index: int):   # ok
    send_string(server, system.AI_list[index].get_owner_name())


def type_set_owner_name(server: socket.socket, index: int):   # ok
    owner_name = get_string(server)
    system.AI_list[index].set_owner_name(owner_name)
    send_true(server)


def type_get_used_token(server: socket.socket, index: int):   # ok
    send_string(server, str(system.AI_list[index].get_used_token()))


def type_get_temperature(server: socket.socket, index: int):   # ok
    send_string(server, str(system.AI_list[index].get_temperature()))


def type_configure_immerse(server: socket.socket):
    length = len(immerse.immerse)
    send_int(server, length)
    for i in immerse.immerse:
        send_string(server, i["user"])
        send_string(server, i["target"])
        send_string(server, i["group"])


def type_set_immerse(server: socket.socket, user: str):
    target = get_string(server)
    group = get_string(server)
    immerse.set_immerse(user, target, group)
    send_true(server)


# 19个类别,打字都打麻了
type_name = ["create", "clear", "set_prompt", "set_default_prompt", "set_temperature", "get_prompt", "listen",
             "revoke", "speak", "chat", "set_speak", "set_chat", "re_chat", "set_name", "get_name", "set_owner_name",
             "get_owner_name", "get_used_token", "get_temperature", "configure_immerse", "set_immerse"]


def get_request_type(server: socket.socket) -> str:
    requests_type = get_string(server)
    if requests_type not in type_name:
        return "bad_request"
    return requests_type


# 协议主处理流程 协议流程: 双端hello   client发送想要执行的请求及相关参数    server获取请求及相关参数并处理再返回内容    client获取内容   连接关闭
def protocol(server: socket.socket, addr: str):
    log(addr, "connected")
    if not connect_hello(server):
        log(addr, "hello error")
        server.close()
        return
    req = get_request_type(server)  # 获取请求的功能类型
    if req == "bad_request":
        log(addr, "request error")
        server.close()
    log(addr, "request type: " + req)

    # 让IDE闭嘴
    user = "immerse"
    index = 0

    if req != "configure_immerse":
        user = get_string(server)
        log(addr, "user: " + user)
        index = system.get_AI_index(user)
        if req != "create" and index == -1:
            system.add_AI(user, config.default_neko_name, "")
            index = system.get_AI_index(user)
            log(addr, "automatically create neko for " + user)

    # 调用相应处理函数                         为啥不记得switch呢! 原来3.10才有switch啊,那没事了 那我为什么不把它独立成一个函数!
    if req == "configure_immerse":
        type_configure_immerse(server)
    elif req == "create":
        type_create(server, user)
    elif req == "clear":
        type_clear(server, index)
    elif req == "set_prompt":
        type_set_prompt(server, index)
    elif req == "set_default_prompt":
        type_set_default_prompt(server, index)
    elif req == "set_temperature":
        type_set_temperature(server, index)
    elif req == "get_prompt":
        type_get_prompt(server, index)
    elif req == "listen":
        type_listen(server, index)
    elif req == "revoke":
        type_revoke(server, index)
    elif req == "speak":
        type_speak(server, index)
    elif req == "chat":
        type_chat(server, index)
    elif req == "set_speak":
        type_set_speak(server, index)
    elif req == "set_chat":
        type_set_chat(server, index)
    elif req == "re_chat":
        type_re_chat(server, index)
    elif req == "get_name":
        type_get_name(server, index)
    elif req == "set_name":
        type_set_name(server, index)
    elif req == "get_owner_name":
        type_get_owner_name(server, index)
    elif req == "set_owner_name":
        type_set_owner_name(server, index)
    elif req == "get_used_token":
        type_get_used_token(server, index)
    elif req == "get_temperature":
        type_get_temperature(server, index)
    elif req == "set_immerse":
        type_set_immerse(server, user)

    log(addr, "request completed, socket closed")
    server.close()


# 启动服务器
def start_server():
    log("localhost", "start server")
    server = socket.socket()
    server.bind((config.host, config.port))
    server.listen(5)

    while system.server_run:  # 该参数将由console控制
        c, addr = server.accept()
        _thread.start_new_thread(protocol, (c, str(addr)))


# 这玩意怎么能整这么多
