import wx
from pubsub import pub


'''
下载管理
'''


class DownloadPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(DownloadPanel, self).__init__(*args, **kw)
        vbox = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(self, -1, label='|    ----    下载列表    ----    |', style = wx.ALIGN_CENTER_HORIZONTAL)
        list_box = wx.ListBox(self, -1)
        self.list_box = list_box
        self.item_list = list()
        vbox.Add(text, 1, wx.EXPAND | wx.ALL, 20)
        vbox.Add(list_box, 20, wx.EXPAND | wx.ALL, 20)
        self.cid_set = set()
        self.SetSizer(vbox)
        pub.subscribe(self.handle_join, 'join')
        pub.subscribe(self.handle_start, 'start')
        pub.subscribe(self.handle_update, 'update')
        pub.subscribe(self.handle_finish, 'finish')
   
    def handle_join(self, msg):
        cid = msg['cid']
        if cid in self.cid_set:
            return
        self.cid_set.add(cid)
        self.item_list.append(msg['output_path'])
        self.list_box.SetItems(self.item_list)

    def handle_start(self, msg):
        cid = msg['cid']
        if cid not in self.cid_set:
            return
        k = -1
        for index, item in enumerate(self.item_list):
            if item.startswith(msg['output_path']):
                k = index
                break
        self.item_list[k] = f'{msg["output_path"]}  ---->   0/{str(msg["file_size"])}'
        self.list_box.SetItems(self.item_list)

    def handle_update(self, msg):
        cid = msg['cid']
        if cid not in self.cid_set:
            return
        k = -1
        for index, item in enumerate(self.item_list):
            if item.startswith(msg['output_path']):
                k = index
                break
        self.item_list[k] = f'{msg["output_path"]}  ---->   {str(msg["value"])}/{str(msg["file_size"])}'
        self.list_box.SetItems(self.item_list)
    
    def handle_finish(self, msg):
        cid = msg['cid']
        if cid not in self.cid_set:
            return
        k = -1
        for index, item in enumerate(self.item_list):
            if item.startswith(msg['output_path']):
                k = index
                break
        self.item_list[k] = f'{msg["output_path"]}  ---->   下载完成'
        self.list_box.SetItems(self.item_list)