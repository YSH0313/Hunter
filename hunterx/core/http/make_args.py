# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/2 10:28
# @Version: 1.0.0
# @Description: '获取和规范请求参数'
import json
import re
from hunterx.utils.single_tool import is_json, deal_re
from hunterx.core.data_class.data_class import RequestParams

class MakeArgs(object):

    def handle(self, obj: dict):
        """处理特殊meta参数"""
        item_name = obj.get('item_name')
        if item_name:
            del obj['item_name']
            item = globals()[item_name]()
            for k, v in obj.items():
                if hasattr(item, k):
                    setattr(item, k, v)
                else:
                    raise AttributeError(f'{item_name} has no attribute {k}')
            return item
        else:
            return obj

    @staticmethod
    def make_params(task: json, agent_whitelist: list, is_proxy: bool, is_sameip: bool, ua_proxy: bool, time_out: int):
        """获取并处理有关的参数"""
        contents = json.loads(task)
        callback = contents.get('callback')
        is_encode = contents.get('is_encode')
        url = contents.get('url')
        headers = contents.get('headers')
        params = contents.get('params')
        data = contents.get('data')
        json_params = contents.get('json_params')
        cookies = contents.get('cookies')
        timeout = contents.get('timeout')
        dont_filter = contents.get('dont_filter')
        encoding = contents.get('encoding')
        meta = contents.get('meta')
        for k, v in meta.items():
            if is_json(v) and not isinstance(v, dict):
                meta[k] = json.loads(v, object_hook=MakeArgs.handle)
        level = contents.get('level')
        proxy = contents.get('proxy')
        meta['proxy'] = proxy if proxy and is_sameip else meta.get('proxy')
        verify_ssl = contents.get('verify_ssl')
        allow_redirects = contents.get('allow_redirects')
        is_httpx = contents.get('is_httpx')
        is_TLS = contents.get('is_TLS')
        is_file = contents.get('is_file')
        stream = contents.get('stream')
        file_path = contents.get('file_path')
        chunk_size = contents.get('chunk_size')
        http2 = contents.get('http2')
        retry_count = contents.get('retry_count')
        is_change = contents.get('is_change')
        param = meta, meta.get('proxy') if (meta if meta else {}) else proxy
        meta = param[0]
        proxy = param[1] if meta.get('proxy') else proxy
        ignore_ip = contents.get('ignore_ip')
        methods = contents.get('method')
        timeout = timeout if timeout else time_out
        return {
            'method': methods, 'is_encode': is_encode, 'url': url, 'task': contents, 'headers': headers,
            'params': params, 'data': data, 'json_params': json_params, 'cookies': cookies, 'timeout': timeout,
            'callback': callback, 'dont_filter': dont_filter, 'encoding': encoding, 'meta': meta, 'level': level,
            'proxy': proxy, 'verify_ssl': verify_ssl, 'is_httpx': is_httpx, 'is_TLS': is_TLS, 'is_file': is_file,
            'stream': stream, 'file_path': file_path, 'chunk_size': chunk_size, 'http2': http2,
            'retry_count': retry_count, 'is_change': is_change, 'allow_redirects': allow_redirects,
            'ignore_ip': ignore_ip, 'request_info': task, 'Agent_whitelist': agent_whitelist, 'IS_PROXY': is_proxy,
            'IS_SAMEIP': is_sameip, 'UA_PROXY': ua_proxy
        }


    @staticmethod
    async def get_kwargs(is_httpx=False, is_TLS=False, **kwargs):
        if is_httpx:
            proxy = kwargs.get('proxy')
            verify = kwargs.get('verify_ssl')
            follow_redirects = kwargs.get('allow_redirects')
            del kwargs['allow_redirects']
            kwargs['proxy'] = {"all://": proxy} if proxy else None
            kwargs['verify'] = verify
            kwargs['follow_redirects'] = follow_redirects
            return kwargs
        elif is_TLS:
            proxy = kwargs.get('proxy')
            verify = kwargs.get('verify_ssl')
            del kwargs['verify_ssl']
            del kwargs['proxy']
            ip = deal_re(re.search('//(.*)', proxy, re.S)) if proxy else None
            kwargs['proxies'] = {"https": ip, "http": ip} if ip else None
            kwargs['verify'] = verify
            return kwargs
        return kwargs

    # @staticmethod
    # async def request_preprocess(task, url, is_change, meta, headers, agent_whitelist, is_proxy, is_sameip, ua_proxy):
    #     """请求预处理"""
    #     proxy = None
    #     is_proxy = True if url not in agent_whitelist and is_proxy else False
    #     if is_proxy and ((proxy == None) or (is_change)):
    #         proxy = await asy_rand_choi_pool()
    #         if is_sameip:
    #             meta['proxy'] = proxy
    #             task['meta']['proxy'] = proxy
    #     if isinstance(headers, dict) and ua_proxy:
    #         headers['User-Agent'] = await get_ua()
    #     return task, proxy, headers, meta, is_proxy

    @staticmethod
    async def request_preprocess(request_params: RequestParams, agent_whitelist, is_proxy, is_same_ip, ua_proxy):
        # 调用 RequestParams 的异步方法
        await request_params.preprocess(agent_whitelist, is_proxy, is_same_ip, ua_proxy)
