from .db_utils import get_option,get_list

def init_func(app):
    app.add_template_global(get_option, 'get_option')
    app.add_template_global(get_list, 'get_list')
