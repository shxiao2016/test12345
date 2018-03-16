""" Configuration Objects
    TODO: read db parameters from cfg2
"""


class DBConfig(object):
    _config = None
    DB_URI = ('%(dialect)s+%(driver)s://%(username)s:%(password)s@%(host)s:%(port)'
              's/%(database)s?charset=%(charset)s')

    @classmethod
    def get_uri(cls):
        return cls.DB_URI % cls._config


class StagingConfig(DBConfig):
    host = None
    _config = {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'username': 'chinauser',
        'password': 'Chinacctest@123',
        'host': 'abe2-enable-s01.internal.linkedin.cn',
        'port': '3306',
        'database': 'zephyr_data_stg',
        'charset': 'utf8'
    }


class ProdConfig(DBConfig):
    host = None
    _config = {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'username': 'chinauser',
        'password': 'Chinacctest@123',
        'host': 'makto-db-061.corp.linkedin.com',
        'port': '3306',
        'database': 'zephyr_data',
        'charset': 'utf8'
    }


def getConfig(dev_env):
    if dev_env is None or dev_env:
        return StagingConfig.get_uri()
    else:
        return ProdConfig.get_uri()
