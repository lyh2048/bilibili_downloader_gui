import wx
import threading
import os
from bilibili_utils import BilibiliUtils


'''
主页
'''


class IndexPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(IndexPanel, self).__init__(*args, **kw)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer()
        input = wx.TextCtrl(self, -1, value='请输入视频的BV号')
        self.input = input
        search_button = wx.Button(self, -1, label='搜索')
        self.Bind(wx.EVT_BUTTON, self.search, search_button)
        data_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        data_list.InsertColumn(0, '#', wx.LIST_FORMAT_CENTER, 50)
        data_list.InsertColumn(1, '名称', wx.LIST_FORMAT_CENTER, 750)
        data_list.InsertColumn(2, '操作', wx.LIST_FORMAT_CENTER, 100)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.select_item, data_list)
        self.data_list = data_list
        self.page_list = None
        self.bv = None
        hbox.Add(input, 3, wx.ALL | wx.EXPAND, 10)
        hbox.Add(search_button, 1, wx.ALL | wx.EXPAND, 10)
        vbox.Add(hbox, 1, wx.ALL | wx.EXPAND, 10)
        vbox.Add(data_list, 20, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(vbox)
    
    def search(self, e):
        bv = self.input.Value
        if bv.startswith('BV'):
            result = BilibiliUtils().get_page_list(bv)
            if result is None:
                wx.MessageBox('获取视频列表失败', '提示', wx.OK)
            else:
                self.page_list = result
                self.bv = bv
        else:
            wx.MessageBox('请输入有效的BV号', '提示', wx.OK)
        self.data_list.DeleteAllItems()
        for item in self.page_list:
            index = self.data_list.InsertItem(self.data_list.GetItemCount(), 'P' + str(item['page']))
            self.data_list.SetItem(index, 1, item['name'])
            self.data_list.SetItem(index, 2, '下载')

    def select_item(self, e):
        index = e.GetIndex()
        cid = self.page_list[index]['cid']
        bv = self.bv
        result = BilibiliUtils().get_play_url(bv, cid, 64)
        if result == None:
            wx.MessageBox('获取视频下载链接失败', '错误', wx.OK)
            return
        dialog = wx.FileDialog(self, message="请选择保存位置", defaultDir=os.getcwd(), defaultFile=str(cid), wildcard="Video files (*.flv)|*.flv", style=wx.FD_SAVE)
        dialog.ShowModal()
        output_path = dialog.GetPath()
        dialog.Destroy()
        video_url = result['data']['durl'][0]['url']
        file_size = result['data']['durl'][0]['size']
        thread = threading.Thread(target=BilibiliUtils.download_video, args=(cid, video_url, file_size, output_path))
        thread.setDaemon(True)
        thread.start()
        wx.MessageBox('一个任务添加到下载队列', '提示', wx.OK)