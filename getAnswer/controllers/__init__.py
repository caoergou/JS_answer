from .user_view import user_view
from .bbs_index import bbs_index
from .api_view import api_view
from .post_collection import post_collection

# # 蓝本默认配置
# DEFAULT_BLUEPRINT = (
#     # (蓝本，前缀)
#     (bbs_index, ''),
#     (user_view, '/user'),
#     (post_collection, '/collection'),
#     (api_view, '/api'),
#     (exception_view, '/error'),
# )

bp_list = [user_view, bbs_index, api_view, post_collection]

def config_blueprints(app):
    for bp in bp_list:
        app.register_blueprint(bp)