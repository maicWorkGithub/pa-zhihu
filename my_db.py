# coding: utf-8
import pymysql


class MyDB:
    def __init__(self, identity, droptb=False):
        self.person_tb_name = 'person' + '_' + str(identity)
        self.link_tb_name = 'link' + '_' + str(identity)
        self.table_id = identity
        self.con = pymysql.connect(
            host='localhost', user='maic', passwd='1111', db='zhihu',
            cursorclass=pymysql.cursors.DictCursor)
        try:
            with self.con.cursor() as cor:
                if droptb:
                    cor.execute('DROP TABLE IF EXISTS %s;' % (self.person_tb_name, ))
                    cor.execute('DROP TABLE IF EXISTS %s;' % (self.link_tb_name, ))
                cor.execute('CREATE TABLE IF NOT EXISTS %s ('
                            "zhihu_ID    VARCHAR (50) PRIMARY KEY, "
                            "home_page   VARCHAR (200), "
                            "gender      VARCHAR (10), "
                            "username    VARCHAR (30), "
                            "location    VARCHAR (30), "
                            "business    VARCHAR (30), "
                            "company     VARCHAR (50), "
                            "`position`  VARCHAR (30), "
                            "education   VARCHAR (30), "
                            "major       VARCHAR (30), "
                            "agreed      INT, "
                            "thanks      INT, "
                            "asked       INT, "
                            "answered    INT, "
                            "post        INT, "
                            "collect     INT, "
                            "public_edit INT, "
                            "followed    INT, "
                            "follower    INT)" % (self.person_tb_name,))

            with self.con.cursor() as cor:
                cor.execute("CREATE TABLE IF NOT EXISTS %s ("
                            "link   VARCHAR (200) PRIMARY KEY, "
                            "status VARCHAR (20))" % (self.link_tb_name,))
            self.con.commit()
            cor.close()

            # with self.con.cursor() as cor:
            #     cor.execute("CREATE TABLE IF NOT EXISTS social ("
            #                 "username   VARCHAR (30) PRIMARY KEY, "
            #                 "linked_people VARCHAR (255))")
            # self.con.commit()
        except Exception:
            raise

    def save_person(self, pd):
        if not len(pd):
            return
        cor = self.con.cursor()
        sql = "SELECT * FROM %s WHERE zhihu_ID='%s';" % (self.person_tb_name, pd['zhihu_ID'])
        print('save person sql, check exists or not: ' + str(sql))
        cor.execute(sql)
        res = cor.fetchall()
        if res:
            print(pd['zhihu_ID'] + ' 已存在')
            return

        print('=' * 40)
        print('正在保存 [%s] 的信息' % pd['username'])
        print('=' * 40)

        try:
            with self.con.cursor() as cor:
                cor.execute("INSERT INTO %s "
                            "(zhihu_ID,   home_page,  gender,    username, "
                            "location,    business,   company,   `position`, "
                            "education,   major,      agreed,    thanks, "
                            "asked,       answered,   post,      collect, "
                            "public_edit, followed,   follower) "
                            "VALUES (\'%s\', \'%s\', \'%s\', \'%s\',"
                            " \'%s\', \'%s\', \'%s\', \'%s\',"
                            " \'%s\', \'%s\', \'%d\', \'%d\',"
                            " \'%d\', \'%d\', \'%d\', \'%d\',"
                            " \'%d\', \'%d\', \'%d\');"
                            % (self.person_tb_name,
                               pd['zhihu_ID'],  pd['home-page'], pd['gender'], pd['username'],
                               pd['location'],  pd['business'], pd['company'], pd['position'],
                               pd['education'], pd['major'], int(pd['agreed']), int(pd['thanks']),
                               int(pd['asked']), int(pd['answered']), int(pd['post']), int(pd['collect']),
                               int(pd['public-edit']), int(pd['followed']), int(pd['follower'])))
            self.con.commit()
            cor.close()
        except Exception:
            raise

    def save_links(self, links):
        if not len(links):
            return
        print('正在保存连接的数量: ' + str(len(links)))
        try:
            with self.con.cursor() as cor:
                for link in links:
                    code = self.is_exist_link(link)
                    if code == 'same':
                        continue
                    elif code == 'diff':
                        sql1 = "UPDATE %s SET status=\'%s\' WHERE link='%s';" % (self.link_tb_name, link['status'], link['link'])
                        print('save link, update status sql: ' + str(sql1))
                        cor.execute(sql1)
                        self.con.commit()
                    else:
                        sql2 = "INSERT INTO %s (link, status) VALUES (\'%s\', \'%s\');" % (self.link_tb_name, link['link'], link['status'])
                        print('save link, insert new sql: ' + sql2)
                        cor.execute(sql2)
                        self.con.commit()
                cor.close()
        except Exception:
            raise

    def is_exist_link(self, link):
        try:
            with self.con.cursor() as cor:
                sql = "SELECT status FROM %s WHERE link='%s';" % (self.link_tb_name, link['link'])
                print('check is exists link, sql: ' + sql)
                cor.execute(sql)
                result = cor.fetchall()
                if result:
                    if link['overwrite']:
                        if link['status'] == result[0]['status']:
                            return 'same'
                        else:
                            return 'diff'
                    else:
                        return 'same'
                else:
                    return 'new'
        except Exception:
            raise

    def get_data_count(self, tb_name):
        try:
            with self.con.cursor() as cor:
                sql = "SELECT COUNT(*) FROM %s;" % (tb_name + '_' + str(self.table_id), )
                print('get data count, sql: ' + str(sql))
                cor.execute(sql)
                res = cor.fetchall()
                return res[0][0] if res[0][0] else 0
        except Exception:
            raise

    def get_links_to_crawl(self, num=1, lock=True):
        try:
            with self.con.cursor() as cor:
                sql1 = "SELECT link FROM %s WHERE status='non-crawled' LIMIT %d;" % (self.link_tb_name, num)
                print('get link to crawled, query sql: ' + str(sql1))
                cor.execute(sql1)
                res = cor.fetchall()
                if lock:
                    for url in res:
                        sql2 = "UPDATE %s SET status='lock' WHERE link=\'%s\';" % (self.link_tb_name, url['link'])
                        print('get link to crawled, lock link sql: ' + str(sql2))
                        cor.execute(sql2)
                    self.con.commit()
                    cor.close()
                if res:
                    return res[0] if res[0] else {}
                cor.close()
        except Exception:
            raise


'''
class DBPool(MyDB):
    def __init__(self, tb_name, pool_num):
        super(DBPool, self).__init__(tb_name)
        self.pool_num = pool_num
        self.pool = []

    def get_link_to_crawl(self, ):
        try:
            with self.con.cursor() as cor:
                cor.execute("SELECT link FROM links WHERE status='non-crawled' LIMIT %d;" % self.pool_num)
                links = cor.fetch_all()
                self.pool.append(links)

        finally:
            self.con.close()
'''

if __name__ == '__main__':
    my_db = MyDB('test', droptb=True)
    big_links = [
        {'link': 'www.baidu.com', 'status': 'non-crawled', 'overwrite': True},
        {'link': 'www.baidu.com', 'status': 'crawled', 'overwrite': True},
        {'link': 'www.example.com', 'status': 'non-crawled', 'overwrite': True},
        {'link': 'www.google.com', 'status': 'non-crawled', 'overwrite': True},
        {'link': 'www.baidu.com', 'status': 'non-crawled', 'overwrite': False},
        {'link': 'www.bing.com', 'status': 'non-crawled', 'overwrite': True}
    ]

    pdict = {
        'zhihu_ID': 'aaa',
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

    my_db.save_links(big_links)
    my_db.save_person(pdict)


