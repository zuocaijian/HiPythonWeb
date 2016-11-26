# -*- coding:utf-8 -*-

"""
开发环境下的配置文件，以使用不动的web环境
"""

__author__ = 'zcj'

configs = {
    'db': {
        'host': '127.0.0.1',
        'port': '3306',
        'user': 'www-data',
        'password': 'www-data',
        'database': 'awesome'
    },
    'session': {
        'secret': 'AwEsOmE'
    }
}
