import json
from bson import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash
from random import randint
from flask import (Blueprint, render_template, request, jsonify, url_for, 
        session, redirect)
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import mongo
from .. import utils, db_utils, code_msg, forms, models
from ..models import User

# 创建蓝图，第一个参数为自定义，供前端使用，第二个参数为固定写法
# 第三个参数为 URL 前缀
topic_view = Blueprint("topic", __name__, url_prefix="", template_folder="templates")



@topic_view.route('/')
def index():
    return render_template("topic/topic_square.html")
