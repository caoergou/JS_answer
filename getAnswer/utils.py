import random
from flask import session


# 生成验证码
def gen_verify_num():
    a = random.randint(5, 50)
    b = random.randint(-a, 20)
    if b<0:
        data = {'question': f"{a}{b}=?", 'answer': a+b}
    else:
        data = {'question': f"{a}+{b}=?", 'answer': a+b}
    # 答案保存到 session 中
    session['ver_code'] = data['answer']
    return data


# 验证码检验
def verify_num(code):
    if int(code) != int(session['ver_code']):
        raise Exception('验证码错啦！')