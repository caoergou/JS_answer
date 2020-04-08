from flask_pymongo import PyMongo

# 实例化一个 PyMongo 类
mongo = PyMongo()

def init_extensions(app):
    # 调用 PyMongo 类的 init_app 方法进行初始化
    mongo.init_app(app)