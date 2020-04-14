from getAnswer import create_app
from flask_script import Manager, Server
import os



config = os.environ.get('FLASK_CONFIG', 'Dev')
# 初始化 app 应用
app = create_app(config)
# 将 app 作为参数创建 Manager 类的实例，该实例可以看作是拥有一些额外功能的 app
manager = Manager(app)  
# 开启 DEBUG 模式
manager.add_command('runserver', Server(use_debugger=True, port=80,threaded=True))

if __name__ == '__main__':
  manager.run()
