#!/usr/bin/env python3
# coding: utf-8

header = {
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0)'
}

# 新欢 尤雨溪, 2333
base_person_page = 'https://www.zhihu.com/people/evanyou'

zhihu_home = 'https://www.zhihu.com'
Captcha_URL_Prefix = zhihu_home + '/captcha.gif?r='
login_with_email = zhihu_home + '/login/email'
followed_url_suffix = '/followees'
followed_topic_suffix = '/topics'
active_answered_url_suffix = '/answers'
active_asked_url_suffix = '/asks'



