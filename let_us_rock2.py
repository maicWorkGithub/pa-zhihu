#!/usr/bin/env python3
# coding: utf-8
from gevent import monkey

monkey.patch_all()

import gevent
from gevent import pool
from gevent import queue
from base_setting import *
from web_parser import *
from sq_db import *
import time


class Slut:
    def __init__(self, coroutine_num, base_url, db_name):
        self.coroutine_num = coroutine_num
        self.db = SqDb(db_name)
        self.db.save_link(base_url)
        self.start_time = time.time()
        self.pool = pool.Pool(coroutine_num)
        self.queue = queue.Queue()
        self.status = 'stopped'
        # 第一次爬100个人作为实验
        self.data_limit = 100

    def start_work(self):
        self.status = 'running'
        while self.db.get_data_count('links'):
            self.pool.wait_available()
            self.single_worker()
            if self.db.get_data_count('persons') > self.data_limit:
                gevent.killall(self.pool)
                self.status = 'stopped'
        print(self.status)

        # while self.pool_left:
        #     # 这个不知道是干嘛用的
        #     gevent.sleep(1)

    def single_worker(self):
        url = self.db.get_links_to_crawl()
        if not url:
            print(self.db.get_data_count('links'))
            print(self.db.get_data_count('persons'))
            if self.db.get_data_count('links'):
                print('Job Done!')
                return
        self.pool.spawn(self._work, url[0])

    def _work(self, url):
        web_parser = WebParser(url)
        web_parser.get_person_info()
        web_parser.get_user_followed()
        self.db.save_data(web_parser.person_dict)
        self.db.save_link(web_parser.followed_urls)

    @property
    def pool_left(self):
        return self.pool.size - self.pool.free_count()

if __name__ == "__main__":
    slut = Slut(10, base_person_page, 'test1')
