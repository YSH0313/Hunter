# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2024/12/31 18:23
# @Version: 1.0.0
# @Description: ''
import asyncio
import json
import heapq

from hunterx.core.http.request_objects import Requests, FormRequests, PatchRequests
from hunterx.core.instancemeta import Base
from hunterx.utils.expandjsonencode import ExpandJsonEncoder
from hunterx.utils.log import LogCaptor


class PriorityQueue(Base):

    def __init__(self):
        super().__init__()
        self.logger = LogCaptor().get_logger()

        self._queue = []
        self._index = 0
        self.callback_map = {}  # 回调函数优先级map表

    async def push(self, item, priority=0):
        # 序列化任务参数
        if (isinstance(item, FormRequests)) or (isinstance(item, Requests)) or (isinstance(item, PatchRequests)):
            mess_demo = {}
            fun_name = ''
            for k, v in item.__dict__.items():
                if (k == 'callback') and (v != None):
                    if (isinstance(v, str)):
                        mess_demo[k] = v
                    else:
                        fun_name = v.__name__
                        mess_demo['callback'] = fun_name
                else:
                    mess_demo[k] = v
            if fun_name not in self.callback_map.keys():
                self.callback_map[fun_name] = mess_demo.get('level') or 0
            priority = mess_demo.get('level')
            item = json.dumps(mess_demo, cls=ExpandJsonEncoder)
        heapq.heappush(self._queue, (-priority, self._index, item))  # 添加优先级和索引及元素
        self._index += 1

    async def pop(self):
        if self._queue:
            data = heapq.heappop(self._queue)[-1]  # 返回元素不返回优先级和索引
            return data

    async def consumer_memory(self):
        '''
        双端队列 右边弹出任务
        :param keys: 键列表，默认为None（将获取所有任务的keys）
        :return:
        '''
        try:
            self.logger.info('Consumer has initiated')
            while True:
                if len(self._queue) > 0:
                    task = await self.pop()
                    if task:
                        await self.process_message(task)
                else:
                    await asyncio.sleep(1)
        except Exception as e:
            self.logger.error('Error in consumer_memory', exc_info=True)

    async def process_message(self, task):
        self.logger.info(f'Queue Message: {task}')
