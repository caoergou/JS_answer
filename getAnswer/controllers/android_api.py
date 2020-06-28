import json
import random
from datetime import datetime
from random import randint

from bson import ObjectId, json_util
from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required
from flask_uploads import UploadNotAllowed
from werkzeug import generate_password_hash

from getAnswer.controllers.user_view import send_active_email
from getAnswer.db_utils import find_one, get_page
from getAnswer.models import Page

from .. import code_msg, db_utils, models
from ..extensions import mongo, upload_photos
from ..models import R

android = Blueprint("android", __name__, url_prefix="android")



@android.route('/user/login', methods=['POST'])
def login():
    email = request.values.get('email')
    password = request.values.get('password')
    user = mongo.db.users.find_one({'email': email})
    if not user:
        return jsonify(R.fail(msg="没有该用户"))#jsonify(code_msg.USER_NOT_EXIST)
    if not models.User.validate_login(user['password'], password):
        return jsonify(R.fail(msg="密码错误"))
    if not user.get('is_active', False):
        return jsonify(R.fail(msg="该账户尚未激活"))
    if user.get('is_disabled', False):
        return jsonify(R.fail(msg="该账户已被禁用"))
    
    res_dict = {
        'email':user['email'],
        'username':user['username'],
        'avatar':user['avatar']
    }
    res = R.ok(data = res_dict,msg="登录成功")
    return jsonify(res)

@android.route('/user/register', methods=['POST'])
def register():
    email = request.values.get('email')
    password = request.values.get('password')
    username = request.values.get('username')
    user = mongo.db.users.find_one({'email': email})
    # 这步用来验证邮箱是否已经被注册
    if user:
        return jsonify(R.fail(msg="邮箱已被注册"))
    # 创建注册用户的基本信息
    user = {'is_active': False,
            'coin': 0,
            'email': email,
            'username': username,
            'vip': 0,
            'reply_count': 0,
            'avatar': url_for('static',
                filename='images/avatar/{}.jpg'.format(randint(0, 12))),
            'password': generate_password_hash(password),
            'created_at': datetime.utcnow()
    }
    mongo.db.users.insert_one(user)
    send_active_email(user['username'], user['_id'], user['email'])
    res_dict = {
        'eamil':user['email'],
        'username':user['username'],
        'avatar':user['avatar']
    }
    return jsonify(R.ok(msg="注册成功，请查看邮箱激活！",data=res_dict))

@android.route('/question', methods=['post'])
def question(KEY_PAGE=1, size=5):
    KEY_PAGE = int(request.values.get('KEY_PAGE'))
    # size = 5 if int(request.values.get('size')) else int(request.values.get('size'))
    size = size if size > 0 else 5     # 每页展示数量
    total = mongo.db['posts'].count()    # 符合要求的数据的数量
    skip_count = size * (KEY_PAGE - 1)        # 略过的数据的数量
    result = []
    has_more = total > KEY_PAGE * size        # 布尔值，是否有更多数据待展示
    if total - skip_count > 0:
        # 查找数据
        result =json_util.dumps(mongo.db['posts'].find(limit=size),ensure_ascii=False) 
        if skip_count > 0:
            result.skip(skip_count)
        t = json.loads(result)
        for i in t[:]:
            i['user'] = find_one('users', {'_id': i['user_id']['$oid']})
        # print(t)
        return json_util.dumps(t,ensure_ascii=False)
    else:
        return jsonify([])

@android.route('/answer', methods=['post'])
def answer(KEY_PAGE=1, size=5):
    question_id = request.values.get('id')
    # size = 5 if int(request.values.get('size')) else int(request.values.get('size'))
    size = size if size > 0 else 5     # 每页展示数量
    total = mongo.db['comments'].count(filter={'post_id':ObjectId(question_id)})    # 符合要求的数据的数量
    skip_count = size * (KEY_PAGE - 1)        # 略过的数据的数量
    result = []
    has_more = total > KEY_PAGE * size        # 布尔值，是否有更多数据待展示
    # if total - skip_count > 0:
        # 查找数据
    result =json_util.dumps(mongo.db['comments'].find(filter={'post_id': ObjectId(question_id)},limit=size),ensure_ascii=False) 
    if skip_count > 0:
        result.skip(skip_count)
    t = json.loads(result)
    for i in t[:]:
        i['user'] = find_one('users', {'_id': i['user_id']['$oid']})
    # for i in t[:]:
    #     i['user'] = find_one('users', {'_id': i['user_id']['$oid']})
    return json_util.dumps(t,ensure_ascii=False)
    # # size = 5 if int(request.values.get('size')) else int(request.values.get('size'))
    # size = size if size > 0 else 5     # 每页展示数量
    # total = mongo.db['posts'].count()    # 符合要求的数据的数量
    # skip_count = size * (KEY_PAGE - 1)        # 略过的数据的数量
    # result = []
    # has_more = total > KEY_PAGE * size        # 布尔值，是否有更多数据待展示
    # if total - skip_count > 0:
    #     # 查找数据
    #     result =json_util.dumps(mongo.db['posts'].find(limit=size),ensure_ascii=False) 
    #     t = json.loads(result)
    #     for i in t[:]:
    #         i['user'] = find_one('users', {'_id': i['user_id']['$oid']})
    #     # print(t)
    # return json_util.dumps(t,ensure_ascii=False)

# @bbs_index.route('/post/<ObjectId:post_id>/')
# @bbs_index.route('/post/<ObjectId:post_id>/page/<int:pn>/')
# def post_detail(post_id, pn=1):
#     '''帖子详情页的视图函数'''
#     post = mongo.db.posts.find_one_or_404({'_id': post_id})
#     # 当有人访问时，帖子浏览量 + 1
#     if post:
#         post['view_count'] = post.get('view_count', 0) + 1
#         mongo.db.posts.save(post)
#     post['user'] = find_one('users', {'_id': post['user_id']}) or {}
#     # 获取评论
#     page = get_page('comments', pn=pn, size=10,
#             filter1={'post_id': post_id}, sort_by=('is_adopted', -1))
#     return render_template('jie/detail.html', post=post, 
#             page_name='jie', comment_page=page, topic_id=post['topic_id'])

# @bbs_index.route('/comment/<ObjectId:comment_id>/')
# def jump_comment(comment_id):
#     comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
#     post_id = comment['post_id']
#     pn = 1
#     if not comment.get('is_adopted', False):
#         comment_index = mongo.db.comments.count({'post_id': post_id,
#                 '_id': {'$lt': comment_id}})
#         pn = comment_index / 10
#         if pn == 0 or pn % 10 != 0:
#             pn += 1
#     return redirect(url_for('bbs_index.post_detail', post_id=post_id, pn=pn
#             ) + '#item-' + str(comment_id))

# @bbs_index.route('/')
# @bbs_index.route('/page/<int:pn>/size/<int:size>')#用来显示指定页数和回答数的页面
# @bbs_index.route('/page/<int:pn>')#只传入了 pn 参数指定页数
# def index(pn=1, size=10):
#     sort_key = request.values.get('sort_key', '_id')
#     # 排序字段和升降序，DESCENDING 的值是 -1 ，表示降序
#     sort_by = (sort_key, DESCENDING)#元组，分别是排序字段和升降序的标志
#     post_type = request.values.get('type')
#     filter1 = {}
#     # 问答状态分类：not_closed 未结/已结；is_cream 精华帖
#     if post_type == 'not_closed':
#         filter1['is_closed'] = {'$ne': True}
#     if post_type == 'is_closed':
#         filter1['is_closed'] = True
#     if post_type == 'is_cream':
#         filter1['is_cream'] = True
#     page = get_page('posts', pn=pn, filter1=filter1, size=size, sort_by=sort_by)
#     return render_template("post_list.html", 
#             page=page, sort_key=sort_key, post_type=post_type)


# def get_page(collection_name, pn=1, size=10, sort_by=None, filter1=None):
#     _process_filter(filter1)
#     size = size if size > 0 else 10     # 每页展示数量
#     total = mongo.db[collection_name].count(filter1)    # 符合要求的数据的数量
#     skip_count = size * (pn - 1)        # 略过的数据的数量
#     result = []
#     has_more = total > pn * size        # 布尔值，是否有更多数据待展示
#     if total - skip_count > 0:
#         # 查找数据
#         result = mongo.db[collection_name].find(filter1, limit=size)
#         # 排列数据
#         if sort_by:
#             result = result.sort(sort_by[0], sort_by[1])
#         # 略过数据
#         if skip_count > 0:
#             result.skip(skip_count)
#     # 计算总页数
#     page_count = total // size
#     if total % size > 0:
#         page_count += 1
#     page = Page(pn, size, sort_by, filter1, list(result), has_more,
#             page_count, total)
#     return page

# @android.route('/post/delete/<ObjectId:post_id>', methods=['POST'])
# @login_required
# def post_delete(post_id):
#     '''删帖视图函数'''
#     post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})
#     # 只有帖子的发布者和管理员可以删除帖子
#     if post['user_id'] != current_user.user['_id'] and \
#             not current_user.user['is_admin']:
#         return jsonify(code_msg.USER_UN_HAD_PERMISSION)
#     # 删除帖子
#     mongo.db.posts.delete_one({'_id': post_id})
#     # 删除帖子其他用户收藏夹中的 post_id
#     mongo.db.users.update_many({}, {'$pull': {'collections': post_id}})
#     # 删除检索索引
#     # whoosh_searcher.delete_document('posts', 'obj_id', str(post_id))
#     return jsonify(
#         code_msg.DELETE_SUCCESS.put(
#             'action', url_for('bbs_index.index')))


# @android.route('/post/set/<ObjectId:post_id>/<string:field>/<int:val>',
#                 methods=['POST'])
# @login_required
# def post_set(post_id, field, val):
#     '''设定帖子状态'''
#     post = mongo.db.posts.find_one_or_404({'_id': post_id})
#     topic = mongo.db.topics.find_one_or_404({'_id': post['topic_id']})
#     if field != 'is_closed':
#         if not current_user.user['is_admin'] and \
#                 current_user.user['_id'] != topic['moderator_id']:
#             return jsonify(code_msg.USER_UN_HAD_PERMISSION)
#     elif current_user.user['_id'] != post['user_id'] \
#             and not current_user.user['is_admin'] \
#             and current_user.user['_id'] != topic['moderator_id']:
#         return jsonify(code_msg.USER_UN_HAD_PERMISSION)
#     val = val == 1
#     # 更新帖子状态
#     mongo.db.posts.update_one({'_id': post_id}, {'$set': {field: val}})
#     return jsonify(models.R.ok())


# def add_message(user, content):
#     # 用户不能自己给自己发消息
#     if user and user['_id'] != current_user.user['_id']:
#         # user['unread'] = user.get('unread', 0) + 1
#         message = {
#             'user_id': user['_id'],
#             'content': content,
#             'create_at': datetime.utcnow()
#         }
#         mongo.db.messages.insert_one(message)
#         mongo.db.users.update({'_id': user['_id']}, {'$inc': {'unread': 1}})


# @android.route('/reply', methods=['POST'])
# @login_required
# def post_reply():
#     # 从请求参数中得到帖子的 id
#     post_id = request.values.get('id')
#     if not post_id:
#         abort(404)
#     # 将帖子 id 转换为 ObjectId 类型
#     post_id = ObjectId(post_id)
#     # 通过帖子 id 查询到对应数据库帖子对象
#     post = mongo.db.posts.find_one_or_404({'_id': post_id})
#     user = current_user.user
#     content = request.values.get('content')
#     if not user.get('is_active', False) or user.get('is_disabled', False):
#         return jsonify(code_msg.USER_UN_ACTIVE_OR_DISABLED)
#     if not content:
#         return jsonify(code_msg.POST_CONTENT_EMPTY)

#     comment = {
#         'content': content,
#         'post_id': post_id,
#         'user_id': user['_id'],
#         'create_at': datetime.utcnow(),
#     }

#     # 保存评论
#     mongo.db.comments.save(comment)
#     mongo.db.users.update_one({'_id': user['_id']},
#                               {'$inc': {
#                                   'reply_count': 1
#                               }})
#     mongo.db.posts.update({'_id': post_id}, {'$inc': {'comment_count': 1}})

#     if post['user_id'] != current_user.user['_id']:
#         # 给发帖人新增一条通知消息
#         user = mongo.db.users.find_one({'_id': post['user_id']})
#         add_message(
#             user,
#             render_template('user_message/reply_message.html',
#                             post=post,
#                             user=current_user.user,
#                             comment=comment))

#     if content.startswith('@'):
#         end = content.index(' ')
#         username = content[1:end]
#         if username != current_user.user['username']:
#             user = mongo.db.users.find_one({'username': username})
#             # 给被@的人新增一条通知消息
#             add_message(
#                 user,
#                 render_template('user_message/reply_message.html',
#                                 post=post,
#                                 user=current_user.user,
#                                 comment=comment))
#     return jsonify(code_msg.COMMENT_SUCCESS)


# @android.route('/adopt/<ObjectId:comment_id>', methods=['POST'])
# @login_required
# def post_adopt(comment_id):
#     if not comment_id:
#         abort(404)
#     # 通过 comment_id 查询到相应评论读对象
#     comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
#     post = mongo.db.posts.find_one_or_404({'_id': comment['post_id']})
#     if post['user_id'] != current_user.user['_id']:
#         return jsonify(code_msg.USER_UN_HAD_PERMISSION)
#     if post.get('accepted', False):
#         return jsonify(code_msg.HAD_ACCEPTED_ANSWER)
#     # 将被采纳评论的 'is_adopted' 标记为 True
#     mongo.db.comments.update_one({'_id': comment_id},
#                                  {'$set': {
#                                      'is_adopted': True
#                                  }})
#     # 帖子变成已接受答案状态
#     post['accepted'] = True
#     # 保存帖子的改动
#     mongo.db.posts.save(post)
#     # 只有悬赏硬币不为0的时候，才将硬币加给被采纳的回帖人
#     reward = post.get('reward', 0)
#     user = mongo.db.users.find_one({'_id': comment['user_id']})
#     if reward > 0 and user:
#         mongo.db.users.update_one({'_id': comment['user_id']},
#                                   {'$inc': {
#                                       'coin': reward
#                                   }})
#     # 给回帖人添加一条通知消息
#     if user:
#         add_message(
#             user,
#             render_template('user_message/adopt_message.html',
#                             post=post,
#                             comment=comment))
#     return jsonify(models.R.ok())


# @android.route('/reply/delete/<ObjectId:comment_id>', methods=['POST'])
# @login_required
# def reply_delete(comment_id):
#     if not current_user.user['is_admin']:
#         return jsonify(code_msg.USER_UN_HAD_PERMISSION)
#     comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
#     post_id = comment['post_id']
#     # 更新回答数减 1
#     update_action = {'$inc': {'comment_count': -1}}
#     if comment.get('is_adopted', False):
#         # 如果删除的是采纳的评论，恢复其他评论可采纳
#         update_action['$set'] = {'accepted': False}
#     # 更新帖子回帖数和恢复其他评论可采纳
#     mongo.db.posts.update_one({'_id': post_id}, update_action)
#     # 删除这条回答
#     mongo.db.comments.delete_one({'_id': comment_id})
#     return jsonify(code_msg.DELETE_SUCCESS)


# @android.route('/reply/zan/<ObjectId:comment_id>', methods=['POST'])
# @login_required
# def reply_zan(comment_id):
#     ok = request.values.get('ok')
#     user_id = current_user.user['_id']
#     # 在 'zan' 里查询当前用户的 user_id 是否在里面
#     res = mongo.db.comments.find_one({
#         '_id': comment_id,
#         'zan': {
#             '$elemMatch': {
#                 '$eq': user_id
#             }
#         }
#     })
#     # 默认取消点赞
#     action = '$pull'
#     count = -1
#     if ok == 'false' and not res:
#         # 点赞
#         action = '$push'
#         count = 1
#     # 点赞后更新在 'zan' 里添加点赞用户的 user_id，更新点赞数量 'zan_count'
#     mongo.db.comments.update_one({'_id': comment_id}, {
#         action: {
#             'zan': user_id
#         },
#         '$inc': {
#             'zan_count': count
#         }
#     })
#     return jsonify(models.R().ok())

# @android.route('/reply/putCoin/<ObjectId:comment_id>', methods=['POST'])
# @login_required
# def reply_putCoin(comment_id):
#     ok = request.values.get('ok')
#     tb_user_id = current_user.user['_id']
#     rc_user_id=mongo.db.comments.find_one({'_id':comment_id})['user_id']
#     # 在 'putCoin' 里查询当前用户的 user_id 是否在里面
#     res = mongo.db.comments.find_one({
#         '_id': comment_id,
#         'putCoin': {
#             '$elemMatch': {
#                 '$eq': tb_user_id
#             }
#         }
#     })
#     if ok == 'false' and not res:
#         # 投币
#         action = '$push'
#         # 点赞后更新在 'putCoin' 里添加投币用户的 user_id，更新点赞数量 'coin_count'
#         mongo.db.comments.update_one({'_id': comment_id}, {
#             action: {
#                 'putCoin': tb_user_id
#             },
#             '$inc': {
#                 'coin_count': 2
#             }
#         })
#         # 还要减少投币人的硬币数量
#         mongo.db.users.update_one({'_id': tb_user_id}, {
#             '$inc': {
#                 'coin_count': -2
#             }
#         })
#         mongo.db.users.update_one({'_id': rc_user_id}, {
#             '$inc': {
#                 'coin_count': 2
#             }
#         })
#         remain_coin=mongo.db.users.find_one({'_id':tb_user_id})['coin']
#         return jsonify(models.R().ok().put('msg',"投币成功，剩余硬币数量："+str(remain_coin)+" 个"))
#     return jsonify(models.R().fail().put("msg","投币失败"))


# @android.route('/reply/update/<ObjectId:comment_id>', methods=['POST'])
# @login_required
# def reply_update(comment_id):
#     '''内容更新'''
#     content = request.values.get('content')
#     if not content:
#         return jsonify(code_msg.POST_CONTENT_EMPTY)
#     comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
#     if current_user.user['_id'] != comment['user_id']:
#         abort(403)
#     mongo.db.comments.update_one({'_id': comment_id},
#                                  {'$set': {
#                                      'content': content
#                                  }})
#     return jsonify(models.R.ok())


# @android.route('/reply/content/<ObjectId:comment_id>',
#                 methods=['POST', 'GET'])
# @login_required
# def get_reply_content(comment_id):
#     '''内容获取'''
#     comment = mongo.db.comments.find_one_or_404({'_id': ObjectId(comment_id)})
#     return jsonify(models.R.ok(data=comment['content']))


# @android.route('/upload/<string:name>')
# @android.route('/upload', methods=['POST'])
# def upload(name=None):
#     if request.method == 'POST':
#         if not current_user.is_authenticated:
#             return jsonify(code_msg.USER_UN_LOGIN)
#         # ‘smfile’ 对应的值就是我们上传的文件
#         file = request.files['smfile']
#         if not file:
#             return jsonify(code_msg.FILE_EMPTY)
#         try:
#             filename = upload_photos.save(file)
#         except UploadNotAllowed:
#             return jsonify(code_msg.UPLOAD_UN_ALLOWED)
#         # 因为存储在帖子内容里，所以用个相对路径，方便数据转移
#         file_url = '/api/upload/' + filename
#         result = models.R(data={'url': file_url}).put('code', 0)
#         return jsonify(result)
#     # 访问上传文件时
#     if not name:
#         abort(404)
#     return redirect(upload_photos.url(name))

# @android.route('/sign', methods=['POST'])
# @login_required
# def user_sign():
#     '''用户签到功能'''
#     date = datetime.utcnow().strftime('%Y-%m-%d')
#     user = current_user.user
#     doc = {
#         'user_id': user['_id'],
#         'date': date
#     }
#     # 如果用户今天已经签过到，返回相关信息
#     sign_log = mongo.db['user_signs'].find_one(doc)
#     if sign_log:
#         return jsonify(code_msg.REPEAT_SIGNED)
#     # 随机奖励
#     interval = db_utils.get_option('sign_interval',
#             {'val': '1-100'})['val'].split('-')
#     coin = random.randint(int(interval[0]), int(interval[1]))
#     doc['coin'] = coin
#     # print(coin)
#     # 插入签到记录
#     mongo.db['user_signs'].insert_one(doc)
#     # 更新硬币数量
#     mongo.db.users.update({'_id': user['_id']}, {"$inc": {'coin': coin}})
#     return jsonify(models.R.ok(data={'signed': True, 'coin': coin}))

# @android.route('/sign/status', methods=['POST'])
# @login_required
# def sign_status():
#     user = current_user.user
#     # 查询数据库中用户今天是否已经记录过签到信息
#     sign_log = mongo.db['user_signs'].find_one({'user_id': user['_id'], 'date': datetime.utcnow().strftime('%Y-%m-%d')})
#     signed = False
#     coin = 0
#     if sign_log:
#         signed = True
#         coin = sign_log.get('coin', 0)
#     return jsonify(models.R.ok(data={'signed': signed, 'coin': coin}))
