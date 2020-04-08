from getAnswer import create_app
from flask_script import Manager
import os

config_name = os.environ.get('FLASK_CONFIG') or 'Dev'

app = create_app(config_name)
# 把 app 传给 Manager 对象
manager = Manager(app)

if __name__ == '__main__':
    manager.run()