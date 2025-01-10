# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/6 10:28
# @Version: 1.0.0
# @Description: ''
from typing import Optional, List

from hunterx.core.http.request_objects import Response
from hunterx.core.data_class.data_class import RequestParams
from hunterx.middlewares.middleware import Middleware, SpiderMiddleware


class MiddlewareManager:
    def __init__(self, middlewares: Optional[List[Middleware]] = None):
        """
        初始化中间件管理器。

        :param middlewares: 一个中间件列表，每个中间件必须继承 Middleware
        """
        self.middlewares = middlewares
        self._reverse_middlewares = list(reversed(middlewares)) if middlewares else []

    async def handle_open(self, spider) -> object:
        """
        按顺序处理所有中间件的 process_request。
        """
        if self.middlewares:
            for middleware in self.middlewares:
                if middleware is SpiderMiddleware:
                    spider = await middleware.process_open(spider)
        return spider

    async def handle_executed(self, spider) -> object:
        """
        按顺序处理所有中间件的 process_request。
        """
        if self.middlewares:
            for middleware in self.middlewares:
                if middleware is SpiderMiddleware:
                    spider = await middleware.process_executed(spider)
        return spider

    async def handle_close(self, spider) -> object:
        """
        按顺序处理所有中间件的 process_request。
        """
        if self.middlewares:
            for middleware in self.middlewares:
                if middleware is SpiderMiddleware:
                    spider = await middleware.process_close(spider)
        return spider

    async def handle_request(self, request: RequestParams) -> RequestParams:
        """
        按顺序处理所有中间件的 process_request。
        """
        if self.middlewares:
            for middleware in self.middlewares:
                if isinstance(middleware, type) and issubclass(middleware, Middleware):
                    request = await middleware.process_request(request)
        return request

    async def handle_response(self, request: RequestParams, response: Response) -> Response:
        """
        按顺序处理所有中间件的 process_response，倒序调用。
        """
        if self.middlewares:
            for middleware in self._reverse_middlewares:
                if isinstance(middleware, type) and issubclass(middleware, Middleware):
                    response = await middleware.process_response(request, response)
        return response

    async def handle_exception(self, request: RequestParams, exception):
        """
        按顺序处理所有中间件的 process_exception。
        """
        if self.middlewares:
            for middleware in self.middlewares:
                if isinstance(middleware, type) and issubclass(middleware, Middleware):
                    try:
                        await middleware.process_exception(request, exception)
                    except Exception as exc:
                        exception = exc  # 更新异常
        raise exception
