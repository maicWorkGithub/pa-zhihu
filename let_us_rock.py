#!/usr/bin/env python3
# coding: utf-8

from gevent import monkey

monkey.patch_all()
import gevent
import sys
from base_setting import *
from sq_db import *
# from web_parser import *
import os
import requests
from lxml import html

# def login():
#     if (os.path.isfile('cookies.json')):
#         assert ('cookies.json', str)
#
db = SqDb()
work_num = 10

# def work(url):
#     web_parser = WebParser(url)
#     web_parser.get_person_info()
#     web_parser.get_user_followed()
#     db.save_data(web_parser.person_dict)
#     db.save_link(web_parser.followed_urls)

tieba_url_start = 'http://tieba.baidu.com/p/4003196488?pn=1'


# 返回每个页面的用户名检测

def get_username_list(url):
    r = requests.get(url)
    if r.status_code != 200:
        print('第 [%s] 页抓取失败, code: %s' % (url[-1:], r.status_code))
    print('第 [%s] 页' % (url[-1:],))
    db.save_link([{'link': url, 'status': 'crawled'}])
    get_username_list(db.get_links_to_crawl()[0])


def get_tieba_work(init_url):
    cor = db.link_con.cursor()
    for i in range(1, 500):
        cor.execute("INSERT INTO links (link, status) VALUES (?, ?);", (init_url[:-1] + str(i), 'non-crawled'))

    db.link_con.commit()
    cor.close()

    get_username_list(init_url)

    urls = db.get_links_to_crawl(work_num)
    works = []
    if not urls:
        urls = [init_url]
    for url in range(urls):
        works.append(gevent.spawn(get_username_list, url))
    gevent.joinall(works)

get_tieba_work(tieba_url_start)


'''
这里是往链接数据库里塞上500个百度贴吧的链接, 测试

'''

#
