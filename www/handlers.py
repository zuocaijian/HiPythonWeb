# -*- coding:utf-8 -*-

"""
url处理函数
"""

__author__ = 'zcj'

import re, time, json, logging, hashlib, base64, asyncio

from www.coroweb import get, post
from www.models import User, Blog, Comment


@get('/')
async def index(request):
    # users = await User.findAll()
    user1 = {'name': 'zcj', 'email': '253672586@qq.com'}
    user2 = {'name': 'zcj', 'email': '253672586@qq.com'}
    users = [user1, user2]
    return {
        '__template__': 'test.html',
        'users': users
    }


if __name__ == '__main__':
    fn = index
    if callable(fn):
        print('abc')
        method = getattr(fn, '__method__', None)
        path = getattr(fn, '__route__', None)
        if method and path:
            print('true')
