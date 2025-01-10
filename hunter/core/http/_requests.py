# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/2 15:44
# @Version: 1.0.0
# @Description: '请求方法'
import aiohttp
from .make_args import MakeArgs
from curl_cffi.requests import AsyncSession


import async_timeout
import httpx
from yarl import URL

class AsyncRequest:

    @staticmethod
    async def httpx_fun(
            method: str,
            url: str,
            headers: dict,
            timeout: int,
            is_encode: bool,
            is_file: bool,
            stream: bool,
            file_path: str = '',
            chunk_size: int = 10 * 1024 * 1024,
            http2: bool = False,
            **kwargs
    ):
        """
        使用 httpx 发送异步请求，支持文件下载、流式处理等功能。

        :param method: 请求方法 (GET, POST, etc.)
        :param url: 请求 URL
        :param headers: 请求头
        :param timeout: 超时时间
        :param is_encode: 是否对 URL 进行编码
        :param is_file: 是否为文件下载
        :param stream: 是否开启流模式
        :param file_path: 文件保存路径
        :param chunk_size: 文件块大小
        :param http2: 是否启用 HTTP/2
        :param kwargs: 额外参数 (proxy, verify_ssl, follow_redirects 等)
        """
        # 提取额外参数
        proxy = kwargs.pop('proxy', None)
        verify = kwargs.pop('verify_ssl', True)
        follow_redirects = kwargs.pop('follow_redirects', True)

        # 设置超时时间
        async with async_timeout.timeout(timeout):
            async with httpx.AsyncClient(http2=http2, headers=headers, proxies=proxy, verify=verify,
                                         timeout=timeout) as client:
                # 文件下载与流式处理
                if is_file and stream:
                    return await AsyncRequest.handle_stream_download(client, method, url, headers, is_encode, follow_redirects,
                                                        file_path, chunk_size, **kwargs)
                else:
                    # 普通请求
                    response = await client.request(
                        method=method,
                        url=URL(url, encoded=True) if is_encode else url,
                        headers=headers,
                        follow_redirects=follow_redirects,
                        **kwargs
                    )
                    return {'response': response, 'content': response.content}

    @staticmethod
    async def handle_httpx_download( client, method: str, url: str, headers: dict, is_encode: bool,follow_redirects: bool,
            file_path: str, chunk_size: int, **kwargs
    ):
        """
        处理文件下载和流式响应。

        :param client: httpx.AsyncClient 实例
        :param method: 请求方法
        :param url: 请求 URL
        :param headers: 请求头
        :param is_encode: 是否对 URL 进行编码
        :param follow_redirects: 是否跟随重定向
        :param file_path: 文件保存路径
        :param chunk_size: 每块数据的大小
        :param kwargs: 额外参数
        """
        async with client.stream(
            method=method,
            url=URL(url, encoded=True) if is_encode else url,
            headers=headers,
            follow_redirects=follow_redirects,
            **kwargs
        ) as response:
            try:
                response.raise_for_status()
                if file_path:
                    # 文件写入到指定路径
                    with open(file_path, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size):
                            f.write(chunk)
                    return {'response': response, 'content': None}
                else:
                    # 不保存文件，返回流对象
                    return {'response': response, 'content': response}
            except httpx.HTTPStatusError as e:
                return {'response': response, 'error': str(e)}

    @staticmethod
    async def aiohttp_fun(
            method: str,
            url: str,
            headers: dict,
            timeout: int,
            cookies: dict = None,
            is_encode: bool = True,
            is_file: bool = False,
            stream: bool = False,
            file_path: str = '',
            chunk_size: int = 10 * 1024 * 1024,
            **kwargs
    ):
        """
        使用 aiohttp 发送异步请求，支持文件下载、流式处理等功能。

        :param method: 请求方法 (GET, POST, etc.)
        :param url: 请求 URL
        :param headers: 请求头
        :param timeout: 超时时间
        :param cookies: 请求 Cookies
        :param is_encode: 是否对 URL 进行编码
        :param is_file: 是否为文件下载
        :param stream: 是否开启流模式
        :param file_path: 文件保存路径
        :param chunk_size: 文件块大小
        :param kwargs: 额外参数
        """
        # 配置 aiohttp 会话
        connector = aiohttp.TCPConnector(verify_ssl=False, limit=25)
        async with async_timeout.timeout(timeout):
            async with aiohttp.ClientSession(
                    connector=connector,
                    trust_env=True,
                    headers=headers,
                    cookies=cookies,
                    conn_timeout=timeout
            ) as session:
                # 发起请求
                async with session.request(
                        method=method,
                        url=URL(url, encoded=True) if is_encode else url,
                        **kwargs
                ) as response:
                    if is_file and stream:
                        # 流式处理文件下载
                        return await AsyncRequest.handle_aiohttp_download(response, file_path, chunk_size)
                    else:
                        # 普通请求
                        content = await response.read()
                        return {'response': response, 'content': content}

    @staticmethod
    async def handle_aiohttp_download(response: aiohttp.ClientResponse, file_path: str, chunk_size: int):
        """
        处理文件下载和流式响应。

        :param response: aiohttp 的响应对象
        :param file_path: 文件保存路径
        :param chunk_size: 每块数据的大小
        """
        try:
            response.raise_for_status()
            if file_path:
                # 将流式内容写入文件
                with open(file_path, 'wb') as file:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        file.write(chunk)
                return {'response': response, 'content': None}
            else:
                # 不保存文件，返回完整响应
                return {'response': response, 'content': response.content}
        except aiohttp.ClientResponseError as e:
            return {'response': response, 'error': str(e)}

    @staticmethod
    async def asyn_request(
            method: str,
            url: str,
            headers: dict,
            timeout: int,
            cookies: dict = None,
            is_encode: bool = True,
            is_httpx: bool = False,
            is_TLS: bool = False,
            is_file: bool = True,
            stream: bool = False,
            file_path: str = '',
            chunk_size: int = 10 * 1024 * 1024,
            http2: bool = False,
            **kwargs
    ):
        """
        异步请求方法，支持多种 HTTP 客户端。

        :param method: 请求方法 (GET, POST, etc.)
        :param url: 请求 URL
        :param headers: 请求头
        :param timeout: 超时时间
        :param cookies: 请求 Cookies
        :param is_encode: 是否对 URL 进行编码
        :param is_httpx: 是否使用 httpx 作为客户端
        :param is_TLS: 是否使用 TLS 连接
        :param is_file: 是否为文件下载
        :param stream: 是否开启流模式
        :param file_path: 文件保存路径
        :param chunk_size: 文件块大小
        :param http2: 是否启用 HTTP/2
        :param kwargs: 额外参数
        """
        kwargs = await MakeArgs.get_kwargs(is_httpx, is_TLS, **kwargs)

        if is_httpx:
            async for response in AsyncRequest._handle_httpx_request(
                method, url, headers, timeout, is_encode, is_file, stream, file_path, chunk_size, http2, **kwargs
            ):
                yield response
        elif is_TLS:
            async for response in AsyncRequest._handle_tls_request(
                method, url, timeout, is_encode, **kwargs
            ):
                yield response
        else:
            async for response in AsyncRequest._handle_aiohttp_request(
                method, url, headers, timeout, cookies, is_encode, is_file, stream, file_path, chunk_size, **kwargs
            ):
                yield response

    @staticmethod
    async def _handle_httpx_request(
        method: str, url: str, headers: dict, timeout: int, is_encode: bool,
        is_file: bool, stream: bool, file_path: str, chunk_size: int, http2: bool, **kwargs
    ):
        """
        使用 httpx 处理请求。
        """
        response_iter = await AsyncRequest.httpx_fun(
            method=method, url=url, headers=headers, timeout=timeout, is_encode=is_encode,
            is_file=is_file, stream=stream, file_path=file_path, chunk_size=chunk_size,
            http2=http2, **kwargs
        )
        yield response_iter

    @staticmethod
    async def _handle_tls_request(
        method: str, url: str, timeout: int, is_encode: bool, **kwargs
    ):
        """
        使用 TLS 处理请求。
        """
        verify = kwargs.get('verify')
        async with async_timeout.timeout(timeout):
            async with AsyncSession(verify=verify) as session:
                response = await session.request(
                    method=method,
                    url=URL(url, encoded=True) if is_encode else url,
                    **kwargs
                )
                yield {'response': response, 'content': response.content}

    @staticmethod
    async def _handle_aiohttp_request(
        method: str, url: str, headers: dict, timeout: int, cookies: dict, is_encode: bool,
        is_file: bool, stream: bool, file_path: str, chunk_size: int, **kwargs
    ):
        """
        使用 aiohttp 处理请求。
        """
        response_iter = await AsyncRequest.aiohttp_fun(
            method=method, url=url, headers=headers, timeout=timeout, cookies=cookies,
            is_encode=is_encode, is_file=is_file, stream=stream, file_path=file_path,
            chunk_size=chunk_size, **kwargs
        )
        yield response_iter

    @staticmethod
    async def iter_chunked(response, is_httpx, chunk_size):
        if is_httpx:
            async for chunk in response.aiter_bytes(chunk_size):  # chunk_size 是块大小，可以根据需要调整
                yield chunk
        else:
            async for chunk in response.iter_chunked(chunk_size):  # chunk_size 是块大小，可以根据需要调整
                yield chunk
