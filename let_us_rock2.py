#!/usr/bin/env python3
# coding: utf-8
from gevent import monkey

monkey.patch_all()

import gevent
from web_parser import *
from sq_db import *
import time

coroutine_num = 100
db = SqDb()

start_time = 0


def start_work(num):
    global start_time
    start_time = time.time()
    urls = db.get_links_to_crawl(num)
    if not urls:
        # if db.get
        print('爬完了')
        return
    else:
        work = []
        for url in urls:
            work.append(gevent.spawn(single_coroutine, url))
        gevent.joinall(work)


def single_coroutine(url):
    if not url:
        print('DONE!!')
        return
    else:
        url = url[0]
    web_parser = WebParser(url)
    web_parser.get_person_info()
    web_parser.get_user_followed()
    db.save_data(web_parser.person_dict)
    db.save_link(web_parser.followed_urls)
    _url = db.get_links_to_crawl()
    _url = _url[0] if _url else []
    return single_coroutine(_url[0])


def get_efficiency():
    return db.person_count() / time.time() - start_time


start_work(coroutine_num)
