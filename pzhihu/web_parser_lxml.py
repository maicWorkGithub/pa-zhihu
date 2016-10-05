#!/usr/bin/env python3
# coding: utf-8
import json
import logging
import math
from urllib import parse

from base_setting import *
from client import Client
from lxml import etree
from lxml import html
from requests import exceptions

logger = logging.getLogger('zhihu-logger')


class WebParser:
    def __init__(self, url):
        self.client = Client()
        self._session = self.client.return_session()
        self.person_dict = {}
        self.followed_urls = []
        self.url = url
        self.parser = html.HTMLParser(encoding='utf-8')

    def get_person_info(self):
        try:
            url_ = 'https://www.zhihu.com/people/' + parse.quote(self.url[self.url.rfind('/') + 1:])
            r = self._session.get(url_)
            if r.status_code == 200:
                try:
                    doc = html.fromstring(r.text, parser=self.parser)
                    self.followed_urls += [{'_id': self.url, 'overwrite': True}]
                    logger.info('拉取链接 [%s] 成功.' % self.url)
                except etree.XMLSyntaxError as e:
                    logger.error('个人首页解析失败, 原因: ' + str(e))
                    return
            elif r.status_code == 404:
                self.followed_urls += [{'_id': self.url, 'overwrite': True}]
                logger.warning('在获取链接 [%s] 时失败, code为: %s' % (self.url, r.status_code))
                return
            else:
                logger.warning('在获取链接 [%s] 时失败, code为: %s' % (self.url, r.status_code))
                self.followed_urls += [{'_id': self.url, 'overwrite': True}]
                return

            # 如果是机构账号，直接返回
            if len(doc.xpath(u'//a[@class="OrgIntroLink"]')):
                self.person_dict['role'] = 'organization'
                return

            # 暂时被知乎限制的账号，页面内容为空
            if len(doc.xpath(u'//div[@class="ProfileBan-wrapper"]')):
                return

            self.person_dict['home-page'] = self.url
            self.person_dict['_id'] = self.url[self.url.rfind('/') + 1:]
            # 如果赞同为0, 直接返回

            self.person_dict['agreed'] = int(self._get_attr_str(doc.xpath(
                u'//span[@class="zm-profile-header-user-agree"]/strong/text()')))

            if self.person_dict['agreed'] == 0:
                return
                # disable user level for now
                # self.person_dict['active_level'] = 'fake-user'
            else:
                gender_class = self._get_attr_str(doc.xpath(
                    u'//span[@class="item gender"]/i/@class'))
                if 'male' in gender_class:
                    self.person_dict['gender'] = 'male'
                elif 'female' in gender_class:
                    self.person_dict['gender'] = 'female'
                else:
                    self.person_dict['gender'] = 'intersexuality'

                self.person_dict['username'] = self._get_attr_str(doc.xpath(
                    u'//div[@class="zm-profile-header-main"]//span[@class="name"]/text()'))
                self.person_dict['location'] = self._get_attr_str(doc.xpath(
                    u'//span[@class="location item"]/@title'))
                self.person_dict['business'] = self._get_attr_str(doc.xpath(
                    u'//span[@class="business item"]/@title'))
                self.person_dict['company'] = self._get_attr_str(doc.xpath(
                    u'//span[@class="employment item"]/@title'))
                self.person_dict['position'] = self._get_attr_str(doc.xpath(
                    u'//span[@class="position item"]/@title'))
                self.person_dict['education'] = self._get_attr_str(doc.xpath(
                    u'//span[@class="education item"]/@title'))
                self.person_dict['major'] = self._get_attr_str(doc.xpath(
                    u'//span[@class="education-extra item"]/@title'))
                self.person_dict['thanks'] = int(self._get_attr_str(doc.xpath(
                    u'//span[@class="zm-profile-header-user-thanks"]/strong/text()')))
                # 这里的0~4非常依赖页面结构，用key in @href会比较安全
                prop_items = doc.xpath(u'//div[@class="profile-navbar clearfix"]//span[@class="num"]/text()')
                prop_items += doc.xpath(
                    u'//div[@class="zm-profile-side-following zg-clear"]/a[@class="item"]/strong/text()')
                self.person_dict['asked'] = int(prop_items[0])
                self.person_dict['answered'] = int(prop_items[1])
                self.person_dict['post'] = int(prop_items[2])
                self.person_dict['collect'] = int(prop_items[3])
                self.person_dict['public-edit'] = int(prop_items[4])

                self.person_dict['followed'] = int(prop_items[5])
                self.person_dict['follower'] = int(prop_items[6])

        except exceptions.ConnectionError as e:
            logger.error(str(e))

    @staticmethod
    def _get_attr_str(arr):
        if len(arr):
            return arr[0]
        else:
            return ''

    def get_user_followed(self):
        if not self.person_dict.get('followed'):
            return
        url = self.url + followed_url_suffix
        hd = header
        hd['Referer'] = self.url
        if hd.get('X-Requested-With'):
            del hd['X-Requested-With']
        try:
            r = self._session.get('https://www.zhihu.com/people/' + parse.quote(url[url.rfind('/') + 1:]), headers=hd)
            if r.status_code == 200:
                times = math.ceil(int(self.person_dict['followed']) / 20) - 1
                try:
                    html_doc = html.fromstring(r.text, parser=self.parser)
                    # 这里可以查看一下自己是多久被找到的。
                    self.followed_urls += [{'_id': str(x),
                                            'status': 'non-crawled', 'overwrite': False} for x in
                                           (html_doc.xpath(u'//a[@class="zg-link author-link"]/@href')) if '/org/'not in x]
                except etree.XMLSyntaxError as e:
                    print('个人followed首页解析失败, 原因: ' + str(e))
                    logger.error('个人followed首页解析失败, 原因: ' + str(e))
                    return
    
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
                    # 这样看起来更合理点，后面报错的页数要用一个自增的变量计算
                    for i in range(times):
                        params['offset'] = (i + 1) * 20
                        data['params'] = json.dumps(params).replace(' ', '')
                        try:
                            r_inner = self._session.post(
                                zhihu_home + '/node/ProfileFolloweesListV2', data=data, headers=headers)
                            if r_inner.status_code == 200:
                                content = r_inner.json()
                                if content['r'] == 0:
                                    for people in content['msg']:
                                        try:
                                            html.fromstring(people, parser=self.parser)
                                            self.followed_urls += [{'_id': str(x),
                                                                    'status': 'non-crawled',
                                                                    'overwrite': False}
                                                                   for x in (html.fromstring(people, parser=self.parser)
                                                                             .xpath(u'//a[@class="zg-link author-link"]'
                                                                                    u'/@href')) if '/org/' not in x]
                                        except etree.XMLSyntaxError as e:
                                            logger.error('个人followed内页的第' + str(i) + '解析失败, 原因: ' + str(e))
                                            continue
                                else:
                                    logger.warning('用户 [%s] 在爬取关注者 [第%s页] 的时候返回内容为空, 已抓取 [%s个] 用户链接'
                                                   % (self.person_dict['username'], times, len(self.followed_urls)))
                            else:
                                logger.warning('用户 [%s] 在爬去关注者时, 抓取 [第%s页] 时失败, code为: %s'
                                               % (self.person_dict['username'], times, r_inner.status_code))
                        except exceptions.ConnectionError as e:
                            logger.error('function get inner user followed connection error.')
                            # else:
                            #     print('用户 [%s] 的关注者少于21人, 人数为: %s'
                            #           % (self.person_dict['username'], self.person_dict['followed']))
        except exceptions.ConnectionError as e:
            logger.error('function get user followed connection error: ' + url)


if __name__ == '__main__':
    wp = WebParser(base_person_page)
    wp.get_person_info()
    wp.get_user_followed()
    print(wp.followed_urls)

