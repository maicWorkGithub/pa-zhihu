#!/usr/bin/env python3
# coding: utf-8
import json
import logging
import math
from urllib import parse

from base_setting import *
from bs4 import BeautifulSoup as bs
from client import Client
from requests import exceptions

logger = logging.getLogger('zhihu-logger')


class WebParser:
    def __init__(self, url):
        self.client = Client()
        self._session = self.client.return_session()
        self.followed_urls = []
        self.url = url
        self.quote_url = 'https://www.zhihu.com/people/' + parse.quote(url[url.rfind('/') + 1:])
        self.person_dict = {
            'home_page': url,
            # '_id': url[url.rfind('/') + 1:],
            'id': url[url.rfind('/') + 1:],
            'agreed': 0,
            'gender': 'intersexuality',
            'username': '',
            'location': '',
            'business': '',
            'company': '',
            'position': '',
            'education': '',
            'major': '',
            'thanks': 0,
            'asked': 0,
            'answered': 0,
            'post': 0,
            'collect': 0,
            'public_edit': 0,
            'followed': 0,
            'follower': 0
        }

    def get_person_info(self):
        try:
            r = self._session.get(self.quote_url)
            if r.status_code == 200:
                try:
                    doc = bs(r.text, 'lxml')
                    self.followed_urls += [{'_id': self.url, 'overwrite': True}]
                    logger.info('get [%s] success.' % self.url)
                except Exception as e:
                    logger.error('get person home failed, caused by: ' + str(e))
                    return
            else:
                logger.warning('get [%s] failed, code: %s' % (self.url, r.status_code))
                self.followed_urls += [{'_id': self.url, 'overwrite': True}]
                return

            # 暂时被知乎限制的账号，页面内容为空
            if len(doc.find_all('div', class_='ProfileBan-wrapper')):
                return

            self.person_dict['agreed'] = int(doc.find('span', class_='zm-profile-header-user-agree').strong.text)

            # 如果赞同为0, 认为是没有价值的用户。
            if self.person_dict['agreed'] == 0:
                return
                # disable user level for now
                # self.person_dict['active_level'] = 'fake-user'
            else:
                if doc.find('span', class_='gender') is not None:
                    self.person_dict['gender'] = 'female' if \
                        'female' in str(doc.find('span', class_='gender').i) else \
                        'male'

                self.person_dict['username'] = doc.find('div', class_='title-section').span.text
                self.person_dict['location'] = doc.find('span', class_='location')['title'] \
                    if doc.find('span', class_='location') else ''
                self.person_dict['business'] = doc.find('span', class_='business')['title'] \
                    if doc.find('span', class_='business') else ''
                self.person_dict['company'] = doc.find('span', class_='company')['title'] \
                    if doc.find('span', class_='company') else ''
                self.person_dict['position'] = doc.find('span', class_='position')['title'] \
                    if doc.find('span', class_='position') else ''
                self.person_dict['education'] = doc.find('span', class_='education')['title'] \
                    if doc.find('span', class_='education') else ''
                self.person_dict['major'] = doc.find('span', class_='major')['title'] \
                    if doc.find('span', class_='major') else ''

                self.person_dict['thanks'] = int(doc.find('span', class_='zm-profile-header-user-thanks').strong.text)
                items = doc.find_all('a', class_='item')
                for i in items:
                    # 定义一个函数, 把i.href传进去更好看一点
                    if i['href'].endswith('/asks'):
                        self.person_dict['asked'] = int(i.span.text)
                    elif i['href'].endswith('/answers'):
                        self.person_dict['answered'] = int(i.span.text)
                    elif i['href'].endswith('/posts'):
                        self.person_dict['post'] = int(i.span.text)
                    elif i['href'].endswith('/collections'):
                        self.person_dict['collect'] = int(i.span.text)
                    elif i['href'].endswith('/logs'):
                        self.person_dict['public-edit'] = int(i.span.text)
                    elif i['href'].endswith('/followees'):
                        self.person_dict['followed'] = int(i.strong.text)
                    elif i['href'].endswith('/followers'):
                        self.person_dict['follower'] = int(i.strong.text)

        except exceptions.ConnectionError as e:
            logger.error(str(e))

    def get_user_followed(self):
        if not self.person_dict.get('followed'):
            return
        url = self.quote_url + followed_url_suffix
        hd = header
        hd['Referer'] = self.quote_url
        if hd.get('X-Requested-With'):
            del hd['X-Requested-With']
        try:
            r = self._session.get(url, headers=hd)
            if r.status_code == 200:
                times = math.ceil(int(self.person_dict['followed']) / 20) - 1
                try:
                    html_doc = bs(r.text, 'lxml')
                    # 这里可以查看一下自己是多久被找到的。
                    self.followed_urls += [{'_id': str(x['href']),
                                            'status': 'non-crawled', 'overwrite': False} for x in
                                           (html_doc.find_all('a', class_='author-link'))]
                except Exception as e:
                    print('个人followed首页解析失败, 原因: ' + str(e))
                    logger.error('个人followed首页解析失败, 原因: ' + str(e))
                    return

                if times:
                    data = {
                        'method': 'next',
                        '_xsrf': html_doc.find('input', {'name': '_xsrf'})['value']
                    }
                    params = {
                        'order_by': 'created',
                        'hash_id': json.loads(html_doc.find('div', class_='zh-general-list')['data-init'])
                        ['params']['hash_id']
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
                            logger.info('the %d ProfileFolloweesList' % i)
                            if r_inner.status_code == 200:
                                content = r_inner.json()
                                if content['r'] == 0:
                                    for people in content['msg']:
                                        try:
                                            self.followed_urls += [{'_id': str(x['href']),
                                                                    'status': 'non-crawled',
                                                                    'overwrite': False}
                                                                   for x in (bs(people, 'lxml')
                                                                             .find_all('a', class_='author-link'))]
                                        except Exception as e:
                                            logger.error('个人followed内页的第' + str(i) + '解析失败, 原因: ' + str(e))
                                            continue
                                else:
                                    logger.warning('用户 [%s] 在爬取关注者 [第%s页] 的时候返回内容为空, 已抓取 [%s个] 用户链接'
                                                   % (self.person_dict['username'], times, len(self.followed_urls)))
                            else:
                                logger.warning('用户 [%s] 在爬取关注者时, 抓取 [第%s页] 失败, code为: %s'
                                               % (self.person_dict['username'], times, r_inner.status_code))
                        except exceptions.ConnectionError as e:
                            logger.error('function get inner user followed connection error.')
        except exceptions.ConnectionError as e:
            logger.error('function get user followed connection error: ' + url)


if __name__ == '__main__':
    wp = WebParser('https://www.zhihu.com/people/raspberrycollections')
    wp.get_person_info()
    wp.get_user_followed()
    print(wp.person_dict)
