<h1 align="center">HunterX</h1>
<p align="center">
    <a href="https://www.python.org/">
        <img alt="Static Badge" src="https://img.shields.io/badge/build-%3E%3D3.11-brightgreen?logo=python&logoColor=appveyor&logoSize=violet&label=python&labelColor=abcdef&color=blue&cacheSeconds=3600">
    </a>
    <a href="https://github.com/YSH0313/Hunter/LICENSE">
        <img alt="GitHub License" src="https://img.shields.io/github/license/YSH0313/Hunter?logo=appveyor&logoColor=violet&logoSize=auto&label=license&labelColor=abcdef&color=green&cacheSeconds=3600">
    </a>
</p>

## 项目背景

这个项目为作者在工作学习中诞生的，一直以来作为本人的工作利器，经过多年的实战打磨，决定开源出来和大家一起学习进步，项目中也存在诸多可优化迭代的方向，期待和你一起完善。

## 项目简介

`HunterX` 是一款可以帮助你快速开发一个网络爬虫应用的一套异步并发框架，他提供了许多内置方法，
让你的开发代码更加的简洁，爬虫代码更加规范，方便维护，除此以外还可以多线程并发的做一些数据处理的工作，
更多功能请查看 [官方文档]() 或添加开发者的微信 `YSH026-`。

### [官方文档]()

## 快速开始

### 环境准备

- python3.11及以上版本

### 安装说明

执行以下命令安装hunterx

```bash
pip install hunterx
```

安装完成后执行以下命令

```bash
hunterx
```

成功执行后你将看到以下输出，输入和选择你的创建信息

- `ManagerRabbitmq`: 以 `rabbitmq` 作为优先级队列的爬虫任务。
- `ManagerRedis`: 以 `redis` 作为优先级队列的爬虫任务。
- `ManagerMemory`: 以 `内存` 作为优先级队列的爬虫任务。

```text
? You are about to create a new project. Please follow the prompts to fill in the information. Yes
? 📁Enter the project name for your project: my_project
? 💡Enter the task name for the project: first_spider
? ⚙️Please select a kernel: 
  ManagerRabbitmq
  ManagerRedis
❯ ManagerMemory
```

```text
? You are about to create a new project. Please follow the prompts to fill in the information. Yes
? 📁Enter the project name for your project: my_project
? 💡Enter the task name for the project: first_spider
? ⚙️Please select a kernel: ManagerMemory
The project name is: my_project.
The task name is: first_spider.
The selected kernel is: ManagerMemory.
Created file: my_project/generator.py
Created file: my_project/__init__.py
Created file: my_project/items.py
Created file: my_project/middleware.py
Created file: my_project/pipelines.py
Created file: my_project/settings.py
Created file: my_project/spiders/__init__.py
Created file: my_project/spiders/first_spider.py
Project structure created at: /your_path/my_project
```

将创建完成后项目根目录下的 `settings.py` 文件中的各项配置改为自己配置信息

### 项目结构

```text
my_project
    ├── spiders
    │    ├── __init__.py
    │    └── first_spider.py
    ├── __init__.py
    ├── generator.py
    ├── items.py
    ├── middleware.py
    ├── pipelines.py
    └── settings.py
```

### 测试运行

- 使用命令行

```bash
cd my_project/spiders
python first_spider.py
```

- 使用IDE

执行 `spiders` 文件夹下的 `first_spider.py`

### 创建爬虫

- 打开 `generator.py` 文件，根据里面的提示填写信息，完成后运行即可创建

#### 示例：

```python
from hunterx.utils.generator import production

# spider_dir: 爬虫分层目录名称（路径不存在时会自动创建，无需手动创建目录）
# spider_name: 创建的爬虫名称
# kernel_code: 需要使用的核心引擎 默认优先使用内存优先级队列，默认为3(内存队列)，1为rabbitmq队列，2为redis队列
production(spider_name='second_spider', kernel_code=3)
```

执行后你将在 `spiders` 目录下看到刚才创建的名为 `second_spider` 的爬虫文件

### item配置

打开 `items.py` 文件，您应该可以看到以下内容

```python
# -*- coding: utf-8 -*-
# @Description: 自定义item类
# Define here the models for your scraped items
from hunterx.items.baseitem import Item, dataclass, field


@dataclass
class MyProjectItem(Item):
    # name: str = field(default="")
    pass
```

那么你可以根据示例 `name: str = field(default="")` 继续创建更多字段，注意要设置好字段类型

接下来你可以在爬虫中这样使用

```python
# -*- coding: utf-8 -*-
import hunterx
from hunterx.spiders import MemorySpider
from items import MyProjectItem


class FirstSpiderSpider(MemorySpider):
    name = 'first_spider'

    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }

    def start_requests(self):
        url = 'https://www.example.com/'
        yield hunterx.Requests(url=url, headers=self.header, callback=self.parse, level=1)

    async def parse(self, response):
        item = MyProjectItem()
        item.name = 'hunterx'
        yield item


if __name__ == '__main__':
    start_run = FirstSpiderSpider()
    start_run.run()

```

这样在执行后设置的字段就可以被正确的赋值了，接下来可以使用管道 `pipelines.py` 中进行下一步的处理

### pipline配置

打开 `pipelines.py` 文件，你应该可以看到以下内容

```python
from hunterx.piplines.basepipeline import Pipeline
from hunterx.test.my_project.items import MyProjectItem


class MyProjectPipeline(Pipeline):

    async def process_item(self, item, spider):
        if isinstance(item, MyProjectItem):
            print(item)
            print(spider.name)
```

在这里可以获取到在 `items.py` 中设置的字段的值，你可以在这里进一步的对数据进行处理，当然这需要爬虫中正确调用并传递。

以上就是一个快速简单的使用案例，更多使用技巧请查看 [官方文档]()

## License

[MIT](/LICENSE)
