# -*- coding: utf-8 -*-
import hunterx
from hunterx.spiders import RedisSpider


class ThirdSpiderSpider(RedisSpider):
    name = 'second_spider'
    custom_settings = {
        'WATTING_TIME': 20,
        'REDIS_HOST_LISTS': [{'localhost': 6379}],  # 主机名
        'REDIS_ACCOUNT': {
            'username': '',
            'password': ''
        },  # 单机情况下,密码没有的不设置
        'REDIS_ENABLED': True,  # 是否开启redis连接
        'FILTER': False  # 是否去重
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
    start_run = ThirdSpiderSpider()
    start_run.run()
