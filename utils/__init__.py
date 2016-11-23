# -*- coding:utf-8 -*-

"""
常用方法集
"""

__author__ = 'zcj'

import os
import sys


# 获取当前路径并转换成绝对路径
def rePath2AbsPath():
    return os.path.abspath('.')


# 获取当前模块的名字
def get_curr_module_name():
    return __file__


# 获取命令行参数
def get_cmd_args():
    return sys.argv


# 获取当前python命令的可执行文件路径
def get_exe_path():
    return sys.executable
