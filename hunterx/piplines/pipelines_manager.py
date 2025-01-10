# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/6 18:44
# @Version: 1.0.0
# @Description: ''
from typing import Optional, List

from hunterx.piplines.basepipeline import Pipeline
from hunterx.items.baseitem import Item


class PipelineManager:
    def __init__(self, pipelines: Optional[List[Pipeline]] = None):
        """
        初始化 管道 管理器。

        :param pipelines: 一个中间件列表，每个管道必须继承 Pipeline
        """
        self.pipelines = pipelines

        # 缓存已实例化的管道
        self.pipeline_instances = {}

    async def handle_process_item(self, item: Item, spider):
        """
        按顺序处理所有中间件的 process_item。
        如果管道是单例，则直接调用实例。
        """
        if self.pipelines:
            for pipeline_class in self.pipelines:
                # 检查管道实例是否已经创建，若没有则实例化并缓存
                if pipeline_class not in self.pipeline_instances:
                    self.pipeline_instances[pipeline_class] = pipeline_class()

                # 获取实例并调用 process_item 方法
                pipeline_instance = self.pipeline_instances[pipeline_class]
                await pipeline_instance.process_item(item, spider)
