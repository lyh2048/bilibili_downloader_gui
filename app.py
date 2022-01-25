import wx
import json
import os
from login_frame import LoginFrame
from main_frame import MainFrame
from pubsub import pub
from app_context import AppContext


class BApp(wx.App):
    def OnInit(self):
        # 登录成功跳转到主页
        pub.subscribe(self.GoToMain, 'login_succeeded')
        self.icon = wx.Icon("resources/favicon.ico", wx.BITMAP_TYPE_ICO)
        context = AppContext()
        self.main_frame = MainFrame(None)
        self.main_frame.SetIcon(self.icon)
        self.main_frame.Hide()
        if not os.path.exists('./data'):
            # 创建data文件夹
            os.makedirs('./data')
            # 显示登录界面
            self.login_frame = LoginFrame(None)
            self.ShowLogin()
        else:
            if not os.path.exists('./data/session'):
                # 显示登录界面
                self.login_frame = LoginFrame(None)
                self.ShowLogin()
            else:
                with open('./data/session', 'r') as f:
                    cookie = json.load(f)
                    context.set_cookie(cookie)
                # 显示主界面
                old = self.main_frame
                self.main_frame = MainFrame(None)
                self.main_frame.SetIcon(self.icon)
                self.ShowMain()
                old.Close()
        return True
    
    def ShowLogin(self):
        self.login_frame.SetIcon(self.icon)
        self.login_frame.Show()

    def ShowMain(self):
        self.main_frame.Show()
    
    def GoToMain(self):
        self.login_frame.Close()
        self.ShowMain()
        