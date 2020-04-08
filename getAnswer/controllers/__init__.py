import json
from bson import ObjectId
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify


class MyEncoder(json.JSONEncoder):
    '''
    该类作为 json.dumps 方法的 cls 参数的值
    以处理特殊的、不能被序列化的值
    '''

    def default(self, o):
        '''参数 o 为被序列化的值'''
        # 如果 o 是 _id 字段或 datetime 类型的数据，将其转换为字符串
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        # 否则调用父类的同名方法触发 TypeError 异常
        super().default(o)


def config_route(app):
    @app.route('/')
    def home():
        # mongo.db 就是 PyFly 数据库，find 方法的返回值是迭代器
        # 这里使用 list 方法将其转换为列表
        users = list(mongo.db.users.find())
        # cls 参数用于处理特殊类型的数据
        # ensure_ascii=False 使得 JSON 字符串是 UTF-8 编码
        return json.dumps(users, cls=MyEncoder, ensure_ascii=False)