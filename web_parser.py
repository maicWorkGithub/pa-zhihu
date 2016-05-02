#!/usr/bin/env python3
# coding: utf-8
from base_setting import *
from lxml import html
from sq_db import *
import requests
import json
import math
import pprint
import re

sq = SqDb()


class WebParser:
    def __init__(self, url):
        self.person_dict = {}
        self.followed_urls = []
        self.url = url

    def get_person_info(self):
        r = requests.get(self.url, headers=header, cookies=cookies)
        if r.status_code == 200:
            doc = html.fromstring(r.text)
            # self.user_hash = json.loads(doc.xpath(u'//script[@data-name="ga_vars"]/text()')[0])['user_hash']
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
                u'//span[@class="employment item"]/@title'))
            self.person_dict['position'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="position item"]/@title'))
            self.person_dict['education'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="education item"]/text()'))
            self.person_dict['major'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="education-extra item"]/text()'))
            self.person_dict['thanks'] = self._get_attr_str(left_profile[0].xpath(
                u'//span[@class="zm-profile-header-user-thanks"]/strong/text()'))
            self.person_dict['asked'] = left_profile[0].xpath(
                u'//div[@class="profile-navbar clearfix"]//span[@class="num"]/text()')[0]
            self.person_dict['answered'] = left_profile[0].xpath(
                u'//div[@class="profile-navbar clearfix"]//span[@class="num"]/text()')[1]
            self.person_dict['post'] = left_profile[0].xpath(
                u'//div[@class="profile-navbar clearfix"]//span[@class="num"]/text()')[2]
            self.person_dict['collect'] = left_profile[0].xpath(
                u'//div[@class="profile-navbar clearfix"]//span[@class="num"]/text()')[3]
            self.person_dict['public-edit'] = left_profile[0].xpath(
                u'//div[@class="profile-navbar clearfix"]//span[@class="num"]/text()')[4]
            self.person_dict['followed'] = right_profile[0].xpath(
                u'//div[@class="zm-profile-side-following zg-clear"]/a[@class="item"]/strong/text()')[0]
            self.person_dict['follower'] = right_profile[0].xpath(
                u'//div[@class="zm-profile-side-following zg-clear"]/a[@class="item"]/strong/text()')[1]

    @staticmethod
    def _get_attr_str(arr):
        if len(arr):
            return arr[0]
        else:
            return ''

    def get_user_followed(self):
        url = self.url + followed_url_suffix
        hd = header
        hd['Referer'] = self.url
        del hd['X-Requested-With']
        r = requests.get(url, headers=header, cookies=cookies)
        if r.status_code == 200:
            times = math.ceil(int(self.person_dict['followed']) / 20) - 1
            html_doc = html.fromstring(r.text)
            # 这个只用来找前20个
            self.followed_urls.append(html_doc.xpath(u'//h2[@class="zm-list-content-title"]/a/@href'))

            if times:
                data = {
                    'method': 'next',
                    '_xsrf': html_doc.xpath(u'//input[@name="_xsrf"]/@value')
                }
                params = {
                    'order_by': 'created',
                    'hash_id': json.loads(self._get_attr_str(html_doc.xpath(
                        u'//div[@class="zh-general-list clearfix"]/@data-init')))['params']['hash_id']
                }

                headers = header
                headers['Referer'] = url
                headers['Host'] = 'www.zhihu.com'
                headers['X-Requested-With'] = 'XMLHttpRequest'
                # return_people_count = 20
                # total_returned_count = 20
                # while total_returned_count < int(self.person_dict['followed']):
                #     # 这样看起来更合理点
                #     pass
                for i in range(times):
                    params['offset'] = (i + 1) * 20
                    data['params'] = json.dumps(params).replace(' ', '')
                    r_inner = requests.post(url, data=data, headers=headers, cookies=cookies)
                    content = r_inner.json()
                    if content['r'] == 0:
                        for people in content['msg']:
                            self.followed_urls + (html.fromstring(people.xpath(
                                u'//h2[@class="zm-list-content-title"]/a/@href')))
            else:
                raise 'code: %s' % r.status_code

    def save_person_to_db(self):
        sq.save_data(self.get_person_info())

    def save_link_in_db(self):
        sq.save_link(self.followed_urls)
        # followed-topic和回答,提问,最新动态,都有固定的url去抓,这个先不弄了吧.

        # 最新动态没有专门的页面, 只能在主页用ajax请求抓取.

if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)

    wp = WebParser(base_person_page)
    wp.get_person_info()
    print(json.dumps(wp.person_dict, sort_keys=True, indent=2))
    pp.pprint(wp.get_user_followed())
'''
这个函数返回两个东西
1, 爬取当前用户的一个dict
2, 一个当前用户的关注者的list
'''