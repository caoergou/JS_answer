import os
from flask_uploads import ALL


class DevConfig:
    '''开发环境配置'''
    # 数据库链接相关配置
    MONGO_URI = 'mongodb://localhost:27017/getAnswer'

    # 这里使用环境变量 SECRET_KEY 来设置该字段的值以策安全
    # 在启动应用前，需要先设置环境变量，否则使用第二个参数作为缺省值
    SECRET_KEY = os.environ.get('SECRET_KEY', 'caoergou')

    # 配置 CSRF 认证
    WTF_CSRF_ENABLED = False

    # 配置是否允许注册
    Open_Registration = True

    # 文件上传相关配置
    # 配置允许的扩展名
    UPLOADED_PHOTOS_ALLOW = ALL
    # 配置上传照片的目录
    UPLOADED_PHOTOS_DEST = os.path.join(os.getcwd(), 'uploads/pics')
    # 配置上传文件的目录
    UPLOADED_FILES_DEST = os.path.join(os.getcwd(), 'uploads/files')

    # 配置 WHOOSH 搜索的索引存储目录
    WHOOSH_PATH = os.path.join(os.getcwd(), 'whoosh_indexes')


    # 邮箱相关配置
    # SERVER 和 PORT 是需要网上查的，各家的邮箱都不同
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'userverification@getanswer.xyz' #os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD =  'Hth5ADmrxG8pYNyP' #os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[汲识问答]-'
    MAIL_DEBUG = True
    MAIL_USE_SSL = True
    # 邮箱相关配置说明
    # MAIL_SERVER 配置了使用邮箱的服务器。
    # MAIL_PORT 配置了邮箱服务的端口。
    # MAIL_USE_TLS 和 MAIL_USE_SSL 配置是否支持 TLS 和 SSL 协议。
    # MAIL_USERNAME 配置了发送者的邮箱。MAIL_PASSWORD 填写的不是邮箱的登录密码，而是 SMTP 服务的授权码。
    # MAIL_DEBUG = True 是打开调试模式，方便我们接收到关于 Flask Mail 扩展使用的错误信息。
    # MAIL_SUBJECT_PREFIX 定义发送邮件的标题前缀。
    # MAIL_PASSWORD 授权码（关于 MAIL_PASSWORD 授权码怎么获取，可以在网上查到相关资料）


class ProConfig(DevConfig):
    '''生产环境配置'''


configs = {"FLASK_ENV": "development",
 'Dev': DevConfig, 
 'Pro': ProConfig
 }
