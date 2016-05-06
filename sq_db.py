#!/usr/bin/env python3
#  coding: utf-8
import sqlite3
import json
import os


class SqDb:
    def __init__(self):
        self.data_path = os.path.split(os.path.realpath(__file__))[0] + '/data.db'
        self.link_path = os.path.split(os.path.realpath(__file__))[0] + '/link.db'
        self.data_con = sqlite3.connect(self.data_path)
        self.link_con = sqlite3.connect(self.link_path)
        data_cor = self.data_con.cursor()
        link_cor = self.link_con.cursor()
        data_cor.execute("CREATE TABLE IF NOT EXISTS person_dict "
                         "(id INTEGER PRIMARY KEY AUTOINCREMENT, zhihu_ID TEXT, home_page TEXT, "
                          "agreed TEXT, gender TEXT, username TEXT, location TEXT, business TEXT, company TEXT,"
                          "position TEXT, education TEXT, major TEXT, thanks TEXT, asked TEXT, answered TEXT, post TEXT, "
                          "collect TEXT, public_edit TEXT, followed TEXT, follower TEXT)")

        link_cor.execute("CREATE TABLE IF NOT EXISTS links "
                         "(id INTEGER PRIMARY KEY AUTOINCREMENT, link TEXT, status TEXT)")
        data_cor.close()
        link_cor.close()

    def save_data(self, pdict):
        if not len(pdict):
            return
        cor = self.data_con.cursor()
        try:
            cor.execute("INSERT INTO person_dict "
                        "(zhihu_ID, home_page, agreed, gender, username, location, business, company, position, "
                        "education, major, thanks, asked, answered, post, collect, public_edit, followed, follower) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                        (pdict['zhihu-ID'], pdict['home-page'], pdict['agreed'], pdict['gender'], pdict['username'],
                         pdict['location'], pdict['business'], pdict['company'], pdict['position'], pdict['education'],
                         pdict['major'], pdict['thanks'], pdict['asked'], pdict['answered'], pdict['post'],
                         pdict['collect'], pdict['public-edit'], pdict['followed'], pdict['follower']))
        except:
            raise
        self.data_con.commit()
        cor.close()

    def save_link(self, links):
        if not len(links):
            return
        cor = self.link_con.cursor()
        for link in links:
            code = self.is_exist_links(link)
            if code == 'same':
                continue
            elif code == 'diff':
                cor.execute("UPDATE links SET status = ? WHERE link = ?;", (link['status'], link['link']))
                self.link_con.commit()
            else:
                cor.execute("INSERT INTO links (link, status) VALUES (?, ?);", (link['link'], link['status']))
                self.link_con.commit()
        cor.close()

    def is_exist_links(self, link_dict):
        cor = self.link_con.cursor()
        '''
        返回三个字符串
        same: 完全相同, 应该直接放弃, 不插入数据库
        diff: 链接相同, 状态不同, 此时应该以插入的状态为准, 进行覆盖操作
        new : 新链接, 执行插入操作
        '''
        cor.execute("SELECT * FROM links WHERE link=?;", (link_dict['link'], ))
        if cor.fetchall():
            cor.execute("SELECT * FROM links WHERE link=? AND status=?;", (link_dict['link'], link_dict['status']))
            if cor.fetchall():
                return 'same'
            else:
                return 'diff'
        else:
            return 'new'

    def get_links_to_crawl(self, num=1):
        cor = self.link_con.cursor()
        cor.execute("SELECT link FROM links WHERE status='non-crawled' LIMIT ?;", (num, ))
        res = cor.fetchall()
        return res if res else []

    # 下面这三个可以在数据库方法实现
    def get_people_count(self):
        pass

    def get_links_count(self):
        pass

    def crawled_link(self):
        pass

if __name__ == '__main__':
    db = SqDb()
    big_links = [
        {'link': 'www.baidu.com', 'status': 'non-crawled'},
        {'link': 'www.baidu.com', 'status': 'crawled'},
        {'link': 'www.example.com', 'status': 'non-crawled'},
        {'link': 'www.google.com', 'status': 'non-crawled'},
        {'link': 'www.baidu.com', 'status': 'non-crawled'},
        {'link': 'www.bing.com', 'status': 'non-crawled'}
    ]

    pdict = {
        'zhihu-ID': 'aaa',
        'home-page': 'www.baidu.com',
        'agreed': '12',
        'gender': 'male',
        'username': 'wulala',
        'location': 'shanghai',
        'company': 'baidu',
        'position': 'FE',
        'business': 'mm',
        'education': 'shanghai university',
        'major': 'chinese',
        'thanks': 12,
        'asked': 22,
        'answered': '300',
        'post': '3',
        'collect': '22',
        'public-edit': '2',
        'followed': 2000,
        'follower': '233'
    }

    print(db.get_links_to_crawl(2))

