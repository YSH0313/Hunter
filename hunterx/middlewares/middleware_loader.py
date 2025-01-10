# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/6 14:17
# @Version: 1.0.0
# @Description: ''
import sys
import importlib.util
from pathlib import Path
from typing import Optional

from hunterx.middlewares.middleware import Middleware, SpiderMiddleware, ProxyMiddleware, UaMiddleware


def get_middleware_root(current_path: Optional[Path] = None):
    """获取项目根目录"""
    while current_path != current_path.parent:  # 一直递归到根目录
        if (current_path / 'middleware.py').exists():  # 如果标志文件存在
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(f"Could not find 'middleware.py' in any parent directories.")


def get_middleware_module():
    """
    获取middleware模块的所有中间件
    """
    # 获取项目根目录
    script_path = Path(sys.argv[0]).resolve()

    project_root = get_middleware_root(script_path)

    # 动态加载 middleware.py
    middleware_file = project_root / 'middleware.py'

    # 获取文件的绝对路径
    middleware_path = Path(middleware_file)

    # 判断路径是否存在
    if not middleware_path.is_file():
        raise FileNotFoundError(f"{middleware_path} does not exist")

    # 使用 importlib 加载模块
    spec = importlib.util.spec_from_file_location("middleware", str(middleware_path))
    middleware_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(middleware_module)
    return middleware_module


def load_middlewares(middlewares_setting: Optional[dict] = None):
    """
    动态加载 middleware.py 中的所有中间件类
    :param middleware_path: 中间件脚本文件的路径
    """
    if middlewares_setting:
        middleware_module = get_middleware_module()

        # 按优先级排序（数字越小优先级越高）
        sorted_middlewares = sorted(middlewares_setting.items(), key=lambda x: x[1])

        if not hasattr(middleware_module, 'SpiderMiddleware'):
            middleware_module.__setattr__('SpiderMiddleware', SpiderMiddleware)  # 添加默认的爬虫中间件
            sorted_middlewares.append(('SpiderMiddleware', ''))  # 把默认的爬虫中间件添加到列表末尾

        if not hasattr(middleware_module, 'ProxyMiddleware'):
            middleware_module.__setattr__('ProxyMiddleware', ProxyMiddleware)  # 添加默认的代理中间件
            sorted_middlewares.append(('ProxyMiddleware', ''))  # 把默认的代理中间件添加到列表末尾

        if not hasattr(middleware_module, 'UaMiddleware'):
            middleware_module.__setattr__('UaMiddleware', UaMiddleware)  # 添加默认的随机ua头中间件
            sorted_middlewares.append(('UaMiddleware', ''))  # 把默认的随机ua头中间件添加到列表末尾

        # 返回模块中的所有中间件类
        middlewares = {}
        for name, obj in middleware_module.__dict__.items():
            # 检查是否为继承自 Middleware 的类
            if isinstance(obj, type) and issubclass(obj, Middleware) and obj is not Middleware:
                middlewares[name] = obj

        # 转换为排序后的 中间件 列表
        ordered_middlewares = [middlewares[middleware[0]] for middleware in sorted_middlewares]

        return ordered_middlewares
