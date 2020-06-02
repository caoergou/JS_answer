from .api_view import api_view
from .bbs_index import bbs_index
from .exception_view import exception_view
from .topic_view import topic_view
from .user_view import user_view

# 蓝本默认配置
DEFAULT_BLUEPRINT = (
    # (蓝本，前缀)
    (bbs_index, ''),
    (user_view, '/user'),
    (api_view, '/api'),
    (exception_view, '/error'),
    (topic_view, '/topic'),
)


# 封装函数配置蓝本
def config_blueprint(app):
    for blueprint, url_prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
