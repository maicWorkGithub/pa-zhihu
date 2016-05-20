#!/usr/bin/env python3
# coding: utf-8
from gevent import monkey

monkey.patch_all()

import gevent
from gevent import pool
from gevent import queue
from web_parser import *
from sq_db import *
from base_setting import *
import time
import logging

logging.basicConfig(filename=log_file, level=logging.INFO)


class Slut:
    def __init__(self, coroutine_num, base_url, db_name):
        self.coroutine_num = coroutine_num
        self.db = SqDb(db_name)
        self.db.save_link([{'link': base_url, 'status': 'non-crawled', 'overwrite': False}])
        self.start_time = time.time()
        self.pool = pool.Pool(coroutine_num)
        self.link_queue = queue.Queue()
        self.person_queue = queue.Queue()
        self.write_link = None
        self.write_person = None

    def start_work(self):
        self.write_link = self.pool.spawn(self._write_link_to_db)
        self.write_person = self.pool.spawn(self._write_person_to_db)

        self.pool.spawn(self._work, self.db.get_links_to_crawl()[0][0])
        gevent.sleep(1)

        while self.pool_left:
            while self.db.get_links_to_crawl(lock=False):
                gevent.sleep(2)
                self.pool.wait_available()
                self.single_worker()
        print('OVER!!')

    def single_worker(self):
        url = self.db.get_links_to_crawl()
        if not url:
            logging.info('links num in DB: ' + str(self.db.get_data_count('links')))
            print('links num in DB: ' + str(self.db.get_data_count('links')))
            logging.info('persons num in DB: ' + str(self.db.get_data_count('persons')))
            print('persons num in DB: ' + str(self.db.get_data_count('persons')))
            if self.db.get_data_count('links'):
                print('Job Done!')
                return
        print('pool append url: ' + str(url[0][0]))
        self.pool.spawn(self._work, url[0][0])

    def _work(self, url):
        logging.info('Start crawl ' + url)
        print('Start crawl :' + url)
        web_parser = WebParser(url)
        web_parser.get_person_info()
        web_parser.get_user_followed()
        self.person_queue.put(web_parser.person_dict)
        self.link_queue.put(web_parser.followed_urls)

    def _write_link_to_db(self):
        while True:
            link = self.link_queue.get()
            try:
                self.db.save_link(link)
                logging.info('Write link to DB success.')
                print('Write link to DB success.')
            except sqlite3.Error as e:
                logging.warning('Write link to DB Fail. Caused by: ' + str(e))
                print('Write link to DB Fail. Caused by: ' + str(e))

    def _write_person_to_db(self):
        while True:
            person = self.person_queue.get()
            try:
                self.db.save_data(person)
                logging.info('Write person to DB success.')
                print('Write person to DB success.')
                print('效率: ' + str(self.efficiency))
            except sqlite3.Error as e:
                logging.warning('Write person to DB Fail. Caused by: ' + str(e))
                print('Write person to DB Fail. Caused by: ' + str(e))

    @property
    def pool_left(self):
        print('池剩余数量: ' + str(self.pool.free_count()))
        return self.pool.free_count() < (self.pool.size - 2)

    @property
    def efficiency(self):
        _time = time.time() - self.start_time
        count = self.db.get_data_count('persons')
        return count / _time


if __name__ == "__main__":
    slut = Slut(10, base_person_page, 'test2')
    slut.start_work()
