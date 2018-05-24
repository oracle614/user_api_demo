import json
import configparser
import pymysql
from sign import md5


class User(object):
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read('db.conf', encoding="utf-8")

        self.conn = pymysql.connect(host=cf.get('local', 'db_host'),
                               port=int(cf.get('local', 'db_port')),
                               user=cf.get('local', 'db_user'),
                               passwd=cf.get('local', 'db_passwd'),
                               db=cf.get('local', 'db_name'),
                               charset='utf8')

        self.cur = self.conn.cursor()
        
    def __del__(self):
        self.cur.close()
        self.conn.close()

    def getAll(self):
        self.cur.execute("select * from user")
        result = []
        for item in self.cur.fetchall():
            result.append(dict(zip(('id', 'name', 'passwd'), item)))
        return result

    def getUserById(self, id):
        self.cur.execute("select * from user where id=%d" % int(id))
        result = self.cur.fetchone()
        if result:
            return dict(zip(('id', 'name', 'passwd'), result))
        else:
            return None


    def getUserByName(self, name):
        self.cur.execute("select * from user where name='%s'" % name)
        result = self.cur.fetchone()
        if result:
            return dict(zip(('id', 'name', 'passwd'), result))
        else:
            return None

    def checkUser(self, name, passwd):
        if self.getUserByName(name):
            return True if md5(passwd) == self.getUserByName(name).get('passwd') else False
        else:
            return None

    def addUser(self, name, passwd): 
        if self.getUserByName(name):
            return -1
        else:
            self.cur.execute("insert into user (name, passwd) values ('%s', '%s')" % (name, md5(passwd)))
            self.conn.commit()
            return self.checkUser(name, passwd)

    def modifyUser(self, name, passwd): 
        if not self.getUserByName(name):
            return -1
        else:
            self.cur.execute("update user set name='%s', passwd='%s' where name='%s'" % (name, md5(passwd),name))
            self.conn.commit()
            return self.checkUser(name, passwd)

    def updateUser(self, name, passwd): 
        if self.getUserByName(name):
            return self.modifyUser(name, passwd)
        else:
            return self.addUser(name, passwd)

    def delUser(self, name): 
        user = self.getUserByName(name)
        if not user:
            return None
        else:
            self.cur.execute("delete from user where name='%s'" % name)
            self.conn.commit()
            return False if self.getUserByName(name) else True


if __name__ == '__main__':
    u = User()
    print(u.getAll())
    # print(u.getUserById(1))
    # print(u.getUserByName("张三"))
    # print(md5('123456'))
    # print(u.checkUser("张三", '123456'))
    # print(u.addUser("李四", '123456'))
    # print(u.modifyUser("李四", '123456'))
    # print(u.delUser("李四"))