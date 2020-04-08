import os


class DevConfig:
    '''开发环境配置'''

    MONGO_URI = 'mongodb://localhost:27017/pyfly'


class ProConfig(DevConfig):
    '''生产环境配置'''


configs = {
        'Dev': DevConfig,
        'Pro': ProConfig
}