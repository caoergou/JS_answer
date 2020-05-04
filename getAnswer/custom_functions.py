

from datetime import datetime, timedelta

from .db_utils import get_option, get_list, get_page, find_one

def utc2local(utc_st):
    '''将 UTC 标准时间转换成本地时间'''

    now_stamp = datetime.now().timestamp()
    local_time = datetime.fromtimestamp(now_stamp)
    utc_time = datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st


def mongo_date_str(date):
    '''将 datetime 数据类型转换为本地时间后再转换成字符串返回'''

    return utc2local(date).strftime('%Y-%m-%d %H:%M') if date else ''


def date_cal(num, is_add=True):
    d1=datetime.now()
    delta = timedelta(num)
    if is_add:
        return d1 + delta
    else:
        return d1 - delta


def init_func(app):

    app.add_template_global(get_option, 'get_option')
    app.add_template_global(get_list, 'get_list')
    app.add_template_global(get_page, 'get_page')
    app.add_template_global(find_one, 'mongo_find_one')
    app.add_template_global(datetime.now, 'now')
    app.add_template_filter(mongo_date_str, 'mongo_date_str')
    app.add_template_global(date_cal, 'date_cal')

