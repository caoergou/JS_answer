from .extensions import mongo

def get_option(name, default=None):
    return mongo.db.options.find_one({'code': name}) or default