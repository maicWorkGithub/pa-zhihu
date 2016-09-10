#!/usr/bin/env python3
# coding: utf-8
from web_parser import *
from mo_db import MonDb
from base_setting import *
import time
import logging

logger = logging.getLogger('zhihu-logger')


class Single(object):
    def __init__(self):
        self.db = MonDb()
        self.db.save_col('link', [{'_id': base_person_page, 'status': 'non-crawled', 'overwrite': False}])
        self.start_time = time.time()
        self.user_set = 'user-set.txt'
        self.counter = 0
    
    def worker(self):
        while True:
            try:
                url = self.db.get_url()
                if not url:
                    break
                self.counter += 1
                logger.info('person info: %d, efficiency: %d' % self.efficiency)
                logger.info('Start crawl: ' + url)
                web_parser = WebParser(url)
                web_parser.get_person_info()
                web_parser.get_user_followed()
                
                web_parser.person_dict['follower-url'] = [u["_id"] for u in web_parser.followed_urls]
                
                self.db.save_col('link', web_parser.followed_urls)
                self.db.save_col('info', web_parser.person_dict)
                if self.counter == 5:
                    self.db.save_set_file()
                    self.counter = 0
            except Exception as e:
                logger.error('all exception in while: ' + str(e))
                self.db.save_set_file()
            except KeyboardInterrupt as e:
                logger.error('base exception in while: ' + str(e))
                self.db.save_set_file()
                break
                # time.sleep(1)
    
    @property
    def efficiency(self):
        _time = time.time() - self.start_time
        count = self.db.get_count('info')
        return count, count / _time

if __name__ == '__main__':
    s = Single()
    s.worker()
