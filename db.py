import pymysql
import configparser

cf = configparser.ConfigParser()
cf.read("db.conf", encoding="utf-8")

conn = pymysql.connect(host=cf.get('local', 'db_host'),
                       port=int(cf.get('local', 'db_port')),
                       user=cf.get('local', 'db_user'),
                       passwd=cf.get('local', 'db_passwd'),
                       db=cf.get('local', 'db_name'),
                       charset='utf8')

cur = conn.cursor()