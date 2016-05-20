#!/usr/bin/env python3
# coding: utf-8
from base_setting import *
from lxml import html
from client import Client
import json
import math


class WebParser:
    def __init__(self, url):
        self.client = Client('cookies.json')
        self._session = self.client.return_session()
        self.person_dict = {}
        self.followed_urls = []
        self.url = url
        print('开始抓取并解析链接: ' + self.url)

    def get_person_info(self):
        r = self._session.get(self.url)
        if r.status_code == 200:
            doc = html.fromstring(r.text)
            self.followed_urls += [{'link': self.url, 'status': 'crawled', 'overwrite': True}]
            print('拉取链接 [%s] 成功.' % self.url)
        else:
            print('在获取链接 [%s] 时失败, code为: %s' % (self.url, r.status_code))
            self.followed_urls += [{'link': self.url, 'status': 'non-crawled'}]
            return

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
        if hd.get('X-Requested-With'):
            del hd['X-Requested-With']
        r = self._session.get(url, headers=hd)
        if r.status_code == 200:
            times = math.ceil(int(self.person_dict['followed']) / 20) - 1
            html_doc = html.fromstring(r.text)
            self.followed_urls += [{'link': x, 'status': 'non-crawled', 'overwrite': False} for x in
                                   (html_doc.xpath(u'//h2[@class="zm-list-content-title"]/a/@href'))]

            if times:
                data = {
                    'method': 'next',
                    '_xsrf': self._get_attr_str(html_doc.xpath(u'//input[@name="_xsrf"]/@value'))
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
                # return_people_count = 第一次len(self.followed_urls), 后面是len(json)
                # total_returned_count = len(self.followed_urls)
                # while total_returned_count < int(self.person_dict['followed']):
                # 这样看起来更合理点
                for i in range(times):
                    params['offset'] = (i + 1) * 20
                    data['params'] = json.dumps(params).replace(' ', '')
                    r_inner = self._session.post(
                        zhihu_home + '/node/ProfileFolloweesListV2', data=data, headers=headers)
                    if r_inner.status_code == 200:
                        # 这里失败的话
                        content = r_inner.json()
                        if content['r'] == 0:
                            # 这里失败的话
                            for people in content['msg']:
                                self.followed_urls += [{'link': x, 'status': 'non-crawled', 'overwrite': False} for x in
                                                       (html.fromstring(people).xpath(
                                                           u'//h2[@class="zm-list-content-title"]/a/@href'))]
                        else:
                            print('用户 [%s] 在爬取关注者 [第%s页] 的时候返回内容为空, 已抓取 [%s个] 用户链接'
                                  % (self.person_dict['username'], times, len(self.followed_urls)))
                    else:
                        print('用户 [%s] 在爬去关注者时, 抓取 [第%s页] 时失败, code为: %s'
                              % (self.person_dict['username'], times, r_inner.status_code))
            # else:
            #     print('用户 [%s] 的关注者少于21人, 人数为: %s'
            #           % (self.person_dict['username'], self.person_dict['followed']))

# todo: 关注的话题, 回答, 提问, 最新动态, 关注的问题(这个好像看不到)


if __name__ == '__main__':
    wp = WebParser(base_person_page)
    wp.get_user_followed()
    print(wp.followed_urls)

'''
这个函数返回两个东西
1, 爬取当前用户的一个dict
2, 一个当前用户的关注者的list
'''
