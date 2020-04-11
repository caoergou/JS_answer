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


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))
    init_extensions(app)
    config_blueprints(app)
    app.app_context().push()  # 推送应用上下文环境
    install_init()
    return app