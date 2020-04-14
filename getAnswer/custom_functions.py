from .db_utils import get_option

def init_func(app):
    app.add_template_global(get_option, 'get_option')