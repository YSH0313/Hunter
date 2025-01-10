# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2024/12/31 15:52
# @Version: 1.0.0
# @Description: ''
import asyncio
import os
import time
from collections.abc import Iterable
from typing import Optional, Any
from collections.abc import Iterator

from hunterx.commands.config import white_text, blue_text, purple_text, reset_all
from hunterx.core import ManagerRedis
from hunterx.core.http.request_objects import Requests, Response
from hunterx.middlewares.middleware_manager import MiddlewareManager
from hunterx.utils.single_tool import now_time


class RedisSpider(ManagerRedis):
    name: Optional[str] = None
    custom_settings: Optional[dict] = None

    def __init__(self):
        if not getattr(self, "name", None):
            raise ValueError(f"{type(self).__name__} must have a name")
        if not hasattr(self, "start_urls"):
            self.start_urls: list[str] = []

        self.__Asynch = self._settings.ASYNC_PROD
        self.__Auto_clear = self._settings.AUTO_CLEAR

        self.__Waiting_time = self._settings.WAITTING_TIME
        self.__Delay_time = self._settings.DELAY_TIME

    def open_spider(self, spider):
        """开启spider第一步检查状态"""
        self.logger.info(f'Crawler program starts --> {spider.name}')

    def run_start_async(self, func, start_fun):
        print(isinstance(func, Iterator))
        asyncio.run(start_fun(func))

    async def make_start_request(self, start_fun: {__name__}):
        try:
            start_task = self.__getattribute__(start_fun.__name__)()
            if isinstance(start_task, Iterator):
                for s in start_task:
                    await self.producer_mes(message_body=s)
        except Exception as e:
            self.logger.error('Error in make_start_request', exc_info=True)

    def start_requests(self) -> Iterable[Requests]:
        if not self.start_urls:
            raise AttributeError(
                "The spider did not start. start_urls not found, or it was found but is empty. Please check if it has been added correctly."
            )
        for url in self.start_urls:
            yield Requests(url=url, callback=self.parse)

    async def parse(self, response: Response) -> Any:
        pass
        # 其他解析逻辑

    def parse_only(self, task: Any) -> Any:
        pass

    def close_spider(self, **kwargs: Any) -> None:
        pass

    def run(self):
        asyncio.run(self.execute())

    async def execute(self):
        """启动spider的入口"""
        self.starttime = now_time()
        self.start_time = time.time()

        # 单个爬虫启动时的处理逻辑
        self.open_spider(spider=self)

        # 通用中间件爬虫启动时的处理逻辑
        await MiddlewareManager(self.middlewares).handle_open(self)

        if self.__Auto_clear:
            await self.declare_priority_queue()

        if self.__Asynch:  # 如果是异步生产（一边生产一边消费）
            asyncio.create_task(self.make_start_request(start_fun=self.start_requests))

        else:  # 如果不需要异步生产（等生产完之后再开始消费）
            await asyncio.create_task(self.make_start_request(start_fun=self.start_requests))

        # 通用中间件爬虫启动成功的处理逻辑
        await MiddlewareManager(self.middlewares).handle_executed(self)

        # 开启监控队列状态
        # asyncio.run_coroutine_threadsafe(self.shutdown_spider(spider_name=self.name), self.shutdown_loop)
        monitor_task = asyncio.create_task(self.shutdown_spider(spider_name=self.name))

        # 开启消费者
        # await asyncio.create_task(self.consumer_redis())
        consumer_task = asyncio.create_task(self.consumer_redis())

        await asyncio.gather(monitor_task, consumer_task)

    async def shutdown_spider(self, spider_name: str):
        """监控队列及运行状态"""
        try:
            while True:
                now_time = time.time()
                queue_len = await self.get_queue_length()

                self.logger.debug(f'{white_text}{round(now_time - self.last_time)} {blue_text}seconds have passed since the last dequeue operation, and there is {purple_text}{queue_len} {blue_text}message remaining in the queue.{reset_all}')

                if ((now_time - self.last_time >= self.__Waiting_time) and (queue_len == 0)):
                    # do something
                    break

                # self.rm_task()  # 清除已结束的线程
                self.survival_tasks()  # 清除已结束的任务

                await asyncio.sleep(self.__Delay_time)

            self.close_spider()

            self.finished_info(self.starttime, self.start_time)  # 完成时的日志打印

            # 通用中间件爬虫启动成功的处理逻辑
            await MiddlewareManager(self.middlewares).handle_close(self)

            os._exit(0)
        except Exception as e:
            self.logger.error(e, exc_info=True)


if __name__ == '__main__':
    start_run = RedisSpider()
    start_run.run()
