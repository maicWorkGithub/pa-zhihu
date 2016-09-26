#!/usr/bin/env python3
#  coding: utf-8
import sqlite3
import os
import logging
from base_setting import *
import locale

def_lang, def_coding = locale.getdefaultlocale()

logging.basicConfig(filename=log_file, level=logging.INFO)


class SqDb:
    def __init__(self, db_name):
        self.db_path = os.path.split(os.path.realpath(__file__))[0] + '/' + db_name + '.db'
        self.con = sqlite3.connect(self.db_path)
        cor = self.con.cursor()
        # 社交网络的分析应该还存入每个人的关注者的链接，甚至是关注本人的链接
        # 这样的单个个人信息会非常庞大。
        # 个人动态的时效性要求更高。这个先不弄了吧
        cor.execute("CREATE TABLE IF NOT EXISTS persons ("
                    "zhihu_ID    TEXT PRIMARY KEY, "
                    "home_page   TEXT, "
                    "gender      TEXT, "
                    "username    TEXT, "
                    "location    TEXT, "
                    "business    TEXT, "
                    "company     TEXT, "
                    "position    TEXT, "
                    "education   TEXT, "
                    "major       TEXT, "
                    "agreed      INT, "
                    "thanks      INT, "
                    "asked       INT, "
                    "answered    INT, "
                    "post        INT, "
                    "collect     INT, "
                    "public_edit INT, "
                    "followed    INT, "
                    "follower    INT)")

        cor.execute("CREATE TABLE IF NOT EXISTS links ("
                    "link   TEXT PRIMARY KEY, "
                    "status TEXT)")
        cor.close()

    def save_data(self, pdict):
        if not len(pdict):
            return
        print('=' * 30)
        logging.info('正在保存 [%s] 的信息' % pdict['username'])
        # print('正在保存 [%s] 的信息' % pdict['username'])
        print('正在保存 [%s] 的信息' % pdict['username'].encode(def_coding, 'ignore'))
        print('=' * 30)
        cor = self.con.cursor()
        cor.execute("SELECT * FROM persons WHERE zhihu_ID=?;", (pdict['zhihu-ID'], ))
        if cor.fetchall():
            print('用户资料已存在')
            cor.close()
            return
        try:
            cor.execute("INSERT INTO persons "
                        "(zhihu_ID,   home_page,  gender,    username, "
                        "location,    business,   company,   position, "
                        "education,   major,      agreed,    thanks, "
                        "asked,       answered,   post,      collect, "
                        "public_edit, followed,   follower) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                        (pdict['zhihu-ID'],    pdict['home-page'],   pdict['gender'],     pdict['username'],
                         pdict['location'],    pdict['business'],    pdict['company'],    pdict['position'],
                         pdict['education'],   pdict['major'],       pdict['agreed'],     pdict['thanks'],
                         pdict['asked'],       pdict['answered'],    pdict['post'],       pdict['collect'],
                         pdict['public-edit'], pdict['followed'],    pdict['follower']))
        except:
            raise
        self.con.commit()
        cor.close()

    def save_link(self, links):
        print('正在保存链接的数量: [%s]' % len(links))
        logging.info('正在保存链接的数量: [%s]' % len(links))
        if not len(links):
            return
        cor = self.con.cursor()
        for link in links:
            code = self.is_exist_links(link)
            if code == 'same':
                continue
            elif code == 'diff':
                cor.execute("UPDATE links SET status = ? WHERE link = ?;", (link['status'], link['link']))
                self.con.commit()
            else:
                cor.execute("INSERT INTO links (link, status) VALUES (?, ?);", (link['link'], link['status']))
                self.con.commit()
        cor.close()

    def is_exist_links(self, link_dict):
        cor = self.con.cursor()
        '''
        返回三个字符串
        same: 完全相同, 应该直接放弃, 不插入数据库.或者是重复数据
        diff: 链接相同, 状态不同, 此时应该以插入的状态为准, 进行覆盖操作
        new : 新链接, 执行插入操作
        '''
        cor.execute("SELECT * FROM links WHERE link=?;", (link_dict['link'], ))
        result = cor.fetchall()
        if result:
            if link_dict['overwrite']:
                if link_dict['status'] == result[0][1]:
                    return 'same'
                else:
                    return 'diff'
            else:
                return 'same'
        else:
            return 'new'

    def get_links_to_crawl(self, num=1, lock=True):
        cor = self.con.cursor()
        cor.execute("SELECT link FROM links WHERE status='non-crawled' LIMIT ?;", (num,))
        res = cor.fetchall()
        if lock:
            for url in res:
                cor.execute("UPDATE links SET status='lock' WHERE link=?;", (url,))
            self.con.commit()
            cor.close()
        if res:
            return res if res[0] else []

    # 下面这三个可以在数据库方法实现
    def get_data_count(self, table_name):
        cor = self.con.cursor()
        cor.execute("SELECT COUNT (*) FROM " + table_name + ";")
        res = cor.fetchall()
        return res[0][0] if res[0][0] else 0

    def show_table_data(self, table_name):
        cor = self.con.cursor()
        cor.execute("SELECT * FROM " + table_name + ";")
        return cor.fetchall()

if __name__ == '__main__':
    db = SqDb('test1')
    big_links = [
        {'link': 'www.baidu.com', 'status': 'non-crawled', 'overwrite': True},
        {'link': 'www.baidu.com', 'status': 'crawled', 'overwrite': True},
        {'link': 'www.example.com', 'status': 'non-crawled', 'overwrite': True},
        {'link': 'www.google.com', 'status': 'non-crawled', 'overwrite': True},
        {'link': 'www.baidu.com', 'status': 'non-crawled', 'overwrite': False},
        {'link': 'www.bing.com', 'status': 'non-crawled', 'overwrite': True}
    ]

    pdict = {
        'zhihu-ID': 'aaa',
        'home-page': 'www.baidu.com',
        'gender': 'male',
        'username': 'wulala',
        'location': 'shanghai',
        'company': 'baidu',
        'position': 'FE',
        'business': 'mm',
        'education': 'shanghai university',
        'major': 'chinese',
        'agreed': '12',
        'thanks': 12,
        'asked': 22,
        'answered': '300',
        'post': '3',
        'collect': '22',
        'public-edit': '2',
        'followed': 2000,
        'follower': '233'
    }
    # db.save_link(big_links)
    # db.save_data(pdict)
    print(db.get_data_count('persons'))
