# -*- coding: utf-8 -*-
import hunterx
from hunterx.spiders import RabbitmqSpider


class SecondSpiderSpider(RabbitmqSpider):
    name = 'second_spider'
    custom_settings = {
        'WATTING_TIME': 20,
        'RABBITMQ_CONFIG': {
            'username': 'guest',
            'password': 'guest',
            'host': 'localhost',
            'port': 15672,
        },
        'X_MESSAGE_TTL': 86400000,
        'AUTO_CLEAR': True,  # 重启是否自动清空队列
        'ASYNC_PROD': True,  # 是否开启异步生产
        'MQ_ENABLED': True,  # 是否开启Rabbitmq连接'
    }

    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }

    def start_requests(self):
        url = 'https://www.baidu.com/'
        yield hunterx.Requests(url=url, headers=self.header, callback=self.parse, level=1)

    async def parse(self, response):
        print(f'parse {response.status_code}')


if __name__ == '__main__':
    start_run = SecondSpiderSpider()
    start_run.run()
