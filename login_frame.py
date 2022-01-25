import wx
import threading
from bilibili_utils import BilibiliUtils
from app_context import AppContext


class LoginFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(LoginFrame, self).__init__(*args, **kw)
        self.SetTitle('登录')
        self.SetSize(350, 500)
        self.SetMaxSize((350, 500))
        self.SetMinSize((350, 500))
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour("#999")
        context = AppContext()
        if context.get_cookie() is None:
            # 获取二维码和密钥
            self.data = BilibiliUtils().get_login_url()
            # 检查是否登录成功
            thread = threading.Thread(target=BilibiliUtils.check, args=(self.data['data']['oauthKey'], ))
            thread.setDaemon(True)
            thread.start()
        refresh_button = wx.Button(panel, label='刷新')
        self.Bind(wx.EVT_BUTTON, self.refresh, refresh_button)
        text = wx.StaticText(panel, label='请使用哔哩哔哩客户端扫码登录', style=wx.ALIGN_CENTER_HORIZONTAL)
        img = wx.Image('./data/qrcode.png', wx.BITMAP_TYPE_PNG)
        bitmap = wx.Bitmap(img.Scale(300, 300))
        self.image = wx.StaticBitmap(panel, -1, bitmap)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.image, 2, wx.EXPAND | wx.ALL, 20)
        vbox.Add(text, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(refresh_button, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(vbox)
    
    def refresh(self, event):
        self.data = BilibiliUtils().get_login_url()
        # 检查是否登录成功
        thread = threading.Thread(target=BilibiliUtils.check, args=(self.data['data']['oauthKey'], ))
        thread.setDaemon(True)
        thread.start()
        img = wx.Image('./data/qrcode.png', wx.BITMAP_TYPE_PNG)
        bitmap = wx.Bitmap(img.Scale(300, 300))
        self.image.SetBitmap(bitmap)
        