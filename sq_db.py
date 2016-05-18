#!/usr/bin/env python3
#  coding: utf-8
import sqlite3
import time
import os


class SqDb:
    def __init__(self, db_name):
        self.db_path = os.path.split(os.path.realpath(__file__))[0] + '/' + db_name + '.db'
        self.con = sqlite3.connect(self.db_path)
        cor = self.con.cursor()
        cor.execute("CREATE TABLE IF NOT EXISTS persons ("
                    "zhihu_ID    TEXT PRIMARY KEY, "
                    "home_page   TEXT, "
                    "agreed      TEXT, "
                    "gender      TEXT, "
                    "username    TEXT, "
                    "location    TEXT, "
                    "business    TEXT, "
                    "company     TEXT, "
                    "position    TEXT, "
                    "education   TEXT, "
                    "major       TEXT, "
                    "thanks      TEXT, "
                    "asked       TEXT, "
                    "answered    TEXT, "
                    "post        TEXT, "
                    "collect     TEXT, "
                    "public_edit TEXT, "
                    "followed    TEXT, "
                    "follower    TEXT)")

        cor.execute("CREATE TABLE IF NOT EXISTS links ("
                    "link   TEXT PRIMARY KEY, "
                    "status TEXT)")
        cor.close()

    def save_data(self, pdict):
        print('=' * 30)
        print('正在保存 [%s] 的信息' % pdict['username'])
        print('=' * 30)
        if not len(pdict):
            return
        cor = self.con.cursor()
        try:
            cor.execute("INSERT INTO persons "
                        "(zhihu_ID,   home_page, agreed,    gender, "
                        "username,    location,  business,  company, "
                        "position,    education, major,     thanks, "
                        "asked,       answered,  post,      collect, "
                        "public_edit, followed,  follower) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                        (pdict['zhihu-ID'], pdict['home-page'], pdict['agreed'], pdict['gender'],
                         pdict['username'], pdict['location'], pdict['business'], pdict['company'],
                         pdict['position'], pdict['education'], pdict['major'], pdict['thanks'],
                         pdict['asked'], pdict['answered'], pdict['post'], pdict['collect'],
                         pdict['public-edit'], pdict['followed'], pdict['follower']))
        except:
            raise
        self.con.commit()
        cor.close()

    def save_link(self, links):
        print('正在保存链接的数量为: [%s]' % len(links))
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

    def get_links_to_crawl(self, num=1, lock=True):
        time.sleep(3)
        cor = self.con.cursor()
        cor.execute("SELECT link FROM links WHERE status='non-crawled' LIMIT ?;", (num,))
        res = cor.fetchall()
        if lock:
            for url in res:
                cor.execute("UPDATE links SET status='lock' WHERE link=?;", url)
            self.con.commit()
            cor.close()
        print('查询到的链接为: [%s], 此时的Lock条件为: [%s]' % (res, lock))
        return res if res else []

    # 下面这三个可以在数据库方法实现
    def get_data_count(self, table_name):
        cor = self.con.cursor()
        cor.execute("SELECT COUNT (*) FROM " + table_name + ";")
        res = cor.fetchall()
        print(' [%s] 表中有 [%s] 条数据' % (table_name, res[0][0]))
        return res if res[0][0] else 0

    def show_table_data(self, table_name):
        cor = self.con.cursor()
        cor.execute("SELECT * FROM " + table_name + ";")
        return cor.fetchall()

if __name__ == '__main__':
    db = SqDb('test1')
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
    # db.save_link(big_links)
    # db.save_data(pdict)
    print(db.show_table_data('persons'))
