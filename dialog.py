import requests
import wx
import os
import subprocess
from config import Config


class MyDialog(wx.Dialog):
    def __init__(self, cid, accept_description, audio_list, video_list, *args, **kwargs):
        super(MyDialog, self).__init__(*args, **kwargs)
        self.cid = cid
        self.accept_description = accept_description
        self.audio_list = audio_list
        self.video_list = video_list

        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour("#999")
        n = len(self.video_list) // 2
        self.video_list = self.video_list[0:len(self.video_list):2]
        quality_list = self.accept_description[-n:]
        quality = wx.RadioBox(panel, -1, label="请选择视频清晰度", size=wx.DefaultSize, choices=quality_list, style=wx.RA_SPECIFY_COLS)
        gauge1 = wx.Gauge(panel)
        gauge2 = wx.Gauge(panel)
        
        download_btn = wx.Button(panel, label="下载")
        self.Bind(wx.EVT_BUTTON, self.download, download_btn)
        close_btn = wx.Button(panel, label="关闭")
        self.Bind(wx.EVT_BUTTON, self.exit, close_btn)
        
        box = wx.BoxSizer()
        box.Add(download_btn, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        box.Add(close_btn, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        v_box = wx.BoxSizer(wx.VERTICAL)
        v_box.Add(quality, proportion=5, flag=wx.EXPAND|wx.ALL, border=3)
        v_box.Add(gauge1, proportion=1, flag=wx.EXPAND|wx.ALL, border=3)
        v_box.Add(gauge2, proportion=1, flag=wx.EXPAND|wx.ALL, border=3)
        v_box.Add(box, proportion=2, flag=wx.EXPAND|wx.ALL, border=3)
        
        self.gauge1 = gauge1
        self.gauge2 = gauge2
        self.quality = quality
        self.download_btn = download_btn

        panel.SetSizer(v_box)
        self.SetSize((400, 300))
        self.SetTitle("清晰度")
        self.Show(True)

    def exit(self, event):
        self.Destroy()
    
    def download(self, event):
        index = self.quality.GetSelection()
        video_url = self.video_list[index]['baseUrl']
        audio_url = self.audio_list[0]['baseUrl']
        try:
            self.download_btn.Disable()
            _headers = Config.headers.copy()
            _headers['referer'] = 'https://www.bilibili.com'
            video_path = Config.temp + str(self.cid) +".mp4"
            audio_path = Config.temp + str(self.cid) +".mp3"
            self.save(video_url, _headers, video_path, self.gauge1)
            self.save(audio_url, _headers, audio_path, self.gauge2)
            dialog = wx.FileDialog(self, message="请选择保存位置", defaultDir=os.getcwd(), defaultFile=str(self.cid), wildcard="Video files (*.mp4)|*.mp4", style=wx.FD_SAVE)
            dialog.ShowModal()
            output_path = dialog.GetPath()
            dialog.Destroy()
            self.merge(video_path, audio_path, output_path)
            self.download_btn.Enable()
            wx.MessageBox("下载完成", "提示", wx.OK|wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox('下载失败', 'Error', wx.OK|wx.ICON_ERROR)
            self.download_btn.Enable()
            print(e)
    
    def save(self, url, headers, file_name, gauge):
        head = requests.head(url=url, headers=headers)
        file_size = head.headers.get('Content-Length')
        if file_size is not None:
            file_size = int(file_size)
        else:
            file_size = 0
        gauge.SetRange(file_size)
        resp = requests.get(url=url, headers=headers, stream=True)
        chunk_size = 1024
        i = 0
        with open(file_name, "wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                i += len(chunk)
                gauge.SetValue(i)

    def merge(self, video_path, audio_path, output_path):
        cmd = f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac -strict experimental {output_path}"
        if subprocess.call(cmd, shell=False):
            raise Exception("{} 执行失败".format(cmd))