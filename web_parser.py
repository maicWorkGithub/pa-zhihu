#!/usr/bin/env python3
# coding: utf-8
# import sys
# import os

# PACKAGE_PARENT = '..'
# SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
# sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from client import Client
from base_setting import *
from lxml import html
from sq_db import *

sq = SqDb()


class WebParser:
    def __init__(self, url):
        self.login = Client('cookies')
        self._session = self.login.return_session()
        self.person_dict = {}
        self.followed_urls = []
        self.url = url

    def get_person_info(self):
        r = self._session.get(self.url)
        if r.state_code == 200:
            doc = html.tostring(r.text)
            self.person_dict['crawled'] = True
        else:
            doc = ''
            self.person_dict['crawled'] = False
        left_profile = doc.xpath(u'//div[@class="zu-main-content"]')
        right_profile = doc.xpath(u'//div[@class="zu-main-sidebar"]')

        self.person_dict['zhihu-ID'] = self.url[self.url.rfind('/') + 1:]
        self.person_dict['home-page'] = self.url
        # 这里为什么会得到两个name, 另外一个明明不在left_profile里面的
        # 如果赞同为0, 直接返回

        self.person_dict['agreed'] = self._get_attr_str(left_profile[0].xpath(
            u'//span[@class="zm-profile-header-user-agree"]/strong/text()'))

        if self.person_dict['agreed'] == 0:
            self.person_dict['active_level'] = 'fake-user'
        else:
            gender_class = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="item gender"]/i/@class'))
            if 'male' in gender_class:
                self.person_dict['gender'] = 'male'
            elif 'female' in gender_class:
                self.person_dict['gender'] = 'female'
            else:
                self.person_dict['gender'] = 'intersexuality'

            self.person_dict['username'] = self._get_attr_str(left_profile[0].xpath(
                u'//div[@class="zm-profile-header-main"]//span[@class="name"]/text()'))
            self.person_dict['location'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="location item"]/@title'))
            self.person_dict['business'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="business item"]/@title'))
            self.person_dict['company'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="company item"]/@title'))
            self.person_dict['position'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="position item"]/@title'))
            self.person_dict['education'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="education item"]/text()'))
            self.person_dict['major'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="education-extra item"]/text()'))
            self.person_dict['thanks'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="zm-profile-header-user-thanks"]/strong/text()'))
            self.person_dict['asked'] = self._get_attr_str(left_profile[0].xpath(
                u'//div[@class="profile-nav-bar"]//span[@class="num"]/text'))
            self.person_dict['answered'] = self._get_attr_str(left_profile[0].xpath(
                u'//div[@class="profile-nav-bar"]//span[@class="num"][1]/text'))
            self.person_dict['post'] = self._get_attr_str(left_profile[0].xpath(
                u'//div[@class="profile-nav-bar"]//span[@class="num"][2]/text'))
            self.person_dict['collect'] = self._get_attr_str(left_profile[0].xpath(
                u'//div[@class="profile-nav-bar"]//span[@class="num"][3]/text'))
            self.person_dict['public-edit'] = self._get_attr_str(left_profile[0].xpath(
                u'//div[@class="profile-nav-bar"]//span[@class="num"][4]/text'))
            self.person_dict['followed'] = self._get_attr_str(right_profile[0].xpath(
                u'//div[@class="zm-profile-side-following"]/a[@class="item"]/strong/text()]'))
            self.person_dict['follower'] = self._get_attr_str(right_profile[0].xpath(
                u'//div[@class="zm-profile-side-following"]/a[@class="item"][1]/strong/text()]'))

        return self.person_dict

    @staticmethod
    def _get_attr_str(arr):
        if len(arr):
            return arr[0]
        else:
            return ''

    def save_person_to_db(self):
        sq.save_data(self.get_person_info())

    def save_link_in_db(self):
        sq.save_link(self.followed_urls)
        # followed-topic和回答,提问,最新动态,都有固定的url去抓,这个先不弄了吧.

        # 最新动态没有专门的页面, 只能在主页用ajax请求抓取.

if __name__ == '__main__':
    wp = WebParser(base_person_page)
    print(wp.get_person_info())
'''
这个函数返回两个东西
1, 爬取当前用户的一个dict
2, 一个当前用户的关注者的list
'''