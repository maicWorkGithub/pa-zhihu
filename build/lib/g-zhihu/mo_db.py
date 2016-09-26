#!/usr/bin/env python3
# coding: utf-8
import os
import pickle
import time
from pymongo import errors, MongoClient
from .base_setting import *

logger = logging.getLogger('zhihu-logger')

client = MongoClient("mongodb://localhost:27017/",  connect=False)


class MonDb(object):
    def __init__(self):
        db = client['zhihu-crawler']

        self.link_doc = db['link']
        self.info_doc = db['info']

        self.user_set_file = 'user-set.txt'
        self.user_set = self.read_set()
        self.timer = time.time()

    def save_set_file(self):
        pickle.dump(self.user_set, open(self.user_set_file, 'wb'), 0)

    def read_set(self):
        if os.path.isfile(self.user_set_file):
            try:
                with open(self.user_set_file, "rb") as file:
                    unpickler = pickle.Unpickler(file)
                    urls = unpickler.load()
                    if not isinstance(urls, set):
                        return set()
                    else:
                        return urls
            except EOFError:
                logger.error(EOFError)
                return set()
        else:
            return set()

    def save_col(self, col_name, data):
        if len(data):
            try:
                if col_name is 'link':
                    for i in data:
                        if i.get('overwrite') and i['overwrite']:
                            self.update_link(i, {'status': 'crawled'})
                            continue
                        if i['_id'] not in self.user_set:
                            self.user_set.add(i['_id'])
                            del i['overwrite']
                            try:
                                self.link_doc.insert_one(i)
                            except errors.DuplicateKeyError as e:
                                logger.error('save link duplicate key: ' + str(i['_id']))
                        else:
                            continue
                elif col_name is 'info':
                    self.timer = time.time()
                    try:
                        self.info_doc.insert_one(data)
                    except errors.DuplicateKeyError as e:
                        logger.error('save info duplicate key: ' + str(data['home-page']))
                else:
                    logger.error('col_name [%s] is not exist' % col_name)
                    raise Exception('col_name is not exist')
            except errors.PyMongoError as e:
                logger.error('function save col of ' + col_name + ': ' + str(e))

    def update_link(self, data, update):
        try:
            self.link_doc.find_one_and_update({'_id': data['_id']}, {'$set': update})
        except errors.PyMongoError as e:
            logger.error('function update link: ' + str(e))

    def get_count(self, col_name):
        count = 0
        try:
            if col_name == 'link':
                count = self.link_doc.count()
            elif col_name == 'info':
                count = self.info_doc.count()
            else:
                logger.error('col_name [%s] is not exist' % col_name)
                raise Exception('col_name is not exist')
        except errors.PyMongoError as e:
            logger.error('function get count: ' + str(e))
        return count

    def get_url(self):
        url = None
        try:
            url = self.link_doc.find_one({'status': 'non-crawled'})['_id']
        except errors.PyMongoError as e:
            logger.error('function get url: ' + str(e))
        return url


if __name__ == '__main__':
    md = MonDb()
    # mongodb 的查找和更新

    md.save_col('link', [
        {
            '_id': 'https://docs.python.org/3/library/pickle.html1',
            'url': 'https://docs.python.org/3/library/pickle.html1',
            'status': 'non-crawled',
            'overwrite': False
        },
        {
            '_id': 'https://docs.python.org/3/library/pickle.html2',
            'url': 'https://docs.python.org/3/library/pickle.html2',
            'status': 'non-crawled',
            'overwrite': True
        }
    ])
