import os
from flask_uploads import ALL

class Dev:
    # 省略部分代码

    # 配置允许的扩展名
    UPLOADED_PHOTOS_ALLOW = ALL
    # 配置上传照片的目录
    UPLOADED_PHOTOS_DEST = os.path.join(os.getcwd(), 'uploads')
    # 配置上传文件的目录
    UPLOADED_FILES_DEST = os.path.join(os.getcwd(), 'uploads')

class DevConfig:
    '''开发环境配置'''

    MONGO_URI = 'mongodb://localhost:27017/getAnswer'
    # 这里使用环境变量 SECRET_KEY 来设置该字段的值以策安全
    # 在启动应用前，需要先设置环境变量，否则使用第二个参数作为缺省值
    SECRET_KEY = os.environ.get('SECRET_KEY', 'caoergou')

class ProConfig(DevConfig):
    '''生产环境配置'''

# 只须添加数据库的 URI
class Dev:
    MONGO_URI = "mongodb://127.0.0.1:27017/getAnswer"

configs = {
        "FLASK_ENV":"development",
        'Dev': DevConfig,
        'Pro': ProConfig,
        'Open_Registration': True
}