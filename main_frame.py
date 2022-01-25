import wx
import os
from index_panel import IndexPanel
from user_panel import UserPanel
from download_panel import DownloadPanel
from pubsub import pub


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)
        self.SetTitle('哔哩哔哩视频下载器')
        self.SetSize(1000, 600)
        self.SetMaxSize((1000, 600))
        self.SetMinSize((1000, 600))
        # Cookie过期
        pub.subscribe(self.logout, 'logout')
        bmp_index = wx.Bitmap('./resources/index.png', wx.BITMAP_TYPE_PNG)
        bmp_download = wx.Bitmap('./resources/download.png', wx.BITMAP_TYPE_PNG)
        bmp_user = wx.Bitmap('./resources/user.png', wx.BITMAP_TYPE_PNG)
        bmp_quit = wx.Bitmap('./resources/quit.png', wx.BITMAP_TYPE_PNG)
        panel = wx.Panel(self, wx.ID_ANY)
        tool_bar = wx.ToolBar(panel, wx.ID_ANY, style=wx.TB_TEXT | wx.VERTICAL, size=(60, 600))
        tool_bar.SetBackgroundColour("#999")
        tool_bar.AddTool(0, u'主页', bmp_index)
        tool_bar.AddSeparator()
        tool_bar.AddTool(1, u'下载', bmp_download)
        tool_bar.AddSeparator()
        tool_bar.AddTool(2, u'用户', bmp_user)
        tool_bar.AddSeparator()
        tool_bar.AddTool(3, u'退出', bmp_quit)
        tool_bar.AddSeparator()
        tool_bar.Realize()
        tool_bar.Bind(wx.EVT_TOOL, self.OnEventTask)
        self.tool_bar = tool_bar
        self.index_panel = IndexPanel(panel)
        self.download_panel = DownloadPanel(panel)
        self.user_panel = UserPanel(panel)
        self.download_panel.Hide()
        self.user_panel.Hide()
        self.hbox = wx.BoxSizer()
        self.hbox.Add(tool_bar, 1)
        self.hbox.Add(self.index_panel, 20)
        panel.SetSizer(self.hbox)

    def OnEventTask(self, event):
        id = event.GetId()
        if id == 0:
            self.hbox.Clear()
            self.hbox.Add(self.tool_bar, 1)
            self.hbox.Add(self.index_panel, 20)
            self.index_panel.Show()
            self.download_panel.Hide()
            self.user_panel.Hide()
            self.hbox.Layout()
        elif id == 1:
            self.hbox.Clear()
            self.hbox.Add(self.tool_bar, 1)
            self.hbox.Add(self.download_panel, 20)
            self.index_panel.Hide()
            self.download_panel.Show()
            self.user_panel.Hide()
            self.hbox.Layout()
        elif id == 2:
            self.hbox.Clear()
            self.hbox.Add(self.tool_bar, 1)
            self.hbox.Add(self.user_panel, 20)
            self.index_panel.Hide()
            self.download_panel.Hide()
            self.user_panel.Show()
            self.hbox.Layout()
        elif id == 3:
            self.Close()

    def logout(self):
        wx.MessageBox('登录凭证失效，请退出程序，重新登录', caption='错误', style=wx.OK)
        # 移除cookie
        if os.path.exists('./data/session'):
            os.remove('./data/session')
    