# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/3 14:23
# @Version: 1.0.0
# @Description: ''
import sys
from pathlib import Path
from typing import Optional

from hunterx.commands.complete_template import CompleteTemplate
from hunterx.commands.config import red_text, green_text, blue_text, yellow_text, reset_all
from hunterx.commands.tools import re_name


def get_spider_path():
    gen_path = Path(sys.argv[0]).absolute()  # 生成器的路径
    # project_path = gen_path.parent  # 项目路径（无用，用做记录）
    spider_dir_path = gen_path.parent / 'spiders'  # 爬虫目录路径
    return spider_dir_path


def get_spider_file_path(
        spider_dir_path: Optional[Path] = None,
        spider_dir: Optional[str] = None,
        spider_name: Optional[str] = None):
    """
    :param spider_dir_path: 爬虫目录路径
    :param spider_dir: 爬虫文件分层目录
    :param spider_name: 爬虫文件名称
    :return: 爬虫文件完整路径
    """
    spider_file_path = spider_dir_path / f'{spider_name}.py'

    if spider_dir:
        spider_path = spider_dir_path / spider_dir
        spider_path.mkdir(exist_ok=True)
        spider_file_path = spider_path / f'{spider_name}.py'

    return spider_file_path


def get_kernel(kernel_code: Optional[int] = None):
    """
    :param kernel_code: 内核所对应的代码
    :return: 内核类型
    """
    if not kernel_code:
        raise ValueError('Kernel code must be provided')
    kernel_map = {
        1: 'Manager',
        2: 'ManagerRedis',
        3: 'ManagerMemory',
    }

    kernel = kernel_map.get(kernel_code)

    return kernel


def write_file(spider_file_path: Optional[Path] = None, spider_model: Optional[str] = None):
    """
    :param spider_file_path: 完整爬虫文件路径
    :param spider_model: 渲染完成的爬虫模版
    """
    with open(spider_file_path, "w", encoding='utf-8') as f:
        f.write(spider_model)  # 写入文件内容
    print(f"{blue_text}Spider created at: {green_text}{spider_file_path}{reset_all}")

def production(
        spider_dir: Optional[str] = None,
        spider_name: Optional[str] = None,
        kernel_code: Optional[int] = 3):
    """
    :param spider_dir: 爬虫分层目录名称
    :param spider_name: 爬虫名称
    :param kernel_code: 需要使用的核心引擎代码，默认为3使用内存作为优先级队列，1表示使用rabbitmq作为队列，2表示使用redis作为队列
    """

    spider_dir_path = get_spider_path()

    spider_file_path = get_spider_file_path(spider_dir_path, spider_dir, spider_name)

    if spider_file_path.exists():
        response = input(
            f"The crawler file named {green_text}{spider_name}{reset_all} already exists. Do you want to overwrite the write? (y/n): ").strip().lower() or 'n'

        # 输出用户选择的项目名称和任务名称
        if response == 'y':
            print(f'{yellow_text}Spider is overwriting old files.{reset_all}')
        else:
            print(f'{red_text}Spider creation was aborted.{reset_all}')
            return

    kernel = get_kernel(kernel_code)

    spider_template = CompleteTemplate.get_spider_tmpl(kernel)

    template_values = {
        'Class_name': re_name(spider_name),
        'spider_name': spider_name,
    }

    spider_model = spider_template.safe_substitute(template_values)

    write_file(spider_file_path, spider_model)


if __name__ == '__main__':
    production(spider_name='second_spider')
