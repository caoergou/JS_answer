from wtforms import form, fields
from flask_admin.contrib.pymongo import ModelView, filters
from flask_login import current_user
from wtforms.validators import DataRequired, Email, EqualTo,Length
from flask_admin.form import upload
from flask import redirect, url_for, request
from os import path as op
from bson.objectid import ObjectId


class BaseModelView(ModelView):
    permission_name = ''

    # 验证是否为管理员权限
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user['is_admin']

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('user.login', next=request.url))

class OptionsForm(form.Form):
    name = fields.StringField('名称')
    code = fields.StringField('代码', )
    val = fields.StringField('值')
    form_columns = ('name', 'code', 'val')


class OptionsModelView(ModelView):
    column_list = ('name', 'code', 'val')
    column_labels = dict(name='名称', code='代码', val='值')
    column_sortable_list = 'name'
    column_default_sort = ('name', False)
    can_create = True
    can_delete = True
    can_edit = True
    form = OptionsForm



class FriendLinksForm(form.Form):
    name = fields.StringField('网站名称')
    url = fields.StringField('网站链接')
    sort = fields.IntegerField('排序', default=0)
    form_columns = ('name', 'url')


class FriendLinksModelView(BaseModelView):
    column_list = ('url', 'name', 'sort')
    column_labels = dict(name='网站名称', url='网站链接', sort='排序')
    column_sortable_list = 'name'
    column_default_sort = ('name', False)
    can_create = True
    can_delete = True
    can_edit = True
    form = FriendLinksForm

 
class PassagewaysForm(form.Form):
    name = fields.StringField('名称')
    url = fields.StringField('链接')
    sort = fields.IntegerField('排序', default=0)
    form_columns = ('name', 'url')


class PassagewaysModelView(BaseModelView):
    column_list = ('name', 'url', 'sort')
    column_labels = dict(name='名称', url='链接', sort='排序')
    column_sortable_list = 'name'
    column_default_sort = ('name', False)
    can_create = True
    can_delete = True
    can_edit = True
    form = PassagewaysForm


class AdsForm(form.Form):
    name = fields.StringField('名称')
    url = fields.StringField('链接')
    color = fields.StringField('颜色', default='#5FB878')
    sort = fields.IntegerField('排序', default=0)
    form_columns = ('name', 'url')


class AdsModelView(BaseModelView):
    column_list = ('name', 'url', 'color', 'sort')
    column_labels = dict(name='名称', url='链接', color='颜色', sort='排序')
    column_sortable_list = 'name'
    column_default_sort = ('name', False)
    can_create = True
    can_delete = True
    can_edit = True
    form = AdsForm


class FooterLinksForm(form.Form):
    name = fields.StringField('名称')
    url = fields.StringField('链接')
    sort = fields.IntegerField('排序', default=0)
    form_columns = ('name', 'url')


class FooterLinksModelView(BaseModelView):
    column_list = ('name', 'url', 'sort')
    column_labels = dict(name='名称', url='链接', sort='排序')
    column_sortable_list = 'name'
    column_default_sort = ('name', False)
    can_create = True
    can_delete = True
    can_edit = True
    form = FooterLinksForm


class PagesForm(form.Form):
    name = fields.StringField('名称')
    url = fields.StringField('链接')
    sort = fields.IntegerField('排序', default=0)
    icon_code = fields.StringField(
            '图标代码（http://www.layui.com/doc/element/icon.html）')
    form_columns = ('name', 'url', 'icon_code')


class PagesModelView(BaseModelView):
    column_list = ( 'name', 'url', 'icon_code', 'sort')
    column_labels = dict(name='名称', url='链接', icon_code='图标代码', 
            sort='排序')
    column_sortable_list = 'name'
    column_default_sort = ('name', False)
    can_create = True
    can_delete = True
    can_edit = True
    form = PagesForm


# 帖子种类管理
class TopicsForm(form.Form):
    name = fields.StringField('栏目名称')
    sort_key = fields.IntegerField('排序', default=0)
    form_columns = ('name', 'sort_key')


class TopicsModelView(BaseModelView):
    column_list = ('name','topic_admin', 'sort_key')
    column_labels = dict(name='话题名称',topic_admin='管理员', sort_key='排序')
    can_create = True
    can_delete = True
    can_edit = True
    form = TopicsForm

    def after_model_delete(self, model):
        from ..extensions import mongo
        topic_id = ObjectId(model['_id'])
        post_ids = [post['_id'] for post in mongo.db.posts.find(
                {'topic_id': topic_id}, {'_id': 1})]
        mongo.db.users.update_many({}, {'$pull': {'collections': 
                {'$in': post_ids}}})
        mongo.db.posts.delete_many({'topic_id': topic_id})


# 用户表
class UsersForm(form.Form):
    email = fields.StringField('用户邮箱', validators=[
            DataRequired('邮箱不能为空'), Email('邮箱格式不正确')])
    username = fields.StringField('昵称', validators=[
            DataRequired('昵称不能为空')])
    is_active = fields.BooleanField('激活状态')
    is_disabled = fields.BooleanField('禁用')
    is_admin = fields.BooleanField('管理员')
    vip = fields.IntegerField('VIP等级')
    avatar = fields.StringField('头像')
    coin = fields.IntegerField('硬币')
    description = fields.TextAreaField('签名')
    city = fields.StringField('城市')
    renzheng = fields.StringField('认证信息')
    form_columns = ('email', 'username', 'is_active', 'is_admin', 
            'avatar', 'coin', 'description', 'city')


class UsersModelView(BaseModelView):
    column_list = ('email','username', 'is_active', 'is_disabled', 'is_admin', 
            'vip', 'avatar', 'coin', 'description', 'city', 'renzheng')
    column_labels = dict(email='用户邮箱', username='昵称', 
            is_active='激活状态', vip='VIP等级', is_disabled='禁用', 
            is_admin='管理员', avatar='头像', coin='硬币', 
            description='签名', city='城市', renzheng='认证信息')
    can_create = True
    can_delete = True
    can_edit = True
    form = UsersForm


# 帖子表管理
class PostsForm(form.Form):
    title = fields.StringField('标题', validators=[DataRequired('标题不能为空')])
    reward = fields.IntegerField('悬赏')
    comment_count = fields.IntegerField('回帖数')
    is_top = fields.BooleanField('置顶')
    is_cream = fields.BooleanField('加精')
    is_closed = fields.BooleanField('已结')
    form_columns = ('title','reward','comment_count', 'is_top','is_cream', 
            'is_closed')


class PostsModelView(BaseModelView):
    column_list = ('title','comment_count', 'view_count', 'is_top', 
            'is_cream', 'is_closed', 'create_at', 'modify_at', 'reward')
    column_labels = dict(title='标题', comment_count='回帖数', 
            view_count='查看数', is_top='置顶', is_cream='加精', 
            is_closed='已结', create_at='创建日期', modify_at='最后编辑日期', 
            reward='悬赏')
    can_create = False
    can_delete = True
    can_edit = False
    form = PostsForm
    def after_model_delete(self, model):
        from ..extensions import mongo
        post_id = ObjectId(model['_id'])
        mongo.db.users.update_many({}, {'$pull': {'collections': post_id}})
        mongo.db.comments.deleteMany({'post_id':post_id})
