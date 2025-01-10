# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/6 18:43
# @Version: 1.0.0
# @Description: ''
import sys
import importlib.util
from pathlib import Path
from typing import Optional

from hunterx.piplines.basepipeline import Pipeline


def get_pipeline_root(current_path: Optional[Path] = None):
    """获取项目根目录"""
    while current_path != current_path.parent:  # 一直递归到根目录
        if (current_path / 'pipelines.py').exists():  # 如果标志文件存在
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(f"Could not find 'pipelines.py' in any parent directories.")


def load_pipelines(pipelines_setting: Optional[dict] = None):
    """
    动态加载 pipelines.py 中的所有管道类
    :param pipeline_path: 管道脚本文件的路径
    """
    if pipelines_setting:
        # 获取项目根目录
        script_path = Path(sys.argv[0]).resolve()

        project_root = get_pipeline_root(script_path)

        # 动态加载 pipelines.py
        pipeline_file = project_root / 'pipelines.py'

        # 获取文件的绝对路径
        pipeline_path = Path(pipeline_file)

        # 判断路径是否存在
        if not pipeline_path.is_file():
            raise FileNotFoundError(f"{pipeline_path} does not exist")

        # 使用 importlib 加载模块
        spec = importlib.util.spec_from_file_location("pipeline", str(pipeline_path))
        pipeline_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pipeline_module)

        # 返回模块中的所有管道类
        pipelines = {}
        for name, obj in pipeline_module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, Pipeline) and obj is not Pipeline:  # 检查是否为继承自 Middleware 的类
                pipelines[name] = obj

        # 按优先级排序（数字越小优先级越高）
        sorted_pipelines = sorted(pipelines_setting.items(), key=lambda x: x[1])

        # 转换为排序后的 管道 列表
        ordered_pipelines = [pipelines[pipeline[0]] for pipeline in sorted_pipelines]

        return ordered_pipelines
