# -*- coding:utf-8 -*-

"""
url处理函数
"""

__author__ = 'zcj'

import re, time, json, logging, hashlib, base64, asyncio

from www.apis import Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
from www.coroweb import get, post
from www.models import User, Blog, Comment, next_id
from www.config import configs
from www.markdown2 import markdown

from aiohttp import web

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&' '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                filter(lambda s: s.strip() != '', text.split('\n')))
    return lines


def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.INFO('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/')
async def index(request):
    '''
    用户浏览页：首页
    '''
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


@get('/blog/{id}')
async def get_blog(id):
    '''
    用户浏览页：日志详情页
    '''
    blog = await Blog.find(id)
    comments = await Comment.findAll('blog_id=?', [id], orderBy='create_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@get('/manage/blogs')
def manage_blogs(*, page='1'):
    '''
    管理页面：日志列表页
    '''
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }


@get('/manage/blogs/create')
def manage_create_blog():
    '''
    管理页面：创建日志页
    '''
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }


@get('/api/blogs')
async def api_blogs(*, page='1'):
    '''
    后端API：获取日志
    '''
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blog=())
    blogs = await Blog.findAll(orderBy='create_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    '''
    后端API：获取具体一篇日志
    '''
    blog = await Blog.find(id)
    return blog


@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    '''
    后端API：创建日志
    '''
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    await blog.save()
    return blog


@get('/register')
def register():
    '''
    用户浏览页：注册页
    '''
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin():
    '''
    用户浏览页：登录页
    '''
    return {
        '__template__': 'signin.html'
    }


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist')
    user = users[0]
    # check passwd
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid passwd.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/signout')
def signout(request):
    '''
    用户浏览页:注销页
    '''
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.INFO('user signed out.')
    return r


@get('/api/users')
async def api_get_users():
    '''
    后端API：获取用户
    '''
    users = await User.findAll(orderBy='create_at desc')
    for u in users:
        u.passwd = '******'
    return dict(users=users)


@post('/api/users')
async def api_register_user(*, email, name, passwd):
    '''
    后端API：创建新用户
    '''
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name, email=email, passwd=hashlib.sha1(
        sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/manage/users')
def manage_users(*, page='1'):
    '''
    管理页面：用户列表页
    '''
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }


@get('/manage/comments')
def manage_comments(*, page='1'):
    '''
    管理页面：评论列表页
    '''
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }


@get('/api/comments')
async def api_comments(*, page='1'):
    '''
    后端API：获取评论
    '''
    page_index = get_page_index(page)
    num = await Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.findAll(orderBy='create_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)


@get('/manage/blogs/edit')
async def manage_edit_blog(*, id):
    '''
    管理页面：修改日志页
    '''
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id
    }


@post('/api/blogs/{id}')
async def api_update_blog(id, request, *, name, summary, content):
    '''
    后端API：修改日志
    '''
    check_admin(request)
    blog = await Blog.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = summary.strip()
    await blog.update()
    return blog


@post('/api/blogs/{id}/delete')
async def api_delete_blog(request, *, id):
    '''
    后端API：删除日志
    '''
    check_admin(request)
    blog = await Blog.find(id)
    await blog.remove()
    return dict(id=id)


@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
    '''
    后端API：创建评论
    '''
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
    await comment.save()
    return comment


@post('/api/comments/{id}/delete')
async def api_delete_comment(id, request):
    '''
    后端API：删除评论
    '''
    check_admin(request)
    comment = await Comment.find(id)
    if comment is None:
        raise APIResourceNotFoundError('Comment')
    await comment.remove()
    return dict(id=id)


# todo：管理页面：评论列表页（GET /manage/commnets)、修改日志页（GET /manage/blogs/edit）、用户列表页（GET /manage/users）
# todo：后端API：修改日志（POST /api/blogs/edit/:blog_id）、删除日志（POST /api/blogs/:blog_id/delete）、获取评论（GET /api/comments）
# todo：后端API：创建评论（POST /api/blogs/:blog_id/comments）、删除评论（POST /api/comments/:comment_id/delete）


if __name__ == '__main__':
    pass
