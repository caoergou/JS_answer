from flask import Blueprint, render_template, jsonify, url_for, request,redirect
from flask_login import current_user, login_required
from bson import ObjectId
from datetime import datetime
from pymongo import DESCENDING


from .. import code_msg
from ..forms import PostForm
from ..models import R, BaseResult
from ..utils import gen_verify_num, verify_num
from ..extensions import mongo,whoosh_searcher
from ..db_utils import get_page, find_one
from getAnswer.models import Page
# from 



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
@bbs_index.route('/page/<int:pn>/size/<int:size>')#用来显示指定页数和回答数的页面
@bbs_index.route('/page/<int:pn>')#只传入了 pn 参数指定页数
@bbs_index.route("/catalog/<ObjectId:catalog_id>")#传入了 catalog_id 参数用来指定提问类别
@bbs_index.route("/catalog/<ObjectId:catalog_id>/page/<int:pn>")
@bbs_index.route("/catalog/<ObjectId:catalog_id>/page/<int:pn>/size/<int:size>")#在指定类别的基础上再进行分页和指定页面帖子数量。
def index(pn=1, size=10, catalog_id=None):
    sort_key = request.values.get('sort_key', '_id')
    # 排序字段和升降序，DESCENDING 的值是 -1 ，表示降序
    sort_by = (sort_key, DESCENDING)#元组，分别是排序字段和升降序的标志
    post_type = request.values.get('type')
    filter1 = {}
    # 问答状态分类：not_closed 未结/已结；is_cream 精华帖
    if post_type == 'not_closed':
        filter1['is_closed'] = {'$ne': True}
    if post_type == 'is_closed':
        filter1['is_closed'] = True
    if post_type == 'is_cream':
        filter1['is_cream'] = True
    # 增加问答类型
    if catalog_id:
        filter1['catalog_id'] = catalog_id
    page = get_page('posts', pn=pn, filter1=filter1, size=size, sort_by=sort_by)
    return render_template("post_list.html", is_index=catalog_id is None,
            page=page, sort_key=sort_key, catalog_id=catalog_id,
            post_type=post_type)


@bbs_index.route('/post/<ObjectId:post_id>/')
@bbs_index.route('/post/<ObjectId:post_id>/page/<int:pn>/')
def post_detail(post_id, pn=1):
    '''帖子详情页的视图函数'''
    post = mongo.db.posts.find_one_or_404({'_id': post_id})
    # 当有人访问时，帖子浏览量 + 1
    if post:
        post['view_count'] = post.get('view_count', 0) + 1
        mongo.db.posts.save(post)
    post['user'] = find_one('users', {'_id': post['user_id']}) or {}
    # 获取评论
    page = get_page('comments', pn=pn, size=10,
            filter1={'post_id': post_id}, sort_by=('is_adopted', -1))
    return render_template('jie/detail.html', post=post, title=post['title'],
            page_name='jie', comment_page=page, catalog_id=post['catalog_id'])

@bbs_index.route('/comment/<ObjectId:comment_id>/')
def jump_comment(comment_id):
    comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
    post_id = comment['post_id']
    pn = 1
    if not comment.get('is_adopted', False):
        comment_index = mongo.db.comments.count({'post_id': post_id,
                '_id': {'$lt': comment_id}})
        pn = comment_index / 10
        if pn == 0 or pn % 10 != 0:
            pn += 1
    return redirect(url_for('bbs_index.post_detail', post_id=post_id, pn=pn
            ) + '#item-' + str(comment_id))

@bbs_index.route('/refresh/indexes')
def refresh_indexes():
    name = request.values.get('name')
    # 清除索引
    whoosh_searcher.clear(name)
    # 获取 IndexWriter 对象
    writer = whoosh_searcher.get_writer(name)
    for item in mongo.db[name].find({}, 
                ['_id', 'title', 'content', 'create_at', 'user_id', 'catalog_id']):
        item['obj_id'] = str(item['_id'])
        item['user_id'] = str(item['user_id'])
        item['catalog_id'] = str(item['catalog_id'])
        item.pop('_id')
        writer.add_document(**item)
    # 保存修改
    writer.commit()
    return ''

@bbs_index.route('/search')
@bbs_index.route('/search/page/<int:pn>/')
def post_search(pn=1, size=10):
    keyword = request.values.get('kw')
    if keyword is None:
        return render_template('search/list.html', title='搜索',
                message='搜索关键字不能为空!')
    whoosh_searcher.clear('posts')
    writer = whoosh_searcher.get_writer('posts')
    for item in mongo.db['posts'].find({},
            ['_id', 'title', 'content', 'create_at', 'user_id', 'catalog_id']):
        item['obj_id'] = str(item['_id'])
        item['user_id'] = str(item['user_id'])
        item['catalog_id'] = str(item['catalog_id'])
        item.pop('_id')
        writer.add_document(**item)
    # 保存修改
    writer.commit()
    with whoosh_searcher.get_searcher('posts') as searcher:
        # 解析查询字符串
        parser = qparser.MultifieldParser(['title', 'content'],
                whoosh_searcher.get_index('posts').schema)
        q = parser.parse(keyword)
        print('q:', q)
        # 搜索得到结果
        result = searcher.search_page(q, pagenum=pn, pagelen=size,
                sortedby=sorting.ScoreFacet())
        result_list = [x.fields() for x in result.results]
        # 构建页面对象
        page = Page(pn, size, result=result_list,
                has_more=result.pagecount > pn, page_count=result.pagecount,
                total=result.total)
    return render_template('search/list.html', title=keyword + '搜索结果',
            page=page, kw=keyword)