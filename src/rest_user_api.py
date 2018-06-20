import os
import uuid
import datetime
import configparser
from sign import checkSign, md5
from flask import Flask, request, jsonify, abort, session, make_response, redirect
import redis
from flask_session import Session
import os

#import sys
#sys.path.append("/usr/local/lib/python3.6/site-packages")
#from flask_cors import *

cf = configparser.ConfigParser()
conf_path = os.path.join(os.path.dirname(__file__), "db.conf")
cf.read(os.path.join(os.path.dirname(__file__), "db.conf"))


app = Flask(__name__)
app.secret_key = md5("user")
# CORS(app, supports_credentials=True)



if cf.get("DEFAULT", 'redis') == 'on':
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis.Redis(host=cf.get("REDIS", 'redis_server'), port=int(cf.get("REDIS", 'redis_port')))
    Session(app)
    redis_db1 = redis.Redis(host=cf.get("REDIS", 'redis_server'), port=int(cf.get("REDIS", 'redis_port')), db=1)

if cf.get('DEFAULT','mysql') == 'on':
    from user_model_mysql import User
else:
    from user_model_json import User

# 表单类加法接口
@app.route("/add/", methods=["GET", "POST"])
def add():
    a=request.values.get("a")
    b=request.values.get("b")
    return str(int(a)+int(b))

# Rest类减法接口
@app.route("/sub/", methods=["POST"])
def sub():
    if not request.json:
        return jsonify({"code": "100001", "msg":"数据格式错误","data": {"result": null}})
    elif not "a" in request.json or not "b" in request.json:
        return jsonify({"code": "100002", "msg":"参数a或b缺失","data": {"result": null}})
    else:
        a=request.json.get("a")
        b=request.json.get("b")
    
    result = float(a) + float(b)
    return jsonify({"code": "100000", "msg":"成功","data": {"result": result}})


# 01-注册接口，需要参数化
@app.route("/api/user/reg/", methods=["POST"])
def reg():
    if not request.json or not 'name' in request.json or not 'password' in request.json:
        abort(404) #返回404报错
    name = request.json.get('name')
    password = request.json.get('password')
    u = User()
    status = u.addUser(name, password)
    if  status is True:
        code = '100000'
        msg = '成功'
        session_id = str(uuid.uuid1())
        session['session_id'] = True
        response = make_response(jsonify({"code": code, "msg": msg, "data": {"name": name, "passwod": md5(password)}}))
        response.set_cookie('SESSION_ID', session_id, expires=120)
        return response
    elif status == -1:
        code = '100001'
        msg = '失败，用户已存在'
    else:
        code = '100002'
        msg = '失败，添加用户失败'
    return jsonify({"code": code, "msg": msg, "data": {"name": name, "passwod": md5(password)}})
    

# 02-登录接口
@app.route("/api/user/login/", methods=["POST"])
def login():
    if request.json or not 'name' in request.values or not 'password' in request.values:
        abort(404) #返回404报错
    name = request.values.get('name')
    password = request.values.get('password')
    u = User()
    status = u.checkUser(name, password)
    if  status is True:
        code = '100000'
        msg = '成功'
        session_id = str(uuid.uuid1())
        session[session_id] = True
        if app.config.get('SESSION_REDIS'):
            redis_db1.set(name, "logined")
        response = make_response('<h1>登录成功</h1>')
        response.set_cookie('PYSESSID', session_id)
        return response
    elif status is None:
        return '<h1>失败，用户不存在</h1>'
    else:
        return '<h1>失败，用户名或密码错误</h1>'


# 03-登出接口
@app.route("/api/user/logout/", methods=["GET"])
def logout():
    name = request.values.get("name")
    session_id = request.cookies.get('PYSESSID')
    if session_id in session:
        session.pop(session_id)
        redis_db1.delete(name)
    return '<h1>退出登录成功</h1>'


# 04-上传用文件接口
@app.route("/api/user/uploadImage/", methods=['GET','POST'])
def uploadImage():
    if request.method == 'POST':
        img = request.files.get('file')
        if not img:
            return '<h1>上传文件失败</h1>'
        else:
            img_name = img.filename
            img.save(os.path.join(os.path.dirname(__file__), 'uploads', img_name))
            return '<h1>上传成功</h1>'
    session_id = request.cookies.get('SESSION_ID')
    if not session_id in session:
        return '<h1>失败，尚未登录</h1>'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>上传图片</h1>
    <form action="." method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


# 05-获取所有用户信息接口
@app.route("/api/user/getUserList/", methods=["GET"])
def getUserList():
    session_id = request.cookies.get('PYSESSID')
    if not session_id in session:
        return '<h1>失败，尚未登录</h1>'
    else:
        u = User()
        data = u.getAll()
        TEMPLATE_MAIN = '''
<html><body>
<h1>用户列表</h1>
<table border=1>
    <thead>
        <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>密码</th>
        </tr>
    </thead>
    <tbody>
        {template_tr}
    </tbody>
</body></html>
        '''
        TEMPLATE_TR = '''<tr>
    <td>{id}</td>
    <td>{name}</td>
    <td>{password}</td>
</tr>'''
        template_tr = ''
        for user in data:
            template_tr += TEMPLATE_TR.format(id=user.get('id'), name=user.get('name'), password=user.get('password'))
        return TEMPLATE_MAIN.format(template_tr=template_tr)


# 06-获取token接口
@app.route("/api/user/getToken/", methods=['GET'])
def getToken():
    appid = request.values.get('appid')
    if not appid or appid != '136425':
        return '<h1>appid错误</h1>'
    token = str(uuid.uuid1()).replace("-", "").lower()
    session[token] = True
    return 'token=' + token


# 06-更新用户信息接口
@app.route("/api/user/updateUser/", methods=['POST'])
def updateUser():
    if not request.json or not 'name' in request.json or not 'password' in request.json:
        abort(404)

    token = request.values.get('token')
    if not token or not token in session:
        return jsonify({"code": '100007', "msg": '鉴权失败', "data": None})
    else:
        u = User()
        name = request.json.get('name')
        password = request.json.get('password')
        if u.updateUser(name, password):
            code = '100000'
            msg = '成功'
        else:
            code = '100007'
            msg = '更新用户信息失败'
        return jsonify({"code": code, "msg": msg, "data": {"name": name, "passwod": md5(password)}})          


# 07-带签名接口
@app.route("/api/user/delUser/", methods=['POST'])
def detUser():
    print("I am in")
    if not request.json or not 'name' in request.json:
        abort(404) #返回404报错
    elif not 'sign' in request.json or not checkSign(request.json):
        return jsonify({"code": '100007', "msg": '鉴权失败', "data": None})
    else:
        name = request.json.get('name')
        u = User()
        result = u.delUser(name)
        if result:
            return jsonify({"code": '100000', "msg": '成功', "data": {"name":name}})
        elif result == None:
            return jsonify({"code": '100003', "msg": '失败，用户不存在', "data": {"name":name}})
        else:
            return jsonify({"code": '100008', "msg": '失败，删除用户失败', "data": {"name":name}})



if __name__ == '__main__':
    app.run(port=5000)
