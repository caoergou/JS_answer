from whoosh.index import create_in, open_dir, exists_in
from whoosh import writing
import os


class WhooshSearcher:
    def __init__(self, app=None):
        self.initialized = False
        # 索引文件存储路径
        self.whoosh_path = 'whoosh_indexes'
        self.indexes = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        # 在 app 里面关联 whoosh_searcher
        if 'whoosh_searcher' not in app.extensions:
            app.extensions['whoosh_searcher'] = self
        # 添加 config 中的配置
        if app.config['WHOOSH_PATH'] is not None:
            self.whoosh_path = app.config['WHOOSH_PATH']
        # WHOOSH_PATH = os.path.join(os.getcwd(), 'whoosh_indexes')
        # 在配置中的位置上新建索引存储目录的文件
        if not os.path.exists(self.whoosh_path):
            os.mkdir(self.whoosh_path)
        # 初始化结束
        self.initialized = True

    def add_index(self, index_name, schema):
        '''创建索引'''
        if not self.initialized:
            raise Exception('not initialized')
        # 如果索引存储目录已经建立就打开它
        if exists_in(self.whoosh_path, index_name):
            ix = open_dir(self.whoosh_path, index_name)
        else:
            # 否则，按照 schema 模式建立索引存储目录
            ix = create_in(self.whoosh_path, schema, index_name)
        # ix 存储在 self.indexes 字典里,方便在类的其他方法里调用
        self.indexes[index_name] = ix

    def get_index(self, index_name):
        '''打开索引'''
        if not exists_in(self.whoosh_path, index_name):
            raise Exception('This index is not exists')
        ix = self.indexes[index_name]
        if ix is None:
            # 打开索引
            ix = open_dir(self.whoosh_path, index_name)
            self.indexes[index_name] = ix
        return ix

    def get_writer(self, index_name):
        '''获得索引存储目录的写入对象'''
        return self.get_index(index_name).writer()

    def get_searcher(self, index_name):
        '''获得索引存储目录的搜索对象'''
        return self.get_index(index_name).searcher()

    def add_document(self, index_name, doc):
        '''写入索引文件'''
        writer = self.get_writer(index_name)
        writer.add_document(**doc)
        writer.commit()

    def update_document(self, index_name, unique_field, doc):
        '''更新索引文件'''
        writer = self.get_writer(index_name)
        writer.update_document(**unique_field, **doc)
        writer.commit()

    def delete_document(self, index_name, fieldname, termtext):
        '''删除索引文件'''
        writer = self.get_writer(index_name)
        writer.delete_by_term(fieldname, termtext)
        writer.commit()

    def clear(self, index_name):
        '''清除索引'''
        writer = self.get_writer(index_name)
        writer.commit(mergetype=writing.CLEAR)