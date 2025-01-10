# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2024/12/31 16:38
# @Version: 1.0.0
# @Description: ''
from pathlib import Path
from string import Template
from hunterx.commands.config import green_text, blue_text, reset_all


class CompleteTemplate:

    # 查找项目模版根目录文件夹）
    @staticmethod
    def get_template_path(*sub_dirs):
        """
        :param sub_dirs: 包含的层级目录名称
        :return: 完整的目录路径
        """
        current_dir = Path(__file__).resolve().parent
        templates_base_dir = current_dir.parent / 'templates'
        return templates_base_dir / Path(*sub_dirs)

    @staticmethod
    def get_spider_tmpl(kernel: str):
        """
        :param kernel: 内核类型
        :return: 对应的爬虫模版
        """
        # 获取爬虫根目录
        spider_root = CompleteTemplate.get_template_path('spiders')

        tmpl_map = {
            'Manager': 'rabbitmq_spider.tmpl',
            'ManagerRedis': 'redis_spider.tmpl',
            'ManagerMemory': 'memory_spider.tmpl'
        }

        tmpl_path = f'{spider_root}/{tmpl_map[kernel]}'

        # 读取模板文件
        spider_template = tmpl_path
        with open(spider_template, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 创建 Template 对象
        template = Template(template_content)

        return template

    @staticmethod
    def get_pipelines_tmpl():
        """
        :return: pipelines模版
        """
        # 获取项目根目录
        project_root = CompleteTemplate.get_template_path('project')

        tmpl_path = project_root / 'pipelines.py.tmpl'

        # 读取模板文件
        spider_template = tmpl_path
        with open(spider_template, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 创建 Template 对象
        template = Template(template_content)

        return template

    @staticmethod
    def get_middleware_tmpl():
        """
        :return: middlewares模版
        """
        # 获取项目根目录
        project_root = CompleteTemplate.get_template_path('project')

        tmpl_path = project_root / 'middlewares.py.tmpl'

        # 读取模板文件
        spider_template = tmpl_path
        with open(spider_template, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 创建 Template 对象
        template = Template(template_content)

        return template

    @staticmethod
    def get_item_tmpl():
        """
        :return: middlewares模版
        """
        # 获取项目根目录
        project_root = CompleteTemplate.get_template_path('project')

        tmpl_path = project_root / 'items.py.tmpl'

        # 读取模板文件
        spider_template = tmpl_path
        with open(spider_template, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 创建 Template 对象
        template = Template(template_content)

        return template

    # 定义项目结构，文件名为键，文件内容为值
    @staticmethod
    def create_project_structure(
            project_name: str,
            spider_name: str,
            spider_model: str,
            pipelines_model: str,
            middlewares_model: str,
            items_model: str,
    ):
        """
        :params project_name: 项目名称
        :params spider_name: 爬虫名称
        :params spider_model: 爬虫模版
        """
        # 获取项目根目录
        project_root = CompleteTemplate.get_template_path('project')

        # 项目结构定义
        structure = {
            "": [
                {"file_name": "generator.py", 'template_path': f'{project_root}/generator.py.tmpl'},
                {"file_name": "__init__.py"},
                {"file_name": "items.py", 'template': items_model},
                {"file_name": "middleware.py", 'template': middlewares_model},
                {"file_name": "pipelines.py", 'template': pipelines_model},
                {"file_name": "settings.py", 'template_path': f'{project_root}/settings.py.tmpl'}
            ],
            "spiders": [
                {"file_name": "__init__.py"},
                {"file_name": "first_spider.py" if not spider_name else f'{spider_name}.py',
                 'template': spider_model},
            ]
        }

        # 创建文件夹和文件
        for folder, files in structure.items():
            folder_path = Path(project_name) / folder if folder else Path(project_name)
            folder_path.mkdir(parents=True, exist_ok=True)  # 创建目录（如果已存在则忽略）

            for file in files:
                file_name = file.get("file_name")
                template_path = file.get("template_path")
                template = file.get("template", '')

                file_path = folder_path / file_name

                # 如果提供了模板路径，优先读取模板内容
                if template_path and Path(template_path).is_file():
                    with open(template_path, "r", encoding='utf-8') as template_file:
                        content = template_file.read()

                    with open(file_path, "w", encoding='utf-8') as f:
                        f.write(content)  # 写入文件内容
                else:
                    with open(file_path, "w", encoding='utf-8') as f:
                        f.write(template)  # 写入文件内容

                print(f"{blue_text}Created file: {green_text}{file_path}{reset_all}")

        print(f"{blue_text}Project structure created at: {green_text}{Path(project_name).resolve()}{reset_all}")
