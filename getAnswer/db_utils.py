from .extensions import mongo
from bson.objectid import ObjectId
from .models import Page

def get_option(name, default=None):
    return mongo.db.options.find_one({'code': name}) or default

def get_page(collection_name, pn=1, size=10, sort_by=None, filter1=None):
    _process_filter(filter1)
    size = size if size > 0 else 10     # 每页展示数量
    total = mongo.db[collection_name].count(filter1)    # 符合要求的数据的数量
    skip_count = size * (pn - 1)        # 略过的数据的数量
    result = []
    has_more = total > pn * size        # 布尔值，是否有更多数据待展示
    if total - skip_count > 0:
        # 查找数据
        result = mongo.db[collection_name].find(filter1, limit=size)
        # 排列数据
        if sort_by:
            result = result.sort(sort_by[0], sort_by[1])
        # 略过数据
        if skip_count > 0:
            result.skip(skip_count)
    # 计算总页数
    page_count = total // size
    if total % size > 0:
        page_count += 1
    page = Page(pn, size, sort_by, filter1, list(result), has_more,
            page_count, total)
    return page

def find_one(collection_name, filter1=None):
    _process_filter(filter1)
    return mongo.db[collection_name].find_one(filter1)

def _process_filter(filter1):
    if filter1 is None:
        return
    _id = filter1.get('_id')
    # 将传入参数 filter1 的 '_id' 对应的值转化为 ObjectId 类型
    if _id and not isinstance(_id, ObjectId):
        filter1['_id'] = ObjectId(_id)


def get_list(collection_name, sort_by=None, filter1=None, size=None):
    _process_filter(filter1)
    result = mongo.db[collection_name].find(filter1)
    if sort_by:
        result = result.sort(sort_by[0], sort_by[1])
    if size:
        result = result.limit(size)
    result = list(result)
    return result