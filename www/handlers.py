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
    summary = 'Lorem ipsum dolor sit amet, consectetur adpipislicin elit sed wo tempo inciditundng up labore et doloire mabndf aliquea'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, create_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, create_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary, create_at=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


if __name__ == '__main__':
    fn = index
    if callable(fn):
        print('abc')
        method = getattr(fn, '__method__', None)
        path = getattr(fn, '__route__', None)
        if method and path:
            print('true')
