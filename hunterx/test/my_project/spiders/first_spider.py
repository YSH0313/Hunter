# -*- coding: utf-8 -*-
import hunterx
from hunterx.spiders import MemorySpider
from hunterx.test.my_project.items import MyProjectItem


class FirstSpiderSpider(MemorySpider):
    name = 'first_spider'
    custom_settings = {
        'PREFETCH_COUNT': 23,
        'WAITTING_TIME': 10,
        'UA_PROXY': True,
        'MYSQL_CONFIG': {
            'MYSQL_HOST': 'localhost',
            'MYSQL_DBNAME': 'spider_frame',
            'MYSQL_USER': 'root',
            'MYSQL_PASSWORD': 'password',
            'PORT': 3306
        },
        'MYSQL_ENABLED': False,
    }

    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }

    def start_requests(self):
        url = 'https://www.baidu.com/'
        yield hunterx.Requests(url=url, headers=self.header, callback=self.parse, level=1)

    async def parse(self, response):
        print(response.status_code)
        item = MyProjectItem()
        item.name = 'hunterx'
        yield item


if __name__ == '__main__':
    start_run = FirstSpiderSpider()
    start_run.run()
