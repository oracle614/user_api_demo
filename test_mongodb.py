from pymongo import MongoClient

conn = MongoClient('', 27017)
db = conn.mydb
my_set = db.test_set

for i in my_set.find({"name": "张三"}):
    print(i)

print(my_set.findone({"name": "张三"}))