# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/2 13:40
# @Version: 1.0.0
# @Description: ''
from dataclasses import dataclass, replace
from typing import Optional, Dict, Any, Callable, List
from hunterx.internet.proxys import asy_rand_choi_pool, get_ua


@dataclass
class RequestParams:
    method: str = 'GET'
    url: Optional[str] = None
    task: Optional[dict] = None
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    json_params: Optional[Dict[str, Any]] = None
    cookies: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    callback: Optional[Callable] = None
    dont_filter: bool = False
    encoding: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    level: int = 0
    request_info: Optional[Dict[str, Any]] = None
    proxy: Optional[str] = None
    verify_ssl: Optional[bool] = None
    allow_redirects: bool = True
    is_httpx: bool = False
    is_TLS: bool = False
    is_file: bool = False
    stream: bool = False
    file_path: str = ''
    chunk_size: int = 10
    http2: bool = False
    retry_count: int = 0
    is_change: bool = False
    is_encode: Optional[bool] = None
    ignore_ip: bool = False
    is_proxy: bool = False

    Agent_whitelist: Optional[List] = None
    IS_PROXY: bool = False
    IS_SAMEIP: bool = False
    UA_PROXY: bool = False

    async def preprocess(self, agent_whitelist, is_proxy, is_sameip, ua_proxy):
        """请求预处理"""
        proxy = None
        is_proxy = True if self.url not in agent_whitelist and is_proxy else False
        if is_proxy and ((proxy == None) or (self.is_change)):
            proxy = await asy_rand_choi_pool()
            if is_sameip:
                self.meta['proxy'] = proxy
                self.task['meta']['proxy'] = proxy
        if isinstance(self.headers, dict) and ua_proxy:
            self.headers['User-Agent'] = await get_ua()
