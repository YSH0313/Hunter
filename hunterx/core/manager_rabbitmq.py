# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2020-02-23 09:56:50
# @Version: 1.0.0
# @Description: Manager核心文件
import ssl

from aio_pika import IncomingMessage
from requests.exceptions import ProxyError

ssl._create_default_https_context = ssl._create_unverified_context
import json
import time
import httpx
import aiohttp
import asyncio
import inspect
import concurrent.futures
from parsel import Selector
from typing import Optional, Callable

from hunterx.core.Basic import Basic
from hunterx.utils.log import LogCaptor
from hunterx.utils.expandjsonencode import ExpandJsonEncoder
from hunterx.internet.proxys import asy_rand_choi_pool
from hunterx.core.http.make_args import MakeArgs
from hunterx.core.http._requests import AsyncRequest
from hunterx.middlewares.middleware_loader import load_middlewares
from hunterx.middlewares.middleware_manager import MiddlewareManager
from hunterx.core.http.request_objects import Response, Requests, FormRequests, PatchRequests
from hunterx.core.data_class.data_class import RequestParams
from hunterx.utils.single_tool import is_json, per_dic_plus
from hunterx.items.baseitem import Item
# from hunterx.piplines.pipeline_loader import load_pipelines
from hunterx.piplines.pipelines_manager import PipelineManager
from hunterx.core.instancemeta import Base


class ManagerRabbitmq(Basic, Base):
    name: Optional[str] = None
    custom_settings: Optional[dict] = None

    def __init__(self):
        # super().__init__()

        self.last_time = time.time()
        self.starttime = None

        self.running_tasks = []

        self.logger = LogCaptor().get_logger()

        self.__PREFETCH_COUNT = self._settings.PREFETCH_COUNT
        self.__TIME_OUT = self._settings.TIME_OUT
        self.__IS_PROXY = self._settings.IS_PROXY
        self.__IS_SAMEIP = self._settings.IS_SAMEIP
        self.__max_request = self._settings.MAX_REQUEST
        self.__Agent_whitelist = self._settings.AGENT_WHITELIST
        self.__retry_http_codes = self._settings.RETRY_HTTP_CODES
        self.__UA_PROXY = self._settings.UA_PROXY
        self.__IS_INSERT = self._settings.IS_INSERT

        self.__Concurrency = self.__PREFETCH_COUNT

        self.__MIDDLEWARES = self._settings.MIDDLEWARES
        self.middlewares = load_middlewares(self.__MIDDLEWARES) or None

        # self.__ITEM_PIPELINES = self._settings.ITEM_PIPELINES
        # self.pipelines = load_pipelines(self.__ITEM_PIPELINES) or None

    def stop_tasks(self):  # 主动停止正在执行的请求
        for task in self.running_tasks:
            if not task.cancelled():
                task.cancel()

    def survival_tasks(self):  # 清除已结束的任务
        for task in self.running_tasks:
            if task:
                print(task)
                if task.done():
                    self.running_tasks.remove(task)
        return len(self.running_tasks)

    async def process_message(self, message: IncomingMessage):
        """消息处理函数"""
        self.last_time = time.time()
        self.__Concurrency -= 1
        async with message.process():  # 自动确认消息
            task = message.body.decode('utf-8')
            # while self.__Concurrency < 0:
            #     self.logger.debug(f'The request queue is full. Please wait for the results to be returned. {self.__Concurrency}')
            #     time.sleep(1)
            if self.__Concurrency <= 0:
                self.logger.debug(f'The request queue is full. Please wait for the results to be returned. {self.__Concurrency}')
            flag = is_json(task)
            if not flag:  # 判断是否为请求消息，如果不是的话
                if inspect.isgeneratorfunction(self.parse_only):
                    messages = self.parse_only(body=task).__next__()  # 获取生成器元素
                    callback = messages.callback.__name__  # 获取callback函数名
                    self.callback_map[callback] = messages.__dict__.get('level') or 0  # 定义callback优先级
                    messages.level = self.callback_map[callback] + 1  # 增加消息优先级
                    # self.async_thread_pool.submit(self.producer_mes, message_body=messages, is_thread=True)  # 多线程数据处理
                    asyncio.create_task(self.producer_mes(message_body=messages))
                else:
                    # self.async_thread_pool.submit(self.parse_only, body=task)  # 多线程数据处理
                    asyncio.create_task(self.parse_only(body=task))

                self.__Concurrency += 1
            if flag:  # 判断是否为请求消息，如果是的话
                params = MakeArgs.make_params(
                    task=task, agent_whitelist=self.__Agent_whitelist, is_proxy=self.__IS_PROXY,
                    is_sameip=self.__IS_SAMEIP, ua_proxy=self.__UA_PROXY, time_out=self.__TIME_OUT
                )

                await asyncio.create_task(self.make_requests(RequestParams(**params)))

                # requests_task = asyncio.create_task(self.make_requests(RequestParams(**params)))
                # self.running_tasks.append(requests_task)

    async def make_requests(self, request_params: RequestParams):
        """请求处理函数"""
        try:
            # 请求前的中间件调用
            request_params = await MiddlewareManager(self.middlewares).handle_request(request_params)

            # 处理ip代理和ua头，待观察
            # await MakeArgs.request_preprocess(
            #     request_params, self.__Agent_whitelist, self.__IS_PROXY, self.__IS_SAMEIP, self.__UA_PROXY
            # )

            while request_params.retry_count < self.__max_request:

                # 判断是否要忽略使用代理
                request_params.task['proxy'] = proxy = request_params.proxy if not request_params.ignore_ip else None

                try:

                    response_iter = AsyncRequest.asyn_request(
                        request_params.method, request_params.url, request_params.headers, request_params.timeout,
                        request_params.cookies, request_params.is_encode, request_params.is_httpx,
                        request_params.is_TLS, request_params.is_file, request_params.stream, request_params.file_path,
                        request_params.chunk_size, http2=request_params.http2, params=request_params.params,
                        data=request_params.data, json=request_params.json_params, proxy=request_params.proxy,
                        verify_ssl=request_params.verify_ssl, allow_redirects=request_params.allow_redirects
                    )

                    async for response_result in response_iter:
                        response = response_result['response']
                        content = response_result['content']

                        # 响应后的中间件调用
                        response = await MiddlewareManager(self.middlewares).handle_response(request_params, response)

                        if request_params.is_file and request_params.stream:
                            content = AsyncRequest.iter_chunked(content, request_params.is_httpx,
                                                                request_params.chunk_size)

                        status_code = per_dic_plus(response.__dict__, ['status', 'status_code'])

                        # 打印日志
                        await self.infos(status_code, request_params.method, request_params.url)

                        text = await self.handle_encoding(
                            res=content, task=request_params.task, is_file=request_params.is_file,
                            encoding=request_params.encoding
                        )

                        if text:
                            if '您的授权设置可能有问题' in text and '您当前的客户端IP地址为' in text:
                                raise ProxyError(f'{proxy}代理并发数超限制')

                        response_last = Response(
                            url=request_params.url, headers=response.headers, data=request_params.data,
                            cookies=response.cookies, meta=request_params.meta, retry_count=request_params.retry_count,
                            text=text,
                            content=content, status_code=status_code, request_info=request_params.request_info,
                            proxy=proxy, level=request_params.level
                        )

                        await self.Iterative_processing(
                            method=request_params.method, callback=request_params.callback, response_last=response_last,
                            task=request_params.task, retry_count=request_params.retry_count
                        )

                    break
                except (aiohttp.ClientProxyConnectionError, aiohttp.ServerTimeoutError, TimeoutError,
                        concurrent.futures._base.TimeoutError, aiohttp.ClientHttpProxyError, asyncio.TimeoutError,
                        aiohttp.ServerDisconnectedError, aiohttp.ClientConnectorError, aiohttp.ClientOSError,
                        aiohttp.ClientPayloadError, httpx.ConnectTimeout, httpx.ConnectError, httpx.ProxyError,
                        httpx.ReadTimeout) as e:

                    request_params.retry_count += 1

                    await self.retry(
                        request_params.method, request_params.url, request_params.retry_count, repr(e),
                        request_params.task
                    )

                    if request_params.is_proxy:
                        proxy = await asy_rand_choi_pool()
                        if self.__IS_SAMEIP:
                            request_params.meta['proxy'] = proxy
                            request_params.task['meta']['proxy'] = proxy

                except concurrent.futures._base.CancelledError:
                    break

                except Exception as e:
                    if (not request_params.is_proxy) and (self.__max_request):
                        request_params.retry_count += 1
                        await self.retry(
                            request_params.method, request_params.url, request_params.retry_count, repr(e),
                            request_params.task
                        )
                        self.logger.error(f'{repr(e)} Returning to the queue {str(request_params.task)}', exc_info=True)
                    else:
                        request_params.retry_count += 1
                        mess = request_params.task
                        mess['is_change'] = True
                        mess['retry_count'] = request_params.retry_count
                        await self.producer_mes(message_body=json.dumps(mess, cls=ExpandJsonEncoder))
                        self.logger.error(f'{repr(e)} Returning to the queue {str(request_params.task)}', exc_info=True)
                        break
            else:
                response_last = Response(
                    url=request_params.url, headers={}, data={}, cookies=None, meta=request_params.meta,
                    retry_count=request_params.retry_count, text='', content=b'', status_code=None,
                    request_info=request_params.request_info, proxy=request_params.proxy, level=request_params.level
                )
                await self.Iterative_processing(
                    method=request_params.method, callback=request_params.callback, response_last=response_last,
                    task=request_params.task, retry_count=request_params.retry_count
                )

        except Exception as e:
            # 出现异常的中间件调用
            await MiddlewareManager(self.middlewares).handle_exception(request_params, e)

            self.logger.error(e, exc_info=True)
        self.__Concurrency += 1

    async def Iterative_processing(
            self,
            method: str,
            callback: Callable,
            response_last: Response,
            task: dict,
            retry_count: int
    ):
        """迭代器及异常状态码处理函数"""
        mess = task
        if (response_last.status_code != 200) and (response_last.status_code in self.__retry_http_codes) and (
                retry_count < self.__max_request):
            mess['retry_count'] = retry_count = int(retry_count) + 1
            if self.__IS_PROXY:
                mess['proxy'] = await asy_rand_choi_pool()
                if self.__IS_SAMEIP:
                    mess['meta']['proxy'] = mess['proxy']
            if (retry_count < self.__max_request):
                await self.producer_mes(message_body=json.dumps(mess, cls=ExpandJsonEncoder))
                await self.retry(method, response_last.url, str(retry_count),
                                 f'Wrong status code {response_last.status_code}', str(mess))
                self.exc_count += 1
            elif (retry_count == self.__max_request):
                self.logger.debug(f'Give up <{task}>')
                self.giveup_count += 1
                response_last.retry_count = retry_count
                await self.__deal_fun(callback=callback, response_last=response_last)
            return

        if (response_last.status_code != 200) and (response_last.status_code != None) and (
                response_last.status_code not in self.__retry_http_codes):
            if int(retry_count) < 3:
                mess['retry_count'] = retry_count = int(retry_count) + 1
                if self.__IS_PROXY:
                    mess['proxy'] = await asy_rand_choi_pool()
                    if self.__IS_SAMEIP:
                        mess['meta']['proxy'] = mess['proxy']
                await self.producer_mes(message_body=json.dumps(mess, cls=ExpandJsonEncoder))
                await self.retry(method, response_last.url, str(retry_count),
                                 f'Other wrong status code {response_last.status_code}', str(mess))
                self.other_count += 1
            else:
                self.logger.debug(f'Give up <{task}>')
                self.giveup_count += 1
                response_last.retry_count = retry_count
                await self.__deal_fun(callback=callback, response_last=response_last)
            return

        if (retry_count == self.__max_request):
            self.logger.debug(f'Give up <{task}>')
            self.giveup_count += 1
            response_last.retry_count = retry_count
        await self.__deal_fun(callback=callback, response_last=response_last)

    # @count_time
    async def __deal_fun(self, callback: Callable, response_last):
        """回调函数处理"""
        try:
            if response_last.text:
                response_last.xpath = Selector(text=response_last.text).xpath
            if inspect.isasyncgenfunction(getattr(self, callback)):
                async for item in getattr(self, callback)(response=response_last):
                    if isinstance(item, (Requests, FormRequests, PatchRequests)):
                        item.meta['proxy'] = response_last.meta.get('proxy')
                        callname = item.callback if isinstance(item.callback, str) else item.callback.__name__
                        if not item.level:
                            item.level = self.callback_map[callback] + 1 if callback != callname else self.callback_map[callback]
                        await self.producer_mes(message_body=item)
                    elif isinstance(item, Item):
                        await PipelineManager(self.pipelines).handle_process_item(item, self)

            else:
                await getattr(self, callback)(response=response_last)
        except Exception as e:
            self.exec_count += 1
            self.logger.error(e, exc_info=True)
