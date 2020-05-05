from flask import (Blueprint, render_template, flash, current_app, jsonify,
                   request, url_for, abort, redirect)
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime
from flask_uploads import UploadNotAllowed
from ..extensions import mongo, upload_photos
from .. import code_msg, models,db_utils
import random


api_view = Blueprint("api", __name__, url_prefix="", template_folder="templates")


@api_view.route('/post/delete/<ObjectId:post_id>', methods=['POST'])
@login_required
def post_delete(post_id):
    '''删帖视图函数'''
    post = mongo.db.posts.find_one_or_404({'_id': ObjectId(post_id)})
    # 只有帖子的发布者和管理员可以删除帖子
    if post['user_id'] != current_user.user['_id'] and \
            not current_user.user['is_admin']:
        return jsonify(code_msg.USER_UN_HAD_PERMISSION)
    # 删除帖子
    mongo.db.posts.delete_one({'_id': post_id})
    # 删除帖子其他用户收藏夹中的 post_id
    mongo.db.users.update_many({}, {'$pull': {'collections': post_id}})
    # 删除检索索引
    # whoosh_searcher.delete_document('posts', 'obj_id', str(post_id))
    return jsonify(
        code_msg.DELETE_SUCCESS.put(
            'action', url_for('index.index')))


@api_view.route('/post/set/<ObjectId:post_id>/<string:field>/<int:val>',
                methods=['POST'])
@login_required
def post_set(post_id, field, val):
    '''设定帖子状态'''
    post = mongo.db.posts.find_one_or_404({'_id': post_id})
    catalog = mongo.db.catalogs.find_one_or_404({'_id': post['catalog_id']})
    if field != 'is_closed':
        if not current_user.user['is_admin'] and \
                current_user.user['_id'] != catalog['moderator_id']:
            return jsonify(code_msg.USER_UN_HAD_PERMISSION)
    elif current_user.user['_id'] != post['user_id'] \
            and not current_user.user['is_admin'] \
            and current_user.user['_id'] != catalog['moderator_id']:
        return jsonify(code_msg.USER_UN_HAD_PERMISSION)
    val = val == 1
    # 更新帖子状态
    mongo.db.posts.update_one({'_id': post_id}, {'$set': {field: val}})
    return jsonify(models.R.ok())


def add_message(user, content):
    # 用户不能自己给自己发消息
    if user and user['_id'] != current_user.user['_id']:
        # user['unread'] = user.get('unread', 0) + 1
        message = {
            'user_id': user['_id'],
            'content': content,
            'create_at': datetime.utcnow()
        }
        mongo.db.messages.insert_one(message)
        mongo.db.users.update({'_id': user['_id']}, {'$inc': {'unread': 1}})


@api_view.route('/reply', methods=['POST'])
@login_required
def post_reply():
    # 从请求参数中得到帖子的 id
    post_id = request.values.get('id')
    if not post_id:
        abort(404)
    # 将帖子 id 转换为 ObjectId 类型
    post_id = ObjectId(post_id)
    # 通过帖子 id 查询到对应数据库帖子对象
    post = mongo.db.posts.find_one_or_404({'_id': post_id})
    user = current_user.user
    content = request.values.get('content')
    if not user.get('is_active', False) or user.get('is_disabled', False):
        return jsonify(code_msg.USER_UN_ACTIVE_OR_DISABLED)
    if not content:
        return jsonify(code_msg.POST_CONTENT_EMPTY)

    comment = {
        'content': content,
        'post_id': post_id,
        'user_id': user['_id'],
        'create_at': datetime.utcnow(),
    }

    # 保存评论
    mongo.db.comments.save(comment)
    mongo.db.users.update_one({'_id': user['_id']},
                              {'$inc': {
                                  'reply_count': 1
                              }})
    mongo.db.posts.update({'_id': post_id}, {'$inc': {'comment_count': 1}})

    if post['user_id'] != current_user.user['_id']:
        # 给发帖人新增一条通知消息
        user = mongo.db.users.find_one({'_id': post['user_id']})
        add_message(
            user,
            render_template('user_message/reply_message.html',
                            post=post,
                            user=current_user.user,
                            comment=comment))

    if content.startswith('@'):
        end = content.index(' ')
        username = content[1:end]
        if username != current_user.user['username']:
            user = mongo.db.users.find_one({'username': username})
            # 给被@的人新增一条通知消息
            add_message(
                user,
                render_template('user_message/reply_message.html',
                                post=post,
                                user=current_user.user,
                                comment=comment))
    return jsonify(code_msg.COMMENT_SUCCESS)


@api_view.route('/adopt/<ObjectId:comment_id>', methods=['POST'])
@login_required
def post_adopt(comment_id):
    if not comment_id:
        abort(404)
    # 通过 comment_id 查询到相应评论读对象
    comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
    post = mongo.db.posts.find_one_or_404({'_id': comment['post_id']})
    if post['user_id'] != current_user.user['_id']:
        return jsonify(code_msg.USER_UN_HAD_PERMISSION)
    if post.get('accepted', False):
        return jsonify(code_msg.HAD_ACCEPTED_ANSWER)
    # 将被采纳评论的 'is_adopted' 标记为 True
    mongo.db.comments.update_one({'_id': comment_id},
                                 {'$set': {
                                     'is_adopted': True
                                 }})
    # 帖子变成已接受答案状态
    post['accepted'] = True
    # 保存帖子的改动
    mongo.db.posts.save(post)
    # 只有悬赏金币不为0的时候，才将金币加给被采纳的回帖人
    reward = post.get('reward', 0)
    user = mongo.db.users.find_one({'_id': comment['user_id']})
    if reward > 0 and user:
        mongo.db.users.update_one({'_id': comment['user_id']},
                                  {'$inc': {
                                      'coin': reward
                                  }})
    # 给回帖人添加一条通知消息
    if user:
        add_message(
            user,
            render_template('user_message/adopt_message.html',
                            post=post,
                            comment=comment))
    return jsonify(models.R.ok())


@api_view.route('/reply/delete/<ObjectId:comment_id>', methods=['POST'])
@login_required
def reply_delete(comment_id):
    if not current_user.user['is_admin']:
        return jsonify(code_msg.USER_UN_HAD_PERMISSION)
    comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
    post_id = comment['post_id']
    # 更新回答数减 1
    update_action = {'$inc': {'comment_count': -1}}
    if comment.get('is_adopted', False):
        # 如果删除的是采纳的评论，恢复其他评论可采纳
        update_action['$set'] = {'accepted': False}
    # 更新帖子回帖数和恢复其他评论可采纳
    mongo.db.posts.update_one({'_id': post_id}, update_action)
    # 删除这条回答
    mongo.db.comments.delete_one({'_id': comment_id})
    return jsonify(code_msg.DELETE_SUCCESS)


@api_view.route('/reply/zan/<ObjectId:comment_id>', methods=['POST'])
@login_required
def reply_zan(comment_id):
    ok = request.values.get('ok')
    user_id = current_user.user['_id']
    # 在 'zan' 里查询当前用户的 user_id 是否在里面
    res = mongo.db.comments.find_one({
        '_id': comment_id,
        'zan': {
            '$elemMatch': {
                '$eq': user_id
            }
        }
    })
    # 默认取消点赞
    action = '$pull'
    count = -1
    if ok == 'false' and not res:
        # 点赞
        action = '$push'
        count = 1
    # 点赞后更新在 'zan' 里添加点赞用户的 user_id，更新点赞数量 'zan_count'
    mongo.db.comments.update_one({'_id': comment_id}, {
        action: {
            'zan': user_id
        },
        '$inc': {
            'zan_count': count
        }
    })
    return jsonify(models.R().ok())


@api_view.route('/reply/update/<ObjectId:comment_id>', methods=['POST'])
@login_required
def reply_update(comment_id):
    '''内容更新'''
    content = request.values.get('content')
    if not content:
        return jsonify(code_msg.POST_CONTENT_EMPTY)
    comment = mongo.db.comments.find_one_or_404({'_id': comment_id})
    if current_user.user['_id'] != comment['user_id']:
        abort(403)
    mongo.db.comments.update_one({'_id': comment_id},
                                 {'$set': {
                                     'content': content
                                 }})
    return jsonify(models.R.ok())


@api_view.route('/reply/content/<ObjectId:comment_id>',
                methods=['POST', 'GET'])
@login_required
def get_reply_content(comment_id):
    '''内容获取'''
    comment = mongo.db.comments.find_one_or_404({'_id': ObjectId(comment_id)})
    return jsonify(models.R.ok(data=comment['content']))


@api_view.route('/upload/<string:name>')
@api_view.route('/upload', methods=['POST'])
def upload(name=None):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify(code_msg.USER_UN_LOGIN)
        # ‘smfile’ 对应的值就是我们上传的文件
        file = request.files['smfile']
        if not file:
            return jsonify(code_msg.FILE_EMPTY)
        try:
            filename = upload_photos.save(file)
        except UploadNotAllowed:
            return jsonify(code_msg.UPLOAD_UN_ALLOWED)
        # 因为存储在帖子内容里，所以用个相对路径，方便数据转移
        file_url = '/api/upload/' + filename
        result = models.R(data={'url': file_url}).put('code', 0)
        return jsonify(result)
    # 访问上传文件时
    if not name:
        abort(404)
    return redirect(upload_photos.url(name))

@api_view.route('/sign', methods=['POST'])
@login_required
def user_sign():
    '''用户签到功能'''
    date = datetime.utcnow().strftime('%Y-%m-%d')
    user = current_user.user
    doc = {
        'user_id': user['_id'],
        'date': date
    }
    # 如果用户今天已经签过到，返回相关信息
    sign_log = mongo.db['user_signs'].find_one(doc)
    if sign_log:
        return jsonify(code_msg.REPEAT_SIGNED)
    # 随机奖励
    interval = db_utils.get_option('sign_interval',
            {'val': '1-100'})['val'].split('-')
    coin = random.randint(int(interval[0]), int(interval[1]))
    doc['coin'] = coin
    # print(coin)
    # 插入签到记录
    mongo.db['user_signs'].insert_one(doc)
    # 更新金币数量
    mongo.db.users.update({'_id': user['_id']}, {"$inc": {'coin': coin}})
    return jsonify(models.R.ok(data={'signed': True, 'coin': coin}))

@api_view.route('/sign/status', methods=['POST'])
@login_required
def sign_status():
    user = current_user.user
    # 查询数据库中用户今天是否已经记录过签到信息
    sign_log = mongo.db['user_signs'].find_one({'user_id': user['_id'], 'date': datetime.utcnow().strftime('%Y-%m-%d')})
    signed = False
    coin = 0
    if sign_log:
        signed = True
        coin = sign_log.get('coin', 0)
    return jsonify(models.R.ok(data={'signed': signed, 'coin': coin}))