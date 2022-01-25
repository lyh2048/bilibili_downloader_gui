import json
from singleton import Singleton


class AppContext(Singleton):
    init_flag = False

    def __init__(self) -> None:
        if AppContext.init_flag:
            return
        self.config = None
        try:
            # 加载配置文件
            with open('./config/config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(e)
            print('加载配置文件失败')
            exit(-1)
        # Cookie
        self.cookie = None
        AppContext.init_flag = True

    def set_cookie(self, cookie):
        self.cookie = cookie
    
    def get_cookie(self):
        return self.cookie

    def get_config(self):
        return self.config