# -*- coding: utf-8 -*-
import time

from hunterx.middlewares.middleware import Middleware


class UaMiddleware(Middleware):

    @staticmethod
    async def process_request(request):
        request.headers["User-Agent"] = "BestSpider/1.0"
        print(f"Headers added: {request.headers}")
        return request


class TimerMiddleware(Middleware):
    @staticmethod
    async def process_request(request):
        request.start_time = time.time()
        return request

    @staticmethod
    async def process_response(request, response):
        duration = time.time() - request.start_time
        print(f"Response time for {response.url}: {duration:.2f} seconds")
        return response
