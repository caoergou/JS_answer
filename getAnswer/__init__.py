from flask import Flask
from .configs import configs
from .controllers import config_route


def create_app(config_name):
    app = Flask(__name__)
    # from_object 会从传入的对象中读取配置信息
    app.config.from_object(configs[config_name])
    # controllers 中的路由函数
    config_route(app)

    return app