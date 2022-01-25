import wx
from bilibili_utils import BilibiliUtils
from urllib.request import urlretrieve


'''
用户信息
'''


class UserPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(UserPanel, self).__init__(*args, **kw)
        data = BilibiliUtils().get_user_info()
        if data is None:
            return
        face = data['face']
        urlretrieve(face, './data/face.jpg')
        img = wx.Image('./data/face.jpg', wx.BITMAP_TYPE_ANY)
        bitmap = wx.Bitmap(img.Scale(200, 200))
        image = wx.StaticBitmap(self, -1, bitmap)
        mid = data['mid']
        uname = data['uname']
        money = data['money']
        self.SetBackgroundColour("#ffffff")
        mid_text = wx.StaticText(self, label=f'UID: {mid}', style=wx.ALIGN_CENTER_HORIZONTAL)
        uname_text = wx.StaticText(self, label=f'昵称: {uname}', style=wx.ALIGN_CENTER_HORIZONTAL)
        money_text = wx.StaticText(self, label=f'硬币: {round(int(money))}', style=wx.ALIGN_CENTER_HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(image, 2, wx.EXPAND | wx.ALL, 20)
        vbox.Add(mid_text, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(uname_text, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(money_text, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(vbox)