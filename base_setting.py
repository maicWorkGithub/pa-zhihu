#!/usr/bin/env python3
# coding: utf-8

header = {
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.zhihu.com',
    # 'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0)'
}

cookies = {
    '_za': '6581dbbe-11ea-42ed-92a6-8dde32b2aeba',
    'udid': "AJAA0wprmAmPTprblI2WTnTcnYBUmq2mC6s=|1457627430",
    'd_c0': "ACAAb7FnqAmPTpdyLnlEl_imA0Fjvb92aK0=|1458700294",
    '_xsrf': '7e261e37eb7ad572c472c196459d512f',
    'q_c1': 'b7371fdd49c845c6b247bbde46fb8794|1461896341000|1453825985000',
    'l_n_c': '1',
    'l_cap_id': "MTQ2YjRkZjQ3MzM0NDNlOGFmOTI2NjQ2MjZjYWI3NDc=|1461981069|c5fcf5f3f4d6b9415d05e69cccb993d0d84a19ff",
    'cap_id': "OTkzOTBlYjA1YzNmNDRmMDlkNmE2ZjAwOTYxNjE3MDM=|1461981069|693cb1e7afd06c3e9917f7a6c44e0a7ebba10f33"
}

# 新欢 尤雨溪, 2333
base_person_page = 'https://www.zhihu.com/people/evanyou'

zhihu_home = 'https://www.zhihu.com'
Captcha_URL = zhihu_home + '/captcha.gif'
login_with_email = zhihu_home + '/login/email'
followed_url_suffix = '/followees'
followed_topic_suffix = '/topics'
active_answered_url_suffix = '/answers'
active_asked_url_suffix = '/asks'


log_file = 'pa-zhihu-log.txt'
