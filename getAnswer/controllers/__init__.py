from .user_view import user_view
from .bbs_index import bbs_index

bp_list = [user_view,bbs_index]

def config_blueprints(app):
    for bp in bp_list:
        app.register_blueprint(bp)