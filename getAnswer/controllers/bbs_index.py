from flask import Blueprint, render_template,session

bbs_index = Blueprint('bbs_index', __name__, template_folder='templates')

@bbs_index.route('/')
def index():
    # session 其实是类字典对象，可以使用 get 方法获取 Key 对应的 Value
    # 如果没有 Key ，也不会报错，而是返回默认值 None
    return render_template('base.html')
