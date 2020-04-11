from getAnswer.extensions import mongo
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

def init():
    # 生成一个当前目录 'installed.lock' 文件的路径
    lock_file = os.path.join(os.getcwd(), 'installed.lock')
    # 如果检测到当前目录下已经有了这个文件就返回
    if os.path.exists(lock_file):
        return

    # 创建管理员信息
    mongo.db.users.insert_one({
        'email': 'admin',
        'username': 'admin',
        'password': generate_password_hash('admin'),
        'is_admin': True,
        'renzheng': '社区管理员',
        'vip': 5,
        'coin': 99999,
        'avatar': '/static/images/avatar/1.jpg',
        'is_active': True,
        'create_at': datetime.utcnow(),
    })


    options = [
        {
            'name': '网站标题',
            'code': 'title',
            'val': 'PyFly'
        },
        {
            'name': '网站描述',
            'code': 'description',
            'val': 'PyFly'
        },
        {
            'name': '网站关键字',
            'code': 'keywords',
            'val': 'PyFly'
        },
        {
            'name': '网站Logo',
            'code': 'logo',
            'val': '/static/images/logo.png'
        },
        {
            'name': '签到奖励区间（格式: 1-100）',
            'code': 'sign_interval',
            'val': '1-100'
        },
        {
            'name': '开启用户注册（0关闭，1开启)',
            'code': 'open_user',
            'val': '1'
        },
        {
            'name': '管理员邮箱(申请友链链接用到)',
            'code': 'email',
            'val': '981764793@qq.com'
        },
        {
            'name': '底部信息(支持html代码)',
            'code': 'footer',
            'val': 'Power by Python Flask'
        },
    ]
    result = mongo.db.options.insert_many(options)

    with open(lock_file, 'w') as file:
        file.write('1')

if __name__=="__main__":
    init()