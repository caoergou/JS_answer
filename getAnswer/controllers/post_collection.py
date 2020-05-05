from flask import (Blueprint, render_template,flash, request, url_for,
        current_app, session, jsonify, abort)
from .. import db_utils, utils, forms, models
from ..extensions import mongo
from flask_login import login_required
from flask_login import current_user
from bson.json_util import dumps


post_collection = Blueprint("collection", __name__)

#帖子收藏
@post_collection.route('/find/<ObjectId:post_id>', methods=['POST'])
@login_required
def collection_find(post_id=None):
    '''判断帖子是否被收藏'''
    collections = current_user.user.get('collections', [])
    is_collected = False
    # 如果 collections 中有当前帖子的 post_id，说明已经收藏
    if collections and post_id in collections:
        is_collected = True
    # 返回 {'collection': True 或 False }
    return jsonify(models.R.ok(data={'collection': is_collected}))



@post_collection.route('/<string:action>/<ObjectId:post_id>', methods=['POST'])
@login_required
def collection(action, post_id):
    '''收藏帖子'''
    update_action = '$pull'
    if action == 'add':
        update_action = '$push'
    mongo.db.users.update_one({'_id': current_user.user['_id']},
            {update_action: {'collections': post_id}})
    return jsonify(models.R.ok())