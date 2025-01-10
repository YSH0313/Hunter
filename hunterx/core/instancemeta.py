# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/7 12:05
# @Version: 1.0.0
# @Description: ''
from typing import Optional

from hunterx.utils.log import LogCaptor
from hunterx.utils.reload_settings import SettingsManager
from hunterx.piplines.pipeline_loader import load_pipelines


class InstanceMeta(type):

    def __call__(cls, *args, **kwargs):
        # # 检查是否已经存在实例，如果有则返回该实例
        # if not hasattr(cls, '_instance'):
        # 创建实例
        instance = super().__call__(*args, **kwargs)

        # 遍历 MRO，自动调用每个父类的 __init__ 方法
        for base in list(reversed(cls.__mro__))[:-1]:  # 排除当前类
            init = getattr(base, "__init__", None)
            if callable(init):
                # 使用元类来调用父类的初始化方法，传递实例和参数
                init(instance, *args, **kwargs)

            # # 将实例保存在 _instance 属性中，保证单例模式
            # cls._instance = instance
        return instance


class Base(metaclass=InstanceMeta):
    name: Optional[str] = None
    custom_settings: Optional[dict] = None

    def __init__(self, *args, **kwargs):
        # 传递 custom_settings 给 SettingsManager
        self.__settings_manager = SettingsManager(custom_settings=self.custom_settings)
        # 获取设置
        self._settings = self.__settings_manager.get_settings()

        LogCaptor()

        self.callback_map = {}  # 回调函数优先级map表

        self.__ITEM_PIPELINES = self._settings.ITEM_PIPELINES
        self.pipelines = load_pipelines(self.__ITEM_PIPELINES) or None

        self.request_count = 0
        self.success_code_count = 0
        self.wrong_count = 0
        self.giveup_count = 0
        self.exc_count = 0
        self.other_count = 0
