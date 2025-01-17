# -*- coding: utf-8 -*-
import hunterx
from hunterx.spiders import MemorySpider


class ChildSpiderSpider(MemorySpider):
    name = 'child_spider'

    def __init__(self):
        super().__init__()
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }

    def start_requests(self):
        url = 'https://www.baidu.com/'
        yield hunterx.Requests(url=url, headers=self.header, callback=self.parse, level=1)

    async def parse(self, response):
        print(response.text)


if __name__ == '__main__':
    start_run = ChildSpiderSpider()
    start_run.run()
