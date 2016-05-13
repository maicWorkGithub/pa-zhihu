#!/usr/bin/env python3
#  coding: utf-8
import sqlite3
import os


class SqDb:
    def __init__(self, db_name):
        self.db_path = os.path.split(os.path.realpath(__file__))[0] + '/' + db_name
        self.con = sqlite3.connect(self.db_path)
        cor = self.con.cursor()
        cor.execute("CREATE TABLE IF NOT EXISTS persons ("
                    "id          INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "zhihu_ID    TEXT, "
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
                    "id     INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "link   TEXT, "
                    "status TEXT)")
        cor.close()

    def save_data(self, pdict):
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

    def get_links_to_crawl(self, num=1):
        cor = self.con.cursor()
        cor.execute("SELECT link FROM links WHERE status !='crawled' LIMIT ?;", (num,))
        res = cor.fetchall()
        for url in res:
            cor.execute("UPDATE links SET status='lock' WHERE link=?;", url)
        self.con.commit()
        cor.close()
        return res if res else []

    # 下面这三个可以在数据库方法实现
    def get_data_count(self, table_name):
        cor = self.con.cursor()
        cor.execute("SELECT MAX(id) FROM " + table_name + ";")
        res = cor.fetchall()
        return res if res[0][0] else 0

    def get_links_count(self):
        pass

    def crawled_link(self):
        pass

if __name__ == '__main__':
    db = SqDb('db_test')
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
    db.save_link(big_links)
    db.save_data(pdict)
    print(db.get_links_to_crawl(2))

