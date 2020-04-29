from .user_view import user_view
from .bbs_index import bbs_index
from .api_view import api_view
from .post_collection import post_collection

bp_list = [user_view, bbs_index, api_view, post_collection]

def config_blueprints(app):
    for bp in bp_list:
        app.register_blueprint(bp)