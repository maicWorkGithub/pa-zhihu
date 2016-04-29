#!/usr/bin/env python3
# coding: utf-8
import json
import requests
from base_setting import *
import time
import os
import getpass


class Client:
    def __init__(self, cookies=None):
        self._session = requests.Session()
        self._session.headers.update(header)
        if cookies is not None:
            assert isinstance(cookies, str)
            self.login_with_cookies(cookies)

    @staticmethod
    def get_captcha_url():
        return Captcha_URL_Prefix + str(int(time.time() * 1000))

    def get_captcha(self):
        self._session.get(zhihu_home)

        data = {
            'email': '',
            'password': '',
            'remember_me': 'true'
        }

        self._session.post(login_with_email, data=data)
        r = self._session.get(self.get_captcha_url())

        return r.content()

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
        if os.path.isfile(cookies_file):
            with open(cookies_file) as f:
                cookies = f.read()
        cookies_dict = json.loads(cookies)
        self._session.cookies.update(cookies_dict)

    def login_in_terminal(self, need_captcha=False):
        print('========= Zhihu Login ========')

        email = input('email: ')
        password = getpass.getpass('password: ')

        if need_captcha:
            captcha = self.get_captcha()
            with open('captcha.gif', 'wb') as f:
                f.write(captcha)
                print('==== captcha has downloaded, check and type in terminal.====')
                captcha = input('captcha: ')
                os.remove('captcha.gif')
        else:
            captcha = None

        print('======== Logging ========')

        code, msg, cookies_dict = self.login(email, password, captcha)

        if code == 0:
            print('====== Login Successful ======')
        else:
            print('====== Login Failed, Code: %s ======' % code )

        return  cookies_dict

    def create_cookies_file(self):
        cookies_dict = self.login_in_terminal()
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
    client.login_in_terminal()
