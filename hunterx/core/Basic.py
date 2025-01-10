# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2020-02-23 09:56:50
# @Version: 1.0.0
# @Description: 基本信息类
import re
import time
import json
import chardet  # 字符集检测
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from hunterx.queue import PriorityQueue, PriorityMq, PriorityRedis
# from hunterx.core.parentobj import ParentObj
from hunterx.utils.log import LogCaptor
from hunterx.utils.single_tool import now_time, is_contain_chinese
from hunterx.core.instancemeta import Base

_class_cache = {}


def create_dynamic_class(inherit_from, name, custom_settings):
    if inherit_from in _class_cache:
        return _class_cache[inherit_from]

    # 根据传入的参数动态创建类并继承指定的父类
    if inherit_from == "MemorySpider":
        cls = type("DynamicClass", (PriorityQueue, Base), {'name': name, 'custom_settings': custom_settings})
    elif inherit_from == "RabbitmqSpider":
        cls = type("DynamicClass", (PriorityMq, Base), {'name': name, 'custom_settings': custom_settings})
    elif inherit_from == "RedisSpider":
        cls = type("DynamicClass", (PriorityRedis, Base), {'name': name, 'custom_settings': custom_settings})
    _class_cache[inherit_from] = cls
    return cls


class Basic:
    name: Optional[str] = None
    custom_settings: Optional[dict] = None

    def __init__(self):
        # super().__init__(self.custom_settings)
        # self.async_thread_pool = ThreadPoolExecutor()  # 线程池
        # self.work_list = []  # 线程子任务池
        self.logger = LogCaptor().get_logger()

        inherit_from = self.__class__.__bases__[0].__name__

        # 使用工厂函数动态选择父类
        DynamicClass = create_dynamic_class(inherit_from, self.name, self.custom_settings)

        # 在实例化时创建一个动态类
        self.instance = DynamicClass()
        self.bind_fun()
        self.charset_code = re.compile(r'charset=(.*?)"|charset=(.*?)>|charset="(.*?)"', re.S)

    def bind_fun(self):
        # 动态绑定 子类 中重写的方法
        attr_name = "process_message"
        attr_value = getattr(self, attr_name)
        # 仅绑定方法
        if callable(attr_value):
            setattr(self.instance, attr_name, attr_value)

    def __getattr__(self, name):
        # 将未找到的属性转发到 instance
        value = getattr(self.instance, name)
        setattr(self, name, value)  # 缓存属性
        return value

    # def rm_task(self):
    #     """移除已结束的线程子任务池"""
    #     [self.work_list.remove(i) for i in self.work_list if i.done()]

    async def handle_encoding(self, res: bytes, task: dict, is_file: bool, encoding: str):
        """编码处理函数"""
        if is_file:
            text = ''
            return text
        charset_code = chardet.detect(res[0:1])['encoding']
        if encoding:
            charset_code = encoding
        if charset_code:
            try:
                text = res.decode(charset_code)
                if not is_contain_chinese(text):
                    text = await self.cycle_charset(res, task)  # 此处存疑
                return text
            except (UnicodeDecodeError, TypeError, LookupError):
                text = await self.cycle_charset(res, task)
                if not text:
                    text = str(res, charset_code, errors='replace')
                return text
            except Exception as e:
                self.logger.error(f'{repr(e)} Decoding error {task}', exc_info=True)
        else:
            text = await self.cycle_charset(res, task)
            return text

    async def cycle_charset(self, res: bytes, task: dict):
        """异常编码处理函数"""
        charset_code_list = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        for code in charset_code_list:
            try:
                text = res.decode(code)
                return text
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f'{repr(e)} Decoding error {task}', exc_info=True)

    async def infos(self, status: int, method: str, url: str):
        """日志函数"""
        self.request_count += 1
        self.logger.info(f'Mining ({status}) <{method} {url}>')
        if str(status) == '200':
            self.success_code_count += 1
            self.logger.info(f'Catched from <{status} {url}>')

    async def retry(self, method: str, url: str, retry_count: int, abnormal: str, task: dict):
        """重试日志函数"""
        self.logger.debug(f'Retrying <{method} {url}> (failed {retry_count} times): {abnormal + str(task)}')
        self.wrong_count += 1

    def finished_info(self, starttime: str, start_time):
        Total_time = time.time() - start_time
        m, s = divmod(Total_time, 60)
        h, m = divmod(m, 60)
        import collections
        close_info = collections.OrderedDict()  # 将普通字典转换为有序字典
        close_info['Request_count'] = f'请求总数  --  {self.request_count}'
        close_info['Request_200_count'] = f'成功总数  --  {self.success_code_count}'
        close_info['Wrong_count'] = f'重试总数  --  {self.wrong_count}'
        close_info['Give_up_count'] = f'放弃总数  --  {self.giveup_count}'
        close_info['Abnormal_count'] = f'异常码总数  --  {self.exc_count}'
        close_info['Other_count'] = f'其他状态码总数  --  {self.other_count}'
        close_info['Start_time'] = f'开始时间  --  {starttime}'
        close_info['End_time'] = f'结束时间  --  {now_time()}'
        close_info['Total_time'] = "总耗时  --  %d时:%02d分:%02d秒" % (h, m, s)
        self.logger.info('\r\n' + json.dumps(close_info, indent=2, ensure_ascii=False))
