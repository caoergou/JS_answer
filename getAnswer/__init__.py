

from flask import Flask

from .configs import configs
from .controllers import config_blueprint
from .install_init import init as install_init
from .extensions import init_extensions
from flask_wtf.csrf import CSRFProtect
from .custom_functions import init_func  # 新增代码
from getAnswer import flask_objectid_converter

def create_app(config):
    app = Flask(__name__)
    app.jinja_env.auto_reload = True
    app.config['SECRET_KEY'] = 'ergou'
    app.config['JSON_AS_ASCII'] = False
    app.url_map.converters['ObjectId'] = flask_objectid_converter.ObjectIDConverter
    app.config.from_object(configs.get(config))
    csrf=CSRFProtect(app)  #调用csrf保护web程序
    init_extensions(app)
    config_blueprint(app)
    init_func(app)    
    with app.app_context():
        install_init()
    flask_objectid_converter.Base64ObjectIDConverter
    return app