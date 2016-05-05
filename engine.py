#!/usr/bin/env python3
# coding: utf-8

from .base_setting import *
from .sq_db import *
from .web_parser import *
import time

'''

先开存数据库的方法, 一个小时之后开读数据库的方法

'''

start = time.time()

web_parser = WebParser(base_person_page)

db = SqDb()

db.save_data(web_parser.person_dict, 'person')
db.save_data(web_parser.followed_urls, 'urls')

'''
这个时候去读数据库, 看有没有标记为没爬过的url, 然后多线程去抓取
todo: 测一下自增的删除中间一条之后的表现
'''

if int(time.time() - start) == 3600:
    # 也就是一小时之后
    db.read_data('urls')

