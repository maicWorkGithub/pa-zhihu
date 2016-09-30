#!/usr/bin/env python3
# coding: utf-8

import logging
import os
header = {
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/53.0.2785.101 Safari/537.36'
}

# 新欢 尤雨溪, 2333
# base_person_page = 'https://www.zhihu.com/people/evanyou'
base_person_page = 'https://www.zhihu.com/people/光明'

zhihu_home = 'https://www.zhihu.com'
Captcha_URL = zhihu_home + '/captcha.gif'
login_with_email = zhihu_home + '/login/email'
followed_url_suffix = '/followees'
followed_topic_suffix = '/topics'
active_answered_url_suffix = '/answers'
active_asked_url_suffix = '/asks'

# setting about logging

current_dir = os.getcwd()

log_file = current_dir + '/pa-zhihu-log.txt'
a_e_log_file = current_dir + '/all_exception.log'

logger = logging.getLogger('zhihu-logger')
a_e_logger = logging.getLogger('all_exception')

ch_log = logging.StreamHandler()
file_log = logging.FileHandler(log_file, encoding='utf-8')
a_e_log = logging.FileHandler(a_e_log_file, encoding='utf-8')

fmt = "%(asctime)s || %(levelname)s || %(message)s"
fmt2 = "%(asctime)s || %(levelname)s || %(funcName)s || %(lineno)d || %(message)s"
datefmt = "%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
formatter2 = logging.Formatter(fmt=fmt2, datefmt=datefmt)

ch_log.setFormatter(formatter)
file_log.setFormatter(formatter)
a_e_log.setFormatter(formatter2)

logger.setLevel(logging.DEBUG)
a_e_logger.setLevel(logging.DEBUG)

logger.addHandler(ch_log)
logger.addHandler(file_log)
a_e_logger.addHandler(a_e_log)

# user ID set file
user_set = current_dir + '/user-set.text'
