# OpenAI_Chat3.5-python-server

miraiQQ机器人使用openai官方api的聊天插件的服务端(需配合相应的mirai插件一起使用)

使用方法:
git clone https://github.com/stay-miku/OpenAI_Chat3.5-python-server.git
然后运行main.py

相关配置在config.py里,可自行修改(使用前必须修改里面的api_key)

(github新手,有啥问题请见谅~)

AI.py内的AI类是一个对官方库的基本封装(把我认为有用的功能放进去了)

net.py是用socket自行实现的客户端与服务端通信(可以根据这个自己设计客户端),该端为服务端
