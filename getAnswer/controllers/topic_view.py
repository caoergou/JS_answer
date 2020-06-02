import json


from flask import Blueprint, render_template, jsonify, url_for, request,redirect
from flask_login import current_user, login_required
from bson import ObjectId
from datetime import datetime
from pymongo import DESCENDING


from .. import utils, db_utils, code_msg
from ..forms import PostForm,TopicForm
from ..models import R, BaseResult
from ..utils import gen_verify_num, verify_num
from ..extensions import mongo,whoosh_searcher
from ..db_utils import get_page, find_one
from getAnswer.models import Page


from random import randint
from flask import (Blueprint, render_template, request, jsonify, url_for, 
        session, redirect)
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import mongo

from ..models import User
from getAnswer.models import BaseResult

# 创建蓝图，第一个参数为自定义，供前端使用，第二个参数为固定写法
# 第三个参数为 URL 前缀
topic_view = Blueprint("topic", __name__,  template_folder="templates")

@topic_view.route('/')
@topic_view.route("/<ObjectId:topic_id>")#传入了 topic_id 参数用来指定话题
@topic_view.route("/<ObjectId:topic_id>/page/<int:pn>")
@topic_view.route("/<ObjectId:topic_id>/page/<int:pn>/size/<int:size>")#在指定类别的基础上再进行分页和指定页面帖子数量。
def index(pn=1, size=10, topic_id=None):
    sort_key = request.values.get('sort_key', '_id')
    # 排序字段和升降序，DESCENDING 的值是 -1 ，表示降序
    sort_by = (sort_key, DESCENDING)#元组，分别是排序字段和升降序的标志
    post_type = request.values.get('type')
    # user=current_user.user
    filter1 = {}
    # 问答状态分类：not_closed 未结/已结；is_cream 精华帖
    if post_type == 'not_closed':
        filter1['is_closed'] = {'$ne': True}
    if post_type == 'is_closed':
        filter1['is_closed'] = True
    if post_type == 'is_cream':
        filter1['is_cream'] = True
    # 增加问答类型
    if topic_id:
        filter1['topic_id'] = topic_id
        # post = mongo.db.posts.find_one_or_404({'_id': post_id})
        page = get_page('posts', pn=pn, filter1=filter1, size=size, sort_by=sort_by)
        return render_template("/topic/topic_detail.html", is_index=topic_id is None,
            page=page, sort_key=sort_key, topic_id=topic_id,
            post_type=post_type)
    else:
        return render_template("/topic/topic_square.html",is_index=True)


@topic_view.route('/add/', methods=['GET', 'POST'])
@topic_view.route('/edit/<ObjectId:topic_id>/', methods=['GET', 'POST'])
@login_required
def add_topic(topic_id=None):
    form = TopicForm()
    # 如果表单已提交
    if form.is_submitted():
        # 如果没通过表单类中的验证
        if not form.validate():
            # 这里调用 BaseResult 类的实例作为 jsonify 的参数
            return jsonify(BaseResult(1, str(form.errors)))
        # 对于人类操作的验证
        verify_num(form.vercode.data)
        # current_user 就是 models.py 文件里的 User 类的实例
        # current_user.user 就是对应到 MongoDB 数据集合中的一条用户数据
        user = current_user.user
        # 如果这个字段没有被赋值为 True ，说明用户还未激活
        # 后面的实验会使用邮箱验证来激活用户
        if not user.get('is_active'):
            return jsonify(code_msg.USER_UN_ACTIVE_OR_DISABLED)
        if not user.get('is_admin'):
            return jsonify(code_msg.USER_UN_HAD_PERMISSION)
        if form.parent_id.data :
            parent_id = ObjectId(form.parent_id.data)
        else:
            parent_id = '#'
        # 一个话题
        topic = {'name': form.title.data,
                    'description':form.description.data,
                'parent_id':parent_id,
                'topic_admin':form.topic_admin.data,
        }
        # 如果有这个参数，说明该话题已经存在，现在是修改话题的操作
        if topic_id:
            # 增加一个“修改时间” 字段
            topic['modified_at'] = datetime.utcnow()
            # 更新帖子数据
            mongo.db.topics.update_one({'_id': topic_id}, {'$set': topic})
            return jsonify(code_msg.ALTER_topic_SUCCESS.put('action', url_for('.index',topic_id=topic_id)))
        # 否则，就是新建帖子的操作
        else:
            topic['created_at'] = datetime.utcnow()
            # 将新建话题的数据添加到数据库
            mongo.db.topics.insert_one(topic)
            post_id = topic['_id']
            # 这里将 action 字段添加到字典中，以便传入 JS 代码中触发跳转
            return jsonify(code_msg.ADD_topic_SUCCESS.put('action', url_for('.index',topic_id=topic_id)))
    # 如果是使用 GET 方法发送的请求
    ver_code = gen_verify_num()
    topic = None
    title = '创建话题'
    if topic_id:
        topic = mongo.db.topics.find_one_or_404({'_id': topic_id})
        title = '编辑话题'
    return render_template('topic/add.html', page_name='topic', form=form,
            ver_code=ver_code['question'], is_add=(topic_id is None), topic=topic,
            title=title,user=current_user.user)