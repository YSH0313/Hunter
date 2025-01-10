# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2024/12/30 18:46
# @Version: 1.0.0
# @Description: '工具类'


def re_name(str_data: str):
    """格式化爬虫类名"""
    new_name = ''.join([i.capitalize() for i in str_data.split('_')])
    return new_name
