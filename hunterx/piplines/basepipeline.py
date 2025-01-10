# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/6 18:06
# @Version: 1.0.0
# @Description: ''
from typing import Any
from hunterx.items.baseitem import Item


class Pipeline:

    async def process_item(self, item: Item, spider) -> Any:
        """每个 pipeline 子类都需要实现此方法"""
        raise NotImplementedError("Pipeline must implement `process_item`.")
