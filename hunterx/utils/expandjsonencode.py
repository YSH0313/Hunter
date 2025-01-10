# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/8 10:51
# @Version: 1.0.0
# @Description: ''
import json
from datetime import datetime, date


class ExpandJsonEncoder(json.JSONEncoder):
    '''
    采用json方式序列化传入的任务参数，而原生的json.dumps()方法不支持datetime、date，这里做了扩展
    '''

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
