#!/usr/bin/env python3
# coding: utf-8
from web_parser import *
from sq_db import *
from base_setting import *
import time
import logging

logging.basicConfig(filename=log_file, level=logging.INFO)


class Slut:
    def __init__(self, base_url, db_name):
        self.db = SqDb(db_name)
        self.db.save_link([{'link': base_url, 'status': 'non-crawled', 'overwrite': False}])
        self.start_time = time.time()

    def start_work(self):

        self._work(self.db.get_links_to_crawl()[0][0])
        time.sleep(3)
        while self.db.get_links_to_crawl(lock=False):
            print('数据库内条目数： [%s], 效率: [%s]' % self.efficiency)
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
        self._work(url[0][0])

    def _work(self, url):
        logging.info('Start crawl ' + url)
        print('Start crawl :' + url)
        web_parser = WebParser(url)
        web_parser.get_person_info()
        web_parser.get_user_followed()
        self.db.save_link(web_parser.followed_urls)
        self.db.save_data(web_parser.person_dict)

    @property
    def efficiency(self):
        _time = time.time() - self.start_time
        count = self.db.get_data_count('persons')
        return count, count / _time


if __name__ == "__main__":
    slut = Slut(base_person_page, 'test1')
    slut.start_work()
