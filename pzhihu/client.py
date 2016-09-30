#!/usr/bin/env python3
# coding: utf-8
import json
import requests
from base_setting import *
import time
import os
import getpass
from urllib.parse import urlencode


class Client(object):
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(header)
        self.cookies_file = current_dir + '/cookies.json'
        if os.path.isfile(self.cookies_file):
            self.login_with_cookies()
        else:
            self.create_cookies_file()
    
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

    def login_with_cookies(self):
        if os.path.isfile(self.cookies_file):
            # print('======== find cookies file, try login directly. ========')
            with open(self.cookies_file) as f:
                cookies = f.read()
            if len(cookies) and (type(cookies) == str):
                cookies_dict = json.loads(cookies)
                self._session.cookies.update(cookies_dict)
                return True
            else:
                return False
        else:
            return False

    def login_in_terminal(self):
        print('========= Zhihu Login ========')

        email = input('email: ')
        password = getpass.getpass('password: ')

        print('======== Logging by username and password ========')
        
        code, msg, cookies_dict = self.login(email, password)

        if code == 0:
            print('====== Login Successful ======')
        elif '验证码' in msg:
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

    def create_cookies_file(self):
        """创建cookies 文件

        :param file_name: str
        :return: None
        """
        # test file expire of broken
        if self.login_with_cookies():
            print('========cookies file exist and validly.========')
            return
        cookies_dict = self.login_in_terminal()
        if cookies_dict:
            with open(self.cookies_file, 'w') as f:
                f.write(cookies_dict)
            print('====== Create Cookies File Successful.======')
        else:
            print('====== Can\'t Create Cookies File, Maybe Login Failed.======')
    
    def return_session(self):
        return self._session


if __name__ == '__main__':
    client = Client()
    client.create_cookies_file()
