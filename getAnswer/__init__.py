# from flask import Flask
# from getAnswer.configs import configs
# from getAnswer.controllers import config_route
# # 导入 init 函数作为 install_init
# from getAnswer.install_init import init as install_init
# from getAnswer.extensions import init_extensions

# def create_app(config_name):
#     app = Flask(__name__)
#     app.config.from_object(configs[config_name])  # 更新配置项
#     init_extensions(app)  # 初始化扩展，连接数据库
#     config_route(app)     # 将已经创建的视图函数注册到应用上
#     app.app_context().push()  # 推送应用上下文环境
#     install_init()        # 执行向数据库添加数据的函数
#     return app

from flask import Flask

from .configs import configs
from .controllers import config_blueprints
from .install_init import init as install_init
from .extensions import init_extensions
from flask_wtf.csrf import CSRFProtect
from .custom_functions import init_func  # 新增代码
from getAnswer import flask_objectid_converter

def create_app(config):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'PyFLy123'
    app.url_map.converters['ObjectId'] = flask_objectid_converter.ObjectIDConverter
    app.config.from_object(configs.get(config))
    csrf=CSRFProtect(app)  #调用csrf保护web程序
    init_extensions(app)
    config_blueprints(app)
    init_func(app)    
    with app.app_context():
        install_init()
    flask_objectid_converter.Base64ObjectIDConverter

    return app