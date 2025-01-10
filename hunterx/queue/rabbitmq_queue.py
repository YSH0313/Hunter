# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2023-02-23- 09:56:50
# @Version: 1.0.0
# @Description: rabbitmq队列中间件
import json
import asyncio
import platform

import aiohttp
from typing import Optional

from aio_pika import connect_robust, ExchangeType, Message, IncomingMessage
from aio_pika.pool import Pool as AioPikaPool

from hunterx.core.http.request_objects import FormRequests, Requests, PatchRequests
from hunterx.core.instancemeta import Base
from hunterx.utils.expandjsonencode import ExpandJsonEncoder
from hunterx.utils.log import LogCaptor


class PriorityMq(Base):
    name: Optional[str] = None
    custom_settings: Optional[dict] = None
    _instance = None  # 类变量存储实例

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PriorityMq, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()  # 显式调用祖父类的 __init__ 方法
            self.logger = LogCaptor().get_logger()

            self.__Rabbitmq = self._settings.RABBITMQ_CONFIG

            self.__rabbit_username = self.__Rabbitmq['username']  # 连接mq的用户名
            self.__rabbit_password = self.__Rabbitmq['password']  # 连接mq的密码
            self.__rabbit_host = self.__Rabbitmq['host']  # mq的地址
            self.__rabbit_port = self.__Rabbitmq.get('port')  # mq的端口号

            self.__X_MAX_PRIORITY = self._settings.X_MAX_PRIORITY
            self.__PREFETCH_COUNT = self._settings.PREFETCH_COUNT
            self.__message_ttl = self._settings.X_MESSAGE_TTL
            self.__ONLINE = self._settings.ONLINE_SYS.lower()

            self.amqp_url = f"amqp://{self.__rabbit_username}:{self.__rabbit_password}@{self.__rabbit_host}/"

            self.exchange_name = f'ysh_{self.name}'
            self.queue_name = self.name
            self.routing_key = self.name
            if platform.system().lower() == self.__ONLINE:
                self.queue_name += f'_{self.__ONLINE}'
                self.routing_key += f'_{self.__ONLINE}'
            self.max_pool_size = 10

            # 初始化连接池
            self.pool = AioPikaPool(self._create_connection, max_size=self.max_pool_size)

            self._initialized = True

    async def declare_priority_queue(self):
        try:
            # 先删除已有队列
            async with self.pool.acquire() as connection:
                async with connection.channel() as channel:
                    await channel.queue_delete(self.queue_name)
            self.logger.info('The original queue has been cleared!')
        except Exception as e:
            self.logger.error(f"Error deleting queue: {e}", exc_info=True)

    async def get_queue_length(self):
        url = f'http://{self.__rabbit_host}:{self.__rabbit_port}/api/queues/%2F/{self.name}'
        auth = aiohttp.BasicAuth(self.__rabbit_username, self.__rabbit_password)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=auth) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('messages', 0)
                else:
                    self.logger.debug(f"Failed to get queue info: {response.status}")
                    return 0

    async def _create_connection(self):
        """
        创建与RabbitMQ的连接
        """
        return await connect_robust(self.amqp_url)

    async def make_mes(self, item):
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
            priority = mess_demo.get('level')
            item = json.dumps(mess_demo, cls=ExpandJsonEncoder)
            return item, priority

    async def setup_exchange_and_queue(self, channel):
        # 声明交换机
        exchange = await channel.declare_exchange(self.exchange_name, ExchangeType.DIRECT)

        # 自动声明队列，如果队列不存在，会自动创建
        queue = await channel.declare_queue(
            self.queue_name,
            durable=True,
            arguments={
                "x-max-priority": self.__X_MAX_PRIORITY,
                "x-message-ttl": self.__message_ttl
            }  # 设置最大优先级和最大消息的存活时间
        )

        # 绑定队列到交换机
        await queue.bind(exchange, routing_key=self.routing_key)

        return exchange, queue

    async def producer_mes(self, message_body):
        """
        生产者方法，向交换机发送消息
        """
        async with self.pool.acquire() as connection:
            async with connection.channel() as channel:
                # 获取交换机和队列
                exchange, _ = await self.setup_exchange_and_queue(channel)

                item, priority = await self.make_mes(message_body)

                # 发布消息到交换机，并设置优先级
                message = Message(item.encode('utf-8'), priority=priority)
                await exchange.publish(message, routing_key=self.routing_key)
                # print(f"Message sent to exchange '{self.exchange_name}' with routing_key '{self.routing_key}'")

    async def process_message(self, message: IncomingMessage):
        """
        消费者回调方法，处理接收到的消息
        """
        async with message.process():  # 自动确认消息
            print(f"Received message: {message.body.decode()}")
            # 模拟消息处理
            # await asyncio.sleep(1)

    async def consumer_rabbitmq(self):
        """
        消费者方法，接收并处理消息
        """
        async with self.pool.acquire() as connection:
            async with connection.channel() as channel:
                # 设置每次最多接收的消息数量
                await channel.set_qos(prefetch_count=self.__PREFETCH_COUNT)

                # 获取交换机和队列
                _, queue = await self.setup_exchange_and_queue(channel)
                # print(f"Queue '{self.queue_name}' is bound to exchange '{self.exchange_name}' with routing_key '{self.routing_key}'")

                # 设置消费者回调
                await queue.consume(self.process_message)

                # print(f" [*] Waiting for messages. To exit press CTRL+C")
                await asyncio.Future()  # 保持事件循环运行，直到手动停止

    async def close(self):
        """
        关闭连接池
        """
        await self.pool.close()


if __name__ == '__main__':
    # 配置和运行
    async def main():
        # 配置 RabbitMQ 实例
        rabbitmq = PriorityMq(
            amqp_url="amqp://user:password@10.10.101.183/",
            exchange_name="my_exchange",
            queue_name="hello",
            routing_key="hello",
            max_pool_size=10
        )

        # 启动生产者，发送消息
        for i in range(10):
            await rabbitmq.producer_mes("Hello, RabbitMQ!")

        # 启动消费者
        consumer_task = asyncio.create_task(rabbitmq.consumer_rabbitmq())

        # 运行消费者事件循环
        await consumer_task


    asyncio.run(main())
