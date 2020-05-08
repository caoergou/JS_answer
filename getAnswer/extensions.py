from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from flask_admin import Admin
from flask_mail import Mail
from bson import ObjectId
from jieba.analyse import ChineseAnalyzer
# Whoosh相关
from .plugins import WhooshSearcher
from whoosh.fields import Schema, TEXT, ID, DATETIME
from jieba.analyse import ChineseAnalyzer
from flask_cache import Cache
import functools

from .models import User
from .admin import admin_view
from .plugins import WhooshSearcher


# 实例化一个 PyMongo 类
mongo = PyMongo()

# Cache
cache = Cache()

# 创建 LoginManager 类的实例
login_manager = LoginManager()
# 定义处理登录页的路由函数
# 如果用户未登录时访问了需要登录才能访问的页面
# 会自动跳转到此处提供的视图函数所指向的页面
login_manager.login_view = 'user_view.login'


# 创建一个 Mail 类，实现邮箱的管理
mail = Mail()


# 创建 WhooshSearcher 的实例类
whoosh_searcher = WhooshSearcher()


# 实例化图片上传对象，extensions 参数代表允许扩展名
upload_photos = UploadSet(extensions=ALL)
# photos = UploadSet('photos', IMAGES)

# 实例化一个 Amdin 类，用于系统的后台管理
admin = Admin(name='汲识问答 后台管理系统')

# 示例化一个 Mail 类，用于邮箱激活与密码服务
mail = Mail()


# 使用该装饰器的作用是将 user_load 方法
# 设置为 login_manager 的 user_callback 属性
# 以便能够在需要的时候使用 user_id 参数找到对应的用户数据
@login_manager.user_loader
def user_load(user_id):
    # 如果 user_id 存在，find_one 方法返回字典对象
    # 否则返回 None
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    return User(user)

def init_extensions(app):
    # 调用 PyMongo 类的 init_app 方法进行初始化
    mongo.init_app(app)
    
    # 调用 init_app 方法注册 app
    # 此方法的主要作用就是将 login_manager 本身赋值给 app.login_manager 属性
    # 以便 app 能够使用其登录登出等功能
    login_manager.init_app(app)

	# # 使用 cache 可以加快web程序运行速度，即 采用缓存的方法以空间换时间
    # if app.config.get('USE_CACHE', False):
    #     cache.init_app(app, {})
    
	# 获取配置信息并存储在 app 上
    configure_uploads(app, upload_photos)
    
    # 获取邮箱的配置
    mail.init_app(app)

    # 获取搜索服务的配置
    whoosh_searcher.init_app(app)
    # 使用 jieba 中文分词
    chinese_analyzer = ChineseAnalyzer()
	# 建立索引模式对象
    post_schema = Schema(obj_id=ID(unique=True, stored=True),
			title=TEXT(stored=True, analyzer=chinese_analyzer),
			content=TEXT(stored=True, analyzer=chinese_analyzer),
			create_at=DATETIME(stored=True), topic_id=ID(stored=True),
			user_id=ID(stored=True))
    whoosh_searcher.add_index('posts', post_schema)

    # 获取后台管理界面的相关配置
    admin.init_app(app)
    with app.app_context():
        admin.add_view(admin_view.OptionsModelView(mongo.db['options'], 
                '系统设置'))
        admin.add_view(admin_view.UsersModelView(mongo.db['users'], '用户管理'))
        admin.add_view(admin_view.TopicsModelView(mongo.db['topics'], 
                '栏目管理', category='内容管理'))
        admin.add_view(admin_view.PostsModelView(mongo.db['posts'], 
                '帖子管理', category='内容管理'))
        admin.add_view(admin_view.PassagewaysModelView(mongo.db['passageways'], 
                '温馨通道', category='推广管理'))
        admin.add_view(admin_view.FriendLinksModelView(mongo.db['friend_links'], 
                '友链管理', category='推广管理'))
        admin.add_view(admin_view.PagesModelView(mongo.db['pages'], '页面管理', 
                category='推广管理'))
        admin.add_view(admin_view.FooterLinksModelView(mongo.db['footer_links'], 
                '底部链接', category='推广管理'))
        admin.add_view(admin_view.AdsModelView(mongo.db['ads'], '广告管理', 
                category='推广管理'))


def clear_cache(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        cache.clear()
        return f(*args, **kwargs)
    return decorator
