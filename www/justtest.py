# -*- coding:utf-8 -*

"""
测试类
"""

__author__ = 'zcj'

from www.models import User

from www import orm

from hashlib import sha1


def model_test():
    yield from orm.create_pool(user='www-data', password='www-data', database='awesome')

    user1 = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')

    yield from user1.save()


if __name__ == '__main__':
    # for x in model_test():
    #     pass
    utf8Str = ('253672586@qq.com' + ':' + 'zcj19901202').encode('utf-8')
    sha1Str = sha1(utf8Str).hexdigest()
    print(sha1Str)
