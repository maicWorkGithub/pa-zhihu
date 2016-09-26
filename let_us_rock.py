#!/usr/bin/env python3
# coding: utf-8

from gevent import monkey

monkey.patch_all()
import gevent
from base_setting import *
from sq_db import *
import requests

db = SqDb()
work_num = 10

tieba_url_start = 'http://tieba.baidu.com/p/4003196488?pn=1'


# 除了给每个url三个状态之外,还可以用这个方法实现:
# 数据库只暴露出一个对外接口,这个接口管理所有的读写,这个接口每次都看自己的池里面保证有给定数量的url(比如5个),然后分给每个线程
#


# 返回每个页面的用户名检测

def get_username_list(url):
    if not url:
        print("DONE!")
        return
    url = url[0]
    r = requests.get(url)
    if r.status_code != 200:
        print('第 [%s] 页抓取失败, code: %s' % (url[url.find('pn=') + 3:], r.status_code))
    print('第 [%s] 页成功了' % (url[url.find('pn=') + 3:],))
    db.save_link([{'link': url, 'status': 'crawled'}])
    _url = db.get_links_to_crawl()
    get_username_list(_url[0] if _url else [])


# 这个是先往数据库里塞500个链接, 开始之前先跑一下, 之后就关了好了
def create_db():
    cor = db.link_con.cursor()
    for i in range(1, 500):
        cor.execute("INSERT INTO links (link, status) VALUES (?, ?);",
                    (tieba_url_start[:-1] + str(i), 'non-crawled'))

    db.link_con.commit()
    cor.close()


def get_tieba_work(num):
    urls = db.get_links_to_crawl(num)
    works = []
    if not urls:
        print('爬完了')
        return
    for url in urls:
        works.append(gevent.spawn(get_username_list, url))
    gevent.joinall(works)


# def get_tieba_work(num):
#     url = db.get_links_to_crawl(num)[0]
#     get_username_list(url)

# create_db()
get_tieba_work(20)
