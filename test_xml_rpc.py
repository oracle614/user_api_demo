import xmlrpc.client

user = xmlrpc.client.ServerProxy('http://127.0.0.1:5002')
print(user.getAll())