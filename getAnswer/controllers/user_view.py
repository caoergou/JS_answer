# import sys
# sys.path.append("..") #把上级目录加入到变量中
import json
from .. import models
from bson import ObjectId
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from ..extensions import mongo
from .. import utils


# 创建蓝图，第一个参数为自定义，供前端使用，第二个参数为固定写法
# 第三个参数为 URL 前缀
user_view = Blueprint('user', __name__, url_prefix='/user')


class MyEncoder(json.JSONEncoder):
    '''
    该类作为 json.dumps 方法的 cls 参数的值
    以处理特殊的、不能被序列化的值
    '''

    def default(self, o):
        '''参数 o 为被序列化的值'''
        # 如果 o 是 _id 字段或 datetime 类型的数据，将其转换为字符串
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        # 否则调用父类的同名方法触发 TypeError 异常
        super().default(o)

# @user_view.route('/')
# def config_route(app):
#     # @app.route('/')
#     def home():
#         # mongo.db 就是 getAnswer 数据库，find 方法的返回值是迭代器
#         # 这里使用 list 方法将其转换为列表
#         users = list(mongo.db.users.find())
#         # cls 参数用于处理特殊类型的数据
#         # ensure_ascii=False 使得 JSON 字符串是 UTF-8 编码
#         return json.dumps(users, cls=MyEncoder, ensure_ascii=False)

@user_view.route('/')
def home():
    # mongo.db 就是 getAnswer 数据库，find 方法的返回值是迭代器
    # 这里使用 list 方法将其转换为列表
    users = list(mongo.db.users.find())
    print(users)
    # cls 参数用于处理特殊类型的数据
    # ensure_ascii=False 使得 JSON 字符串是 UTF-8 编码
    return json.dumps(users, cls=MyEncoder, ensure_ascii=False)





@user_view.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = mongo.db.users.find_one({'email': email})
        vercode = request.form.get('vercode')   # 获取答案
        try:
            utils.verify_num(vercode)           # 验证答案
        except Exception as e:
            return '<h1>{}</h1>'.format(e), 404
        if not user:
            return jsonify({'status': 50102, 'msg': '用户不存在'})
        if not User.validate_login(user['password'], password):
            return jsonify({'status': 50000, 'msg': '密码错误'})
        # 通过验证后，把用户名添加到 session
        session['username'] = user['username']
        # redirect 用于重定向到网站首页
        # url_for 用于构造 URL ，参数为字符串：蓝图.视图函数
        return redirect(url_for('bbs_index.index'))
        return '<h1>登录成功</h1>'
    ver_code = utils.gen_verify_num()
    return render_template('user/login.html', ver_code=ver_code['question'])

@user_view.route('/register')
def register():
    return render_template('user/register.html')