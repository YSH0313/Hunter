# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/3 16:44
# @Version: 1.0.0
# @Description: ''
from threading import Lock


# 单例模式
class SingletonBase:
    _instance = None
    _lock = Lock()  # 确保线程安全

    def __new__(cls, *args, **kwargs):
        if not cls._instance:  # 如果实例不存在
            with cls._lock:  # 加锁，保证线程安全
                if not cls._instance:  # 双重检查
                    cls._instance = super().__new__(cls)
        return cls._instance

    # def __init__(self):
    #     super().__init__()
    #     if getattr(self, "_initialized", False):  # 避免重复初始化
    #         return
    #     self._initialized = True
