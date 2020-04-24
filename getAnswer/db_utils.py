from .extensions import mongo
from bson.objectid import ObjectId

def get_option(name, default=None):
    return mongo.db.options.find_one({'code': name}) or default


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