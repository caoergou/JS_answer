from flask import Blueprint, render_template,session

from flask import Blueprint, render_template, jsonify, url_for
from flask_login import current_user
from bson import ObjectId
from datetime import datetime

from .. import code_msg
from ..forms import PostForm
from ..models import R, BaseResult
from ..utils import gen_verify_num, verify_num
from ..extensions import mongo

bbs_index = Blueprint('bbs_index', __name__, template_folder='templates')

@bbs_index.route('/add', methods=['GET', 'POST'])
@bbs_index.route('/edit/<ObjectId:post_id>', methods=['GET', 'POST'])
def add(post_id=None):
    form = PostForm()
    # 如果表单已提交
    if form.is_submitted():
        # 如果没通过表单类中的验证
        if not form.validate():
            # 这里调用 BaseResult 类的实例作为 jsonify 的参数
            return jsonify(BaseResult(1, str(form.errors)))
        # 对于人类操作的验证
        try:
            verify_num(form.vercode.data)
        except Exception as e:
            return '<h1>{}</h1>'.format(e), 404
        # current_user 就是 models.py 文件里的 User 类的实例
        # current_user.user 就是对应到 MongoDB 数据集合中的一条用户数据
        user = current_user.user
        # 如果这个字段没有被赋值为 True ，说明用户还未激活
        # 后面的实验会使用邮箱验证来激活用户
        if not user.get('is_active'):
            return jsonify(code_msg.USER_UN_ACTIVE_OR_DISABLED)
        # 金币的处理
        user_coin = user.get('coin', 0)
        if form.reward.data > user_coin:
            msg = '悬赏金币不能大于拥有的金币，当前账号金币为：{}'.format(
               user_coin)
            return jsonify(R.ok(msg=msg))
        # 一条帖子
        post = {'title': form.title.data,
                'catalog_id': ObjectId(form.catalog_id.data),
                'is_closed': False,
                'content': form.content.data
        }
        msg = '发帖成功'
        reward = form.reward.data
        # 如果有这个参数，说明该帖子已经存在，现在是修改帖子的操作
        if post_id:
            # 增加一个“修改时间” 字段
            post['modified_at'] = datetime.utcnow()
            # 更新帖子数据
            mongo.db.posts.update_one({'_id': post_id}, {'$set': post})
            msg = '修改成功'
        # 否则，就是新建帖子的操作
        else:
            post['created_at'] = datetime.utcnow()
            post['reward'] = reward
            post['user_id'] = user['_id']
            # 修改帖子作者的金币数量
            mongo.db.users.update_one({'_id': user['_id']},
                    {'$inc': {'coin': -reward}})
            # 将新建帖子的数据添加到数据库
            mongo.db.posts.insert_one(post)
            post_id = post['_id']
        # 这里将 action 字段添加到字典中，以便传入 JS 代码中触发跳转
        return jsonify(R.ok(msg).put('action', url_for('.index')))
    # 如果是使用 GET 方法发送的请求
    ver_code = gen_verify_num()
    post = None
    title = '发布帖子'
    if post_id:
        post = mongo.db.posts.find_one_or_404({'_id': post_id})
        title = '编辑帖子'
    return render_template('jie/add.html', page_name='jie', form=form,
            ver_code=ver_code['question'], is_add=(post_id is None), post=post,
            title=title)


@bbs_index.route('/')
def index():
    # session 其实是类字典对象，可以使用 get 方法获取 Key 对应的 Value
    # 如果没有 Key ，也不会报错，而是返回默认值 None
    return render_template('base.html')
