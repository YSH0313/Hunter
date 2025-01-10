# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/6 10:25
# @Version: 1.0.0
# @Description: ''
from typing import Union

from hunterx.core.http.request_objects import Response
from hunterx.core.data_class.data_class import RequestParams
from hunterx.internet.proxys import asy_rand_choi_pool, get_ua


class Middleware:

    @staticmethod
    async def process_open(spider: object):
        """爬虫启动前的处理"""
        return spider

    @staticmethod
    async def process_executed(spider: object):
        """爬虫启动成功的处理"""
        return spider

    @staticmethod
    async def process_close(spider: object):
        """爬虫结束的处理"""
        return spider

    @staticmethod
    async def process_request(request: RequestParams) -> RequestParams:
        """在请求发送前处理"""
        return request

    @staticmethod
    async def process_response(request: RequestParams, response: Response) -> Response:
        """在响应返回后处理"""
        return response

    @staticmethod
    async def process_exception(request: RequestParams, exception):
        """在请求或响应阶段捕获异常"""
        raise exception


class SpiderMiddleware(Middleware):

    @staticmethod
    async def process_open(spider: object):
        print('11111111')
        return spider

    @staticmethod
    async def process_executed(spider: object):
        print('22222222')
        return spider

    @staticmethod
    async def process_close(spider: object):
        print('33333333')
        return spider


class ProxyMiddleware(Middleware):

    @staticmethod
    async def process_request(request):
        proxy = None
        request.IS_PROXY = True if request.url not in request.Agent_whitelist and request.IS_PROXY else False
        if request.IS_PROXY and ((proxy == None) or (request.is_change)):
            proxy = await asy_rand_choi_pool()
            if request.IS_SAMEIP:
                request.meta['proxy'] = proxy
                request.task['meta']['proxy'] = proxy
        return request


class UaMiddleware(Middleware):

    @staticmethod
    async def process_request(request):
        if isinstance(request.headers, dict) and request.UA_PROXY:
            request.headers['User-Agent'] = await get_ua()
        return request
