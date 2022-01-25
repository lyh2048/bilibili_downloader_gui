import requests
import wx
import time
import qrcode
import json
from singleton import Singleton
from app_context import AppContext
from pubsub import pub


class BilibiliUtils(Singleton):
    def __init__(self) -> None:
        self.context = AppContext()
        self.request = requests.session()
        self.config = self.context.get_config()
        self.headers = self.config['headers']
    
    def get_login_url(self):
        url = 'http://passport.bilibili.com/qrcode/getLoginUrl'
        resp = self.request.get(url=url, headers=self.headers)
        data = json.loads(resp.text)
        qr = qrcode.QRCode()
        qr.add_data(data['data']['url'])
        img = qr.make_image(fill_color='blue', back_color='pink')
        img.save('./data/qrcode.png')
        return data
    
    def get_user_info(self):
        url = 'http://api.bilibili.com/nav'
        if self.context.get_cookie() is None:
            return None
        cookies_value = self.context.get_cookie()
        resp = self.request.get(url=url, headers=self.headers, cookies=cookies_value)
        result = json.loads(resp.text)
        if result['code'] == -101:
            pub.sendMessage('logout')
            return None
        return result['data']
    
    def get_page_list(self, bv):
        url = f'https://api.bilibili.com/x/player/pagelist?bvid={bv}&jsonp=jsonp'
        resp = self.request.get(url=url, headers=self.headers)
        resp = json.loads(resp.text)
        if resp['code'] != 0:
            return None
        page_list = resp['data']
        return list(map(lambda item: {'cid': item['cid'], 'page': item['page'], 'name': item['part']}, page_list))
    
    def get_play_url(self, bv, cid, qn):
        url = f'http://api.bilibili.com/x/player/playurl?bvid={bv}&cid={cid}&fnval=0&fnver=0&fourk=1'
        cookies_value = self.context.get_cookie()
        resp = self.request.get(url=url, headers=self.headers, cookies=cookies_value)
        result = json.loads(resp.text)
        if result['code'] != 0:
            return None
        return result
    
    def download_video(cid, video_url, file_size, output_path):
        msg = {
            'cid': cid,
            'video_url': video_url,
            'output_path': output_path
        }
        wx.CallAfter(pub.sendMessage, 'join', msg=msg)
        # pub.sendMessage('join', msg=msg)
        context = AppContext()
        cookies_value = context.get_cookie()
        headers = context.get_config()['headers']
        msg['file_size'] = file_size
        wx.CallAfter(pub.sendMessage, 'start', msg=msg)
        # pub.sendMessage('start', msg=msg)
        resp = requests.get(url=video_url, headers=headers, cookies=cookies_value, stream=True)
        chunk_size = 1024
        i = 0
        with open(output_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                i += len(chunk)
                msg['value'] = i
                wx.CallAfter(pub.sendMessage, 'update', msg=msg)
                # pub.sendMessage('update', msg=msg)
        wx.CallAfter(pub.sendMessage, 'finish', msg=msg)
        # pub.sendMessage('finish', msg=msg)
        print(f'{cid}下载完成, 输出路径: {output_path}')
    
    def check(oauthKey):
        data = {
            'oauthKey': oauthKey
        }
        context = AppContext()
        headers = context.get_config()['headers']
        url = 'http://passport.bilibili.com/qrcode/getLoginInfo'
        while True:
            r = requests.post(url=url,data=data, headers=headers)
            result = json.loads(r.text)
            if result['status']:
                print('登录成功')
                cookie_str = r.headers['Set-Cookie']
                cookie_list = cookie_str.split(';')
                s1 = ''
                s2 = ''
                s3 = ''
                s4 = ''
                for item in cookie_list:
                    item = item.strip()
                    if item.startswith('Path=/, DedeUserID'):
                        s1 = item.split('=')[-1]
                    if item.startswith('Path=/, DedeUserID__ckMd5'):
                        s2 = item.split('=')[-1]
                    if item.startswith('Path=/, SESSDATA'):
                        s3 = item.split('=')[-1]
                    if item.startswith('HttpOnly, bili_jct'):
                        s4 = item.split('=')[-1]
                cookie = {
                    'DedeUserID': s1,
                    'DedeUserID__ckMd5': s2,
                    'SESSDATA': s3,
                    'bili_jct': s4,
                }
                context.set_cookie(cookie)
                with open('./data/session', 'w') as f:
                    json.dump(cookie, f)
                pub.sendMessage("login_succeeded")
                break
            else:
                if result['data'] == -1:
                    print('密钥错误')
                    break
                elif result['data'] == -2:
                    print('密钥超时')
                    break
                print(result['message'])
            time.sleep(1)