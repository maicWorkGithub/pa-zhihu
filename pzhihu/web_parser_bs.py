#!/usr/bin/env python3
# coding: utf-8
from base_setting import *
from bs4 import BeautifulSoup as bs
# from bs4 import error
from .client import Client
import json
import math
import logging
from requests import exceptions
from urllib import parse

logger = logging.getLogger('zhihu-logger')


class WebParser:
    def __init__(self, url):
        self.client = Client()
        self._session = self.client.return_session()
        self.followed_urls = []
        self.url = url
        self.person_dict = {
            'home_page': url,
            '_id': url[url.rfind('/') + 1:],
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
            'public-edit': 0,
            'followed': 0,
            'follower': 0
        }

    def get_person_info(self):
        try:
            quote_url = 'https://www.zhihu.com/people/' + parse.quote(self.url[self.url.rfind('/') + 1:])
            r = self._session.get(quote_url)
            logger.error(self.url + ': ' + str(r.status_code))
            if r.status_code == 200:
                try:
                    doc = bs(r.text, 'lxml')
                    self.followed_urls += [{'_id': self.url, 'overwrite': True}]
                    logger.info('拉取链接 [%s] 成功.' % self.url)
                except Exception as e:
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

            # 暂时被知乎限制的账号，页面内容为空
            if len(doc.find_all('div', class_='ProfileBan-wrapper')):
                return

            # 这里为什么会得到两个name, 另外一个明明不在left_profile里面的
            # 如果赞同为0, 直接返回

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

                self.person_dict['username'] = doc.find('span', class_='name').text
                self.person_dict['location'] = doc.find('span', class_='location').tittle
                self.person_dict['business'] = doc.find('span', class_='business').tittle
                self.person_dict['company'] = doc.find('span', class_='company').tittle
                self.person_dict['position'] = doc.find('span', class_='position').tittle
                self.person_dict['education'] = doc.find('span', class_='education').tittle
                self.person_dict['major'] = doc.find('span', class_='major').tittle

                self.person_dict['thanks'] = int(doc.find('span', class_='zm-profile-header-user-thanks').strong.text)
                items = doc.find_all('a', class_='item')
                for i in items:
                    # 定义一个函数, 把i.href传进去更好看一点
                    if 'asks' in i['href']:
                        self.person_dict['asked'] = int(i.span.text)
                    elif 'answers' in i['href']:
                        self.person_dict['answered'] = int(i.span.text)
                    elif 'posts' in i['href']:
                        self.person_dict['post'] = int(i.span.text)
                    elif 'collections' in i['href']:
                        self.person_dict['collect'] = int(i.span.text)
                    elif 'logs' in i['href']:
                        self.person_dict['public-edit'] = int(i.span.text)
                    elif 'followees' in i['href']:
                        self.person_dict['followed'] = int(i.span.text)
                    elif 'followers' in i['href']:
                        self.person_dict['follower'] = int(i.span.text)

        except exceptions.ConnectionError as e:
            logger.error(str(e))

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
                    html_doc = bs(r.text, 'lxml')
                    # 这里可以查看一下自己是多久被找到的。
                    self.followed_urls += [{'_id': str(x),
                                            'status': 'non-crawled', 'overwrite': False} for x in
                                           (html_doc.find('a', class_='author-link')['href'])]
                except Exception as e:
                    print('个人followed首页解析失败, 原因: ' + str(e))
                    logger.error('个人followed首页解析失败, 原因: ' + str(e))
                    return

                if times:
                    data = {
                        'method': 'next',
                        '_xsrf': html_doc.find('input', name='_xsrf')['value']
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
                            if r_inner.status_code == 200:
                                content = r_inner.json()
                                if content['r'] == 0:
                                    for people in content['msg']:
                                        try:
                                            self.followed_urls += [{'_id': str(x),
                                                                    'status': 'non-crawled',
                                                                    'overwrite': False}
                                                                   for x in (bs(people, 'lxml')
                                                                             .find_all('a', class_='author-link')['href'])]
                                        except Exception as e:
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
        except exceptions.ConnectionError as e:
            logger.error('function get user followed connection error: ' + url)


if __name__ == '__main__':
    wp = WebParser(base_person_page)
    wp.get_person_info()
    wp.get_user_followed()
    print(wp.followed_urls)

