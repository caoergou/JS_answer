from werkzeug.security import check_password_hash
from json import JSONEncoder



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


class R(dict):
    #这个类是状态码类，包含成功和失败返回的状态码、信息、数据
    #该类继承于dict，即字典，是对字典功能进行了改良
    @staticmethod
    def ok(msg=None, data=None):
        r = R()
        r.put('status', 0)
        #成功时，状态码为0
        r.put('msg', msg)
        r.put('data', data)
        return r

    @staticmethod
    def fail(code=404, msg=None):
        r = R()
        r.put('status', code)
        r.put('msg', msg)
        return r

    def put(self, k, v):
        self.__setitem__(k, v)
        return self

    def get_status(self):
        return self.get('status')

    def get_msg(self):
        return self.get('msg')


class BaseResult(R):
    def __init__(self, code=0, msg='', data=None):
        self.put('status', code)
        self.put('msg', msg)
        self.put('data', data)


class Page:
    def __init__(self,
                 pn,
                 size,
                 sort_by=None,
                 filter1=None,
                 result=None,
                 has_more=False,
                 page_count=0,
                 total=0):
        self.pn = pn
        self.size = size
        self.sort_by = sort_by
        self.filter1 = filter1
        self.result = result
        self.has_more = has_more
        self.page_count = page_count
        self.total = total

    def __repr__(self):
        # 此处只是简单地返回一个 JSON 字符串
        # 使用 JSONEncoder().encode 等同于使用 json.dumps
        # 因为后者在源码中的实现也是调用了 JSONEncoder 类
        return JSONEncoder().encode(self.__dict__)

class GlobalApiException(Exception):

    def __init__(self, cm):
        self.code_msg = cm
