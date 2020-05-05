import json
from bson import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash
from random import randint
from flask import (Blueprint, render_template, request, jsonify, url_for, 
        session, redirect)
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import mongo
from .. import utils, db_utils, code_msg, forms, models
from ..models import User

# 创建蓝图，第一个参数为自定义，供前端使用，第二个参数为固定写法
# 第三个参数为 URL 前缀
user_view = Blueprint("user", __name__, url_prefix="", template_folder="templates")


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
    user_form = forms.LoginForm()
    if user_form.is_submitted():
        if not user_form.validate():
            return jsonify(models.R.fail(code_msg.PARAM_ERROR.get_msg(), str(user_form.errors)))
        utils.verify_num(user_form.vercode.data)
        user = mongo.db.users.find_one({'email': user_form.email.data})
        if not user:
            return jsonify(code_msg.USER_NOT_EXIST)
        if not models.User.validate_login(user['password'], user_form.password.data):
            return jsonify(code_msg.PASSWORD_ERROR)
        if not user.get('is_active', False):
            return jsonify(code_msg.USER_UN_ACTIVE)
        if user.get('is_disabled', False):
            return jsonify(code_msg.USER_DISABLED)
        login_user(models.User(user))
        action = request.values.get('next')
        if not action:
            action = url_for('bbs_index.index')
        return jsonify(code_msg.LOGIN_SUCCESS.put('action', action))
    logout_user()
    ver_code = utils.gen_verify_num()
    # session['ver_code'] = ver_code['answer']
    return render_template('user/login.html', ver_code=ver_code['question'], form=user_form, title='登录')



@user_view.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    # 当用户提交后，执行 if 语句块中的内容
    if form.is_submitted():
        # 如果没有通过注册表单类中定义的验证，返回错误信息
        if not form.validate():
            return jsonify(code_msg.PASSWORD_ERROR)
            return jsonify({'status': 50001, 'msy': str(form.errors)})
        # 处理验证问题，如果出现异常，捕获并返回 404
        utils.verify_num(form.vercode.data)
        # 这步用来验证邮箱是否已经被注册
        user = mongo.db.users.find_one({'email': form.email.data})
        if user:
            return jsonify(code_msg.EMAIL_EXIST)
        # 创建注册用户的基本信息
        user = {'is_active': False,
                'coin': 0,
                'email': form.email.data,
                'username': form.username.data,
                'vip': 0,
                'reply_count': 0,
                'avatar': url_for('static',
                    filename='images/avatar/{}.jpg'.format(randint(0, 12))),
                'password': generate_password_hash(form.password.data),
                'created_at': datetime.utcnow()
        }
        mongo.db.users.insert_one(user)
        utils.send_email(form.email.data, '你激活了',
                body='你已经成功注册了账号，同时完成了发送邮件功能！')
        # mongo.db.users.update_one({'username': form.username.data},
        #         {'$set': {'is_active': True}})
        return redirect(url_for('.login'))
    ver_code = utils.gen_verify_num()
    return render_template('user/register.html', ver_code=ver_code['question'],
            form=form)



def send_active_email(username, user_id, email, is_forget=False):
    code = mongo.db.active_codes.insert_one({'user_id': user_id})
    # 如果忘记密码
    if is_forget:
        body = render_template('email/user_repwd.html',
                url=url_for('user.user_pass_forget', code=code.inserted_id,
                _external=True))
        utils.send_email(email, '重置密码', body=body)
        return
    # 激活邮件内容
    body = render_template('email/user_active.html', username=username,
            url=url_for('user.user_active', code=code.inserted_id,
            _external=True))
    # 发送邮件
    utils.send_email(email, '账号激活', body=body)

@user_view.route('/active', methods=['GET', 'POST'])
def user_active():
    if request.method == 'GET':
        code = request.values.get('code')
        if code:
            user_id = mongo.db.active_codes.find_one(
                    {'_id': ObjectId(code)})['user_id']
            # 可以激活账户了
            if user_id:
                # 通过激活验证后，删掉 user_id 关联的 active_codes
                mongo.db.active_codes.delete_many({'user_id': ObjectId(user_id)})
                # 激活账户
                mongo.db.users.update({'_id': user_id},
                        {"$set": {'is_active': True}})
                # 根据 user_id 在数据库中取到用户对象
                user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
                # 登录
                login_user(models.User(user))
                return render_template('user/activate.html')
        # 如果没有登录,显示错误
        if not current_user.is_authenticated:
            abort(403)
        return render_template('user/activate.html')
    user = current_user.user
    # 删除
    mongo.db.active_codes.delete_many({'user_id': ObjectId(user['_id'])})
    # 发送邮件
    send_active_email(user['username'], user['_id'], user['email'])
    return jsonify(code_msg.RE_ACTIVATE_MAIL_SEND.put('action',
            url_for('user.active')))

@user_view.route('/forget', methods=['POST', 'GET'])
def user_pass_forget():
    code = request.args.get('code')
    mail_form = forms.SendForgetMailForm()
    if mail_form.is_submitted():
        if not mail_form.validate():
            return jsonify(code_msg.PARAM_ERROR)
        email = mail_form.email.data
        ver_code = mail_form.vercode.data
        utils.verify_num(ver_code)
        # 从数据库 users 集合中取到邮箱关联的用户
        user = mongo.db.users.find_one({'email': email})
        # 如果数据库中没找到用户
        if not user:
            return jsonify(code_msg.USER_NOT_EXIST)
        # 发送忘记密码邮件
        send_active_email(user['username'], user_id=user['_id'],
                email=email, is_forget=True)
        action = request.values.get('next')
        if not action:
            action = url_for('user.login')
        return jsonify(code_msg.RE_PWD_MAIL_SEND.put('action', action))
    has_code = False
    user = None
    # 用户点击重置密码链接访问时
    if code:
        # send_active_email 中会生成
        active_code = mongo.db.active_codes.find_one({'_id': ObjectId(code)})
        # 重置连接失效
        if not active_code:
            return render_template('user/forget.html', page_name='user',
                    has_code=True, code_invalid=True)
        has_code = True
        # 拿到用户
        user = mongo.db.users.find_one({'_id': active_code['user_id']})
    ver_code = utils.gen_verify_num()
    return render_template('user/forget.html', page_name='user',
            ver_code=ver_code['question'], code=code, has_code=has_code,
            user=user)

@user_view.route('/repass', methods=['POST'])
def user_repass():
    if 'email' in request.values:
        pwd_form = forms.ForgetPasswordForm()
        if not pwd_form.validate():
            return jsonify(models.R.fail(code_msg.PARAM_ERROR.get_msg(),
                    str(pwd_form.errors)))
        email = pwd_form.email.data
        ver_code = pwd_form.vercode.data
        code = pwd_form.code.data
        password = pwd_form.password.data
        # 验证码校验
        utils.verify_num(ver_code)
        # 查询、删除邮箱激活码
        active_code = mongo.db.active_codes.find_one_or_404(
                {'_id': ObjectId(code)})
        mongo.db.active_codes.delete_one({'_id': ObjectId(code)})
        # 更新用户密码
        user = mongo.db.users.update(
                {'_id': active_code['user_id'], 'email': email},
                {'$set': {'password': generate_password_hash(password)}}
        )
        if user['nModified'] == 0:
            return jsonify(code_msg.CHANGE_PWD_FAIL.put('action',
                    url_for('user.login')))
        return jsonify(code_msg.CHANGE_PWD_SUCCESS.put('action',
                url_for('user.login')))
    if not current_user.is_authenticated:
        return redirect(url_for('user.login'))
    pwd_form = forms.ChangePassWordForm()
    if not pwd_form.validate():
        return jsonify(models.R.fail(code_msg.PARAM_ERROR.get_msg(),
                str(pwd_form.errors)))
    nowpassword = pwd_form.nowpassword.data
    password = pwd_form.password.data
    user = current_user.user
    if not models.User.validate_login(user['password'], nowpassword):
        raise models.GlobalApiException(code_msg.PASSWORD_ERROR)
    mongo.db.users.update({'_id': user['_id']},
            {'$set': {'password': generate_password_hash(password)}})
    return jsonify(models.R.ok())

# 定义登出函数
@user_view.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # 只需要执行 logout_user 方法即可，十分便捷
    logout_user()
    # 重定向到首页
    return redirect(url_for('bbs_index.index'))


@user_view.route('/<ObjectId:user_id>')
@login_required
def user_home(user_id):
    '''用户主页'''
    # 在数据库 user 集合中查找主键为 user_id 的数据
    user = mongo.db.users.find_one_or_404({'_id': user_id})
    return render_template('user/home.html', user=user)

@user_view.route('/message')
@user_view.route('/message/page/<int:pn>')
@login_required
def user_message(pn=1):
    '''用户通知消息页面'''
    user = current_user.user
    if user.get('unread', 0) > 0:
        # 更新未读消息重新为零
        mongo.db.users.update({'_id': user['_id']}, {'$set': {'unread': 0}})
    message_page = db_utils.get_page('messages', pn,
            filter1={'user_id': user['_id']}, sort_by=('_id', -1))
    return render_template('user/message.html', user_page='message',
            page_name='user', page=message_page)

@user_view.route('/message/remove', methods=['POST'])
@login_required
def remove_message():
    user = current_user.user
    if request.values.get('all') == 'true':
        mongo.db.messages.delete_many({'user_id': user['_id']})
    elif request.values.get('id'):
        msg_id = ObjectId(request.values.get('id'))
        mongo.db.messages.delete_one({'_id': msg_id})
    return jsonify(models.BaseResult())

@user_view.route('/set', methods=['GET', 'POST'])
@login_required
def user_set():
    if request.method == 'POST':
        include_keys = ['username', 'avatar', 'desc', 'city', 'sex']
        data = request.values
        update_data = {}
        for key in data.keys():
            if key in include_keys:
                update_data[key] = data.get(key)
        mongo.db.users.update({'_id': current_user.user['_id']},
                {'$set': update_data})
        return jsonify('修改成功')
    return render_template('user/set.html', user_page='set',
            page_name='user', title='基本设置')

