import random
from flask import session, current_app
from flask_mail import Message
from threading import Thread

from . import extensions


# 生成验证码
def gen_verify_num():
    a = random.randint(5, 50)
    b = random.randint(-a+1, 20)
    if b < 0:
        data = {'question': f"{a}{b}=?", 'answer': a + b}
    else:
        data = {'question': f"{a}+{b}=?", 'answer': a + b}
    # 答案保存到 session 中
    session['ver_code'] = data['answer']
    return data


# 验证码检验
def verify_num(code):
    if int(code) != int(session['ver_code']):
        raise Exception('验证码错啦！')


# 设置接收者、发送内容等
def send_email(to, subject, body, is_txt=True):
    app = current_app._get_current_object()
    print(to,subject,body,app.config.get('MAIL_USERNAME'),app.config.get('MAIL_PASSWORD'))
    
    # 因为这里的 app 对象需要传入其他线程中
    msg = Message(subject=app.config.get('MAIL_SUBJECT_PREFIX') + subject,
                  sender=app.config.get('MAIL_USERNAME'),
                  recipients=[to])
    if is_txt:
        msg.body = body
    else:
        msg.html = body
    # 多线程支持
    thr = Thread(target=send_mail_async, args=[app, msg])
    thr.start()
    return thr


# 发送邮件
def send_mail_async(app, msg):
    with app.app_context():
        extensions.mail.send(msg)