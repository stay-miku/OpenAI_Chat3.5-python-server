import time

import system


# 命令行功能
def start_console():
    time.sleep(0.1)
    while True:
        comm = input(">").split(" ")
        if comm[0] == "stop":
            system.server_run = False
            break
        elif comm[0] == "list":
            for i in system.AI_list:
                print(i.user)
        elif comm[0] == "get":
            if len(comm) == 3:
                index = system.get_AI_index(comm[1])
                if index == -1:
                    print("error user")
                elif comm[2] == "prompt":
                    print(system.AI_list[index].prompt)
                elif comm[2] == "messages":
                    print(system.AI_list[index].get_messages())
                elif comm[2] == "name":
                    print(system.AI_list[index].name)
                elif comm[2] == "owner_name":
                    print(system.AI_list[index].owner_name)
                elif comm[2] == "used_tokens":
                    print(system.AI_list[index].used_tokens)
                elif comm[2] == "temperature":
                    print(system.AI_list[index].temperature)
                else:
                    print("error type")
            else:
                print("unknown command")
        elif comm[0] == "create" and len(comm) == 3:
            print(system.add_AI(comm[1], comm[2]))
        elif comm[0] == "save":
            system.save_AI()
        elif comm[0] == "reload":
            system.AI_list = []
            system.read_AI()
        else:
            print("unknown command")

