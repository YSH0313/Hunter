# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2020-02-23 09:56:50
# @Version: 1.0.0
# @Description: ip代理
import os

# os.environ.setdefault('AIOHTTP_NO_EXTENSIONS', '1')
import aiohttp
import json
import random
import time

ip_lists = []
update = time.time()
url = ''


async def deal_json(response):
    ippool = json.loads(response)['http']
    ip_lists.append(ippool)


async def asy_rand_choi_pool_response():  # 适用于aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=url)
            res = await response.read()
            return res.decode('utf-8')
    except aiohttp.InvalidURL:
        return 'InvalidURL please check your url.'
    except Exception as e:
        return False


async def asy_rand_choi_pool():
    global ip_lists
    global update
    if (len(ip_lists) == 0) or (time.time() - update >= 60):
        response = await asy_rand_choi_pool_response()
        if response != 'InvalidURL please check your url.':
            while response == False:
                response = await asy_rand_choi_pool_response()
            try:
                await deal_json(response=response)
            except:
                while len(ip_lists) == 0:
                    try:
                        response = await asy_rand_choi_pool_response()
                        await deal_json(response=response)
                    except:
                        ip_lists = ip_lists
    if len(ip_lists) != 0:
        proxy = ip_lists.pop()
        return proxy


async def get_ua():
    user_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
        'Opera/8.0 (Windows NT 5.1; U; en)',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) ',
    ]
    user_agent = random.choice(user_agents)  # random.choice(),从列表中随机抽取一个对象
    return user_agent
