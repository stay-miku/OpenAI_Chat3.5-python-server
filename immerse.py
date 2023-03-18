import AI

# 储存沉浸模式数据
immerse = {}


def set_immerse(user: str, target: str, group: str):
    immerse[user] = {"user": user, "target": target, "group": group}
