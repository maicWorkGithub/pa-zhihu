#!/usr/bin/env python3
# coding: utf-8
import json
import requests
from base_setting import *
import time
import os
import getpass
from urllib.parse import urlencode


class Client:
    def __init__(self, cookies=None):
        self._session = requests.Session()
        self._session.headers.update(header)
        if cookies is not None:
            assert isinstance(cookies, str)
            if len(cookies):
                self.login_with_cookies(cookies)
            else:
                print('==== Cookies file is broken. \n Delete it and retry. ====')

    @staticmethod
    def get_captcha_url():
        params = {
            'r': str(int(time.time() * 1000)),
            'type': 'login',
        }
        return Captcha_URL + '?' + urlencode(params)

    def get_captcha(self):
        self._session.get(zhihu_home)

        data = {
            'email': '',
            'password': '',
            'remember_me': 'true'
        }

        self._session.post(login_with_email, data=data)
        r = self._session.get(self.get_captcha_url())

        return r.content

    def login(self, email, password, captcha=None):
        data = {
            'email': email,
            'password': password,
            'remember_me': 'true'
        }
        if captcha is not None:
            data['captcha'] = captcha

        r = self._session.post(login_with_email, data=data)
        content = r.json()

        code = int(content['r'])
        msg = content['msg']
        cookies_str = json.dumps(self._session.cookies.get_dict()) if code == 0 else ''

        return code, msg, cookies_str

    def login_with_cookies(self, cookies_file):
        cookies = None
        if os.path.isfile(cookies_file):
            with open(cookies_file) as f:
                cookies = f.read()
        cookies_dict = json.loads(cookies)
        self._session.cookies.update(cookies_dict)

    def login_in_terminal(self, need_captcha=False):
        print('========= Zhihu Login ========')

        # email = input('email: ')
        # password = getpass.getpass('password: ')

        email = '1764199786@qq.com'
        password = '535271884'

        print('======== Logging ========')

        code, msg, cookies_dict = self.login(email, password)

        if code == 0:
            print('====== Login Successful ======')
        elif '验证码' in json.dumps(msg):
            print('====== Captcha is necessary ======')
            captcha = self.get_captcha()
            with open('captcha.gif', 'wb') as f:
                f.write(captcha)
            print('====== captcha has downloaded in current dir, check and type in terminal.======')
            captcha = input('captcha: ')
            os.remove('captcha.gif')
            code, msg, cookies_dict = self.login(email, password, captcha)
            if code == 0:
                print('====== Login Successful ======')
            else:
                print('====== Login Failed, Message: %s ======' % msg)
        return cookies_dict

    # 第一次验证码为空,登录一次.
    # 第二次请求验证码,登录一次
    #

    def create_cookies_file(self):
        cookies_dict = self.login_in_terminal(True)
        if cookies_dict:
            with open('cookies', 'wb') as f:
                f.write(self.login_in_terminal())
            print('====== Create Cookies File Successful ======')
        else:
            print('====== Can\'t Create Cookies File, Maybe Login Failed ======')

    def return_session(self):
        return self._session

if __name__ == '__main__':
    client = Client()
    if os.path.isfile('cookies.json'):
        client.login_with_cookies('cookies.json')
    else:
        client.create_cookies_file()
