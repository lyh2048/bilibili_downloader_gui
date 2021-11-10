import wx
import requests
import re
import json
from config import Config
from dialog import MyDialog


class MyApp(wx.App):
    def OnInit(self):
        frame = wx.Frame(parent=None, title="哔哩哔哩下载器", size=(800, 600))
        frame.SetMaxSize((800, 600))
        frame.SetMinSize((800, 600))
        panel = wx.Panel(frame, -1)
        panel.SetBackgroundColour("#999")
        icon = wx.Icon("resources/favicon.ico", wx.BITMAP_TYPE_ICO)
        bv_text = wx.TextCtrl(panel)
        bv_text.SetValue("BV1Hq4y1P7e4")
        go_button = wx.Button(panel, label="Go!")
        self.Bind(wx.EVT_BUTTON, self.search, go_button)
        result_list = wx.ListCtrl(panel, style=wx.LC_SMALL_ICON)
        images = wx.ImageList(20, 20, False)
        image = wx.Bitmap('resources/download.png', wx.BITMAP_TYPE_PNG)
        images.Add(image)
        result_list.AssignImageList(images, wx.IMAGE_LIST_SMALL)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.list_select, result_list)
        self.result_list = result_list
        self.bv_text = bv_text
        self.result = []

        box = wx.BoxSizer()
        box.Add(bv_text, proportion=5, flag=wx.EXPAND|wx.ALL, border=3)
        box.Add(go_button, proportion=1, flag=wx.EXPAND|wx.ALL, border=3)
        v_box = wx.BoxSizer(wx.VERTICAL)
        v_box.Add(box, proportion=1, flag=wx.EXPAND|wx.ALL, border=3)
        v_box.Add(result_list, proportion=79, flag=wx.EXPAND|wx.ALL, border=3)

        panel.SetSizer(v_box)

        frame.SetIcon(icon)
        frame.Show()
        return True
    
    def search(self, event):
        bv = self.bv_text.GetValue().strip()
        if bv != '':
            try:
                resp = requests.get(url="https://www.bilibili.com/video/" + bv, headers=Config.headers)
                result = re.findall(r'<script>window.__INITIAL_STATE__=(.*?);.*?</script>', resp.text, re.DOTALL)
                video_info = json.loads(''.join(result))
                pages = video_info['videoData']['pages']
                self.result.clear()
                self.result_list.DeleteAllItems()
                for index, item in enumerate(pages):
                    item['bv'] = bv
                    self.result.append(item)
                    self.result_list.InsertItem(index, item['part'], 0)
            except Exception as e:
                wx.MessageBox('查询失败', 'Error', wx.OK|wx.ICON_ERROR)
                print(e)
    
    def list_select(self, event):
        index = event.GetIndex()
        bv = self.result[index]['bv']
        cid = self.result[index]['cid']
        _headers = Config.headers.copy()
        _headers['referer'] = 'https://www.bilibili.com'
        try:
            resp = requests.get(url=f"https://api.bilibili.com/x/player/playurl?cid={cid}&bvid={bv}&qn=0&type=&otype=json&fourk=1&fnver=0&fnval=976", headers=_headers)
            video_info = json.loads(resp.text)
            accept_description = video_info['data']['accept_description']
            audio_list = video_info['data']['dash']['audio']
            video_list = video_info['data']['dash']['video']
            dialog = MyDialog(cid, accept_description, audio_list, video_list, None)
            dialog.ShowModal()
            dialog.Destroy()
        except Exception as e:
            wx.MessageBox('获取视频信息失败', 'Error', wx.OK|wx.ICON_ERROR)
            print(e)
