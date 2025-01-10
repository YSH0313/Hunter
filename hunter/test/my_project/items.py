# -*- coding: utf-8 -*-
# @Description: 自定义item类
# Define here the models for your scraped items
from hunter.items.baseitem import Item, dataclass, field


@dataclass
class MyProjectItem(Item):
    name: str = field(default="")
