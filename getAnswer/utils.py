import random
from flask import session


# 生成验证码
def gen_verify_num():
    a = random.randint(-20, 20)
    b = random.randint(0, 50)
    data = {'question': f"{a}+{b}=?", 'answer': a+b}
    # 答案保存到 session 中
    session['ver_code'] = data['answer']
    return data


# 验证码检验
def verify_num(code):
    if code != session['ver_code']:
        raise Exception('验证码错啦！')