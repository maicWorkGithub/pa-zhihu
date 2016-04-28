# coding: utf-8
from .client import *
from .base_setting import *
from lxml import html
import json


class WebParser:
    def __init__(self, url):
        self._session = Client().return_session()
        self.person_dict = {}
        self.follower = []
        self.url = url

    def get_person_info(self):
        r = self._session.get(self.url)
        doc = html.tostring(r.text)
        left_profile = doc.xpath(u'//div[@class="zu-main-content"]')
        right_profile = doc.xpath(u'//div[@class="zu-main-sidebar"]')
        self.person_dict = {
            'zhihu-ID': self.url[self.url.rfind('/') + 1:],
            'home-page': self.url,
            'username': left_profile.xpath(u'//span[@class="name"]/text()'),
            'gender': left_profile.xpath(u'//span[@class="gender"]/i[@class="icon"]'),
            'location': left_profile.xpath(u'//span[@class="location"]/@title'),
            'business': left_profile.xpath(u'//span[@class="business"]/@title'),
            'company': left_profile.xpath(u'//span[@class="company"]/@title'),
            'position': left_profile.xpath(u'//span[@class="position"]/@title'),
            'education': left_profile.xpath(u'//span[@class="education"]/text()'),
            'major': left_profile.xpath(u'//span[@class="education-extra"]/text()'),
            'agreed': left_profile.xpath(u'//span[@class="zm-profile-header-user-agree"]/strong/text()'),
            'thanks': left_profile.xpath(u'//span[@class="zm-profile-header-user-thanks"]/strong/text()'),
            'asked': left_profile.xpath(u'//div[@class="profile-nav-bar"]//span[@class="num"][0]/text'),
            'answered': left_profile.xpath(u'//div[@class="profile-nav-bar"]//span[@class="num"][1]/text'),
            'post': left_profile.xpath(u'//div[@class="profile-nav-bar"]//span[@class="num"][2]/text'),
            'collect': left_profile.xpath(u'//div[@class="profile-nav-bar"]//span[@class="num"][3]/text'),
            'public-edit': left_profile.xpath(u'//div[@class="profile-nav-bar"]//span[@class="num"][4]/text'),
            'followed': right_profile.xpath(u'//div[@class="zm-profile-side-following"]/a[@class="item"][0]'
                                            u'//strong/text()]'),
            'follower': right_profile.xpath(u'//div[@class="zm-profile-side-following"]/a[@class="item"][1]'
                                            u'//strong/text()]')
        }

        # followed-topic和回答,提问,最新动态,都有固定的url去抓,这个先不弄了吧.

        # 最新动态没有专门的页面, 只能在主页用ajax请求抓取.

'''
这个函数返回两个东西
1, 爬取当前用户的一个dict
2, 一个当前用户的关注者的list
'''