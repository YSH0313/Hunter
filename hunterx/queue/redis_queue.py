# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/9 10:47
# @Version: 1.0.0
# @Description: ''
import json
import asyncio
import platform
import redis.asyncio as aioredis
from typing import Optional

from hunterx.core.http.request_objects import FormRequests, Requests, PatchRequests
from hunterx.core.instancemeta import Base
from hunterx.utils.expandjsonencode import ExpandJsonEncoder
from hunterx.utils.log import LogCaptor


class PriorityRedis(Base):
    name: Optional[str] = None
    custom_settings: Optional[dict] = None
    _instance = None  # 类变量存储实例

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PriorityRedis, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()  # 显式调用祖父类的 __init__ 方法
            self.logger = LogCaptor().get_logger()

            self.__ONLINE = self._settings.ONLINE_SYS.lower()

            self.__REDIS_HOST_LISTS = self._settings.REDIS_HOST_LISTS
            self.__REDIS_ACCOUNT = self._settings.REDIS_ACCOUNT
            self.__REDIS_ENABLED = self._settings.REDIS_ENABLED
            self.__FILTER = self._settings.FILTER
            if len(self.__REDIS_HOST_LISTS) == 1 and self.__REDIS_ENABLED:
                for redis_server in self.__REDIS_HOST_LISTS:
                    for host, port in redis_server.items():
                        self.__redis_host = host
                        self.__redis_port = port
                for username, password in self.__REDIS_ACCOUNT.items():
                    self.__redis_username = username
                    self.__redis_password = password

            self.amqp_url = f'redis://default:{self.__redis_password}@{self.__redis_host}:{self.__redis_port}'

            self.queue_name = f'ysh_{self.name}'

            if platform.system().lower() == self.__ONLINE:
                self.queue_name += f'_{self.__ONLINE}'

            self._redis_pool = None  # 连接池初始化为空

            self._initialized = True

    async def create_redis_pool(self):
        if not self._redis_pool:  # 如果连接池尚未创建，才创建新的连接池
            self._redis_pool = await aioredis.from_url(
                self.amqp_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10,  # 最大连接数
                socket_timeout=5,  # 请求超时（秒）
                socket_connect_timeout=5,  # 请求超时（秒）
                retry_on_timeout=True,  # 超时后是否自动重试
                health_check_interval=30,  # 每30秒检查连接池健康状况
            )
        return self._redis_pool

    async def get_keys_by_prefix(self, redis, prefix):
        cursor = b'0'
        matched_keys = []

        while cursor:
            # SCAN 命令获取与前缀匹配的键（每次最多100个，避免阻塞）
            cursor, keys = await redis.scan(cursor=cursor, match=prefix + '*', count=100)
            matched_keys.extend(keys)

        # 按照优先级由高到低对key进行排序
        sorted_keys = sorted(matched_keys, key=lambda x: int(x.split('-')[-1]), reverse=True)

        return sorted_keys

    async def declare_priority_queue(self):
        redis = await self.create_redis_pool()

        keys = await self.get_keys_by_prefix(redis, self.queue_name)

        if keys:
            await redis.delete(*keys)

    async def get_queue_length(self):
        redis = await self.create_redis_pool()
        keys = await self.get_keys_by_prefix(redis, self.queue_name)

        task_len = 0
        if len(keys) > 0:
            # 检查key的类型
            key_type = await redis.type(keys[0])

            cmd_map = {
                'list': redis.llen,
                'set': redis.scard,
            }

            # 获取对应的队列检查方法
            cmd = cmd_map[key_type]

            # 每个键的任务数量
            key_len = [(k, await cmd(k)) for k in keys]

            # 所有键的任务数量
            task_len = sum(dict(key_len).values())
        return task_len

    async def get_mes(self, item):
        # 序列化任务参数
        if isinstance(item, (Requests, FormRequests, PatchRequests)):
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
            messages_body = json.dumps(mess_demo, cls=ExpandJsonEncoder)
            return messages_body
        elif isinstance(item, dict):
            messages_body = json.dumps(item, cls=ExpandJsonEncoder)
            return messages_body
        else:
            return item

    async def producer_mes(self, message_body, level=0):
        '''
        双端队列，左边推进任务
        :param level: 优先级(int类型)，数值越大优先级越高，默认1
        :return: 任务队列任务数量
        '''
        redis = await self.create_redis_pool()
        # 重新定义优先队列的key
        key = self.queue_name

        level = message_body.__dict__.get('level', level)

        new_key = key + '-' + str(level)

        messages_body = await self.get_mes(item=message_body)

        if self.__FILTER:
            await redis.sadd(new_key, messages_body)
        else:
            await redis.lpush(new_key, messages_body)

    async def consumer_redis(self):
        '''
        双端队列 右边弹出任务
        :param keys: 键列表，默认为None（将获取所有任务的keys）
        :return:
        '''
        redis = await self.create_redis_pool()
        while True:
            queue_len = await self.get_queue_length()  # 检查队列的消息数量，有则消费，无则等待
            if queue_len > 0:
                all_keys = await self.get_keys_by_prefix(redis, self.queue_name)

                if all_keys:
                    if self.__FILTER:
                        task = await redis.spop(all_keys[0])  # 左边弹出任务，优先消费优先级高的
                        print(task)
                        await self.process_message(task[1])
                    else:
                        # task_key, task = self.r.brpop(all_keys)  # 右边弹出任务,优先消费优先级低的
                        task = await redis.blpop(all_keys[0])  # 左边弹出任务，优先消费优先级高的

                        await self.process_message(task[1])
            else:
                await asyncio.sleep(1)

    async def process_message(self, message):
        print(f"Redis message: {message}")
