#!/usr/bin/env python3
# coding: utf-8
import time

from base_setting import *
from pymongo import errors, MongoClient

logger = logging.getLogger('zhihu-logger')

client = MongoClient("mongodb://localhost:27017/", connect=False)


class MonDb(object):
    def __init__(self):
        db = client['zhihu-crawler']

        self.link_doc = db['link']
        self.info_doc = db['info']
        self.user_set = self.get_set()
        self.timer = time.time()

    def get_set(self):
        try:
            return set([i['_id'] for i in self.link_doc.find()])
        except errors.PyMongoError as e:
            logger.error('[get set]: ' + str(e))
            return set()

    def save_col(self, col_name, data):
        if len(data):
            try:
                if col_name is 'link':
                    for i in data:
                        if i.get('overwrite') and i['overwrite']:
                            self.update_link(i, {'status': i['status']})
                            continue
                        if i['_id'] not in self.user_set:
                            self.user_set.add(i['_id'])
                            del i['overwrite']
                            try:
                                self.link_doc.insert_one(i)
                            except errors.DuplicateKeyError as e:
                                logger.error('[save link] duplicate key: ' + str(i['_id']))
                        else:
                            continue
                elif col_name is 'info':
                    self.timer = time.time()
                    try:
                        self.info_doc.insert_one(data)
                    except errors.DuplicateKeyError as e:
                        logger.error('[save info] duplicate key: ' + str(data['home-page']))
                else:
                    logger.error('col_name [%s] is not exist' % col_name)
                    raise Exception('col_name is not exist')
            except errors.PyMongoError as e:
                logger.error('[save info]: ' + col_name + ': ' + str(e))
    
    def update_link(self, data, update):
        try:
            self.link_doc.find_one_and_update({'_id': data['_id']}, {'$set': update})
        except errors.PyMongoError as e:
            logger.error('[update link]: ' + str(e))

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
            logger.error('[get count]: ' + str(e))
        return count

    def get_url(self):
        url = None
        try:
            url = self.link_doc.find_one({'status': 'non-crawled'})['_id']
            if '.com/org' in url or '.com/topic' in url:
                self.update_link({"_id": url}, {'status': 'dammit'})
                self.get_url()
        except errors.PyMongoError as e:
            logger.error('[get url]: ' + str(e))
        return url


if __name__ == '__main__':
    md = MonDb()
    # mongodb 的查找和更新

    with open('pa-zhihu.log', 'r') as f:
        for line in f.readlines():
            if 'INFO || Start crawl:' in line:
                print(line)
                md.save_col('link', [
                    {
                        "_id": line[line.find('INFO || Start crawl:') + len('INFO || Start crawl:'):].strip(),
                        'status': 'non-crawled',
                        'overwrite': True
                    }
                ])
