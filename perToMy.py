# coding: utf-8

from gevent import monkey

monkey.patch_all()
import pymysql
from .my_db import *
from .web_parser import *
import requests
import gevent
import time
from gevent import pool
from gevent import queue

con = pymysql.connect(
    host='localhost', user='maic', passwd='1111', db='zhihu',
    cursorclass=pymysql.cursors.DictCursor, use_unicode=True, charset="utf8")

cor = con.cursor()
start = time.time()
db = MyDB(identity='test')

_pool = pool.Pool(10)
_Q = queue.Queue()


def work(url):
    wp = WebParser(url)
    wp.get_person_info()
    _Q.put(wp.person_dict)


def write_db():
    while True:
        while not _Q.empty():

            person = _Q.get()
            try:
                db.save_person(person)
                print('-' * 30)
                print('Write person to DB success.')
                print('人物信息条目： [%s] \n 效率: [%s]' % efficiency)
                print('-' * 30)
            except Exception as e:
                print('Write person to DB Fail. Caused by: ' + str(e))
        gevent.sleep(2)


write_person = _pool.spawn(write_db)


def efficiency():
    spent = time.time() - start
    count = db.get_data_count('person')
    return count, count / spent


def run():
    links = db.get_links_to_crawl(200, True)
    while pool_left():
        if len(links) < 100:
            links.append(db.get_links_to_crawl(100, True))
        while len(links):
            _pool.wait_available()
            work(links.pop())


def pool_left():
    return _pool.free_count()
