from werkzeug.security import check_password_hash


class User:
    user = None
    is_active = False
    is_authenticated = True
    is_anonymous = False

    def __init__(self, user):
        self.user = user
        self.is_active = user['is_active']

    def get_id(self):
        return str(self.user['_id'])

    # 因为该方法不涉及类本身的属性，所以使用静态方法装饰器装饰它
    @staticmethod
    def validate_login(password_hash, password):
        # 此 check_password_hash 方法接收两个参数
        # 数据库中的哈希密码和用户在页面上填写的密码
        # 如果验证密码一致则返回 True ，否则返回 False
        return check_password_hash(password_hash, password)