# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2024/12/31 20:08
# @Version: 1.0.0
# @Description: ''
# import sys
# import importlib.util
# from pathlib import Path
# from typing import Optional
# from dotmap import DotMap
#
#
# def load_settings(settings_file: Path):
#     """动态加载 settings 模块"""
#     # 确保文件存在
#     if not settings_file.is_file():
#         raise FileNotFoundError(f"Settings file '{settings_file}' not found!")
#
#     # 加载模块
#     spec = importlib.util.spec_from_file_location("settings", str(settings_file))
#     settings = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(settings)
#
#     return settings
#
#
# def get_all_settings(settings):
#     """获取 settings 中的所有参数并返回为字典"""
#     return {key: value for key, value in vars(settings).items() if not key.startswith("__")}
#
#
# def get_setting(settings, setting_name, default=None):
#     """获取设置项，若不存在则返回默认值"""
#     return getattr(settings, setting_name, default)
#
#
# def update_settings(settings, custom_settings: Optional[dict] = None):
#     settings.update(custom_settings)
#     return settings
#
# def get_setting_root(current_path: Optional[Path] = None):
#     while current_path != current_path.parent:  # 一直递归到根目录
#         if (current_path / 'settings.py').exists():  # 如果标志文件存在
#             return current_path
#         current_path = current_path.parent
#     raise FileNotFoundError(f"Could not find 'settings.py' in any parent directories.")
#
# def final_settings(custom_settings: Optional[dict] = None):
#     # 获取项目根目录
#     script_path = Path(sys.argv[0]).resolve()
#     # project_root = script_path.parent.parent  # 较为死板，暂时放弃
#
#     project_root = get_setting_root(script_path)
#
#     # 动态加载 settings.py
#     settings_file = project_root / 'settings.py'
#     try:
#         settings = load_settings(settings_file)
#     except Exception as e:
#         print(f"Error loading settings: {e}")
#         return
#
#     # 获取所有设置项
#     settings = get_all_settings(settings)
#
#     if custom_settings:
#         settings = update_settings(settings, custom_settings)
#
#     # 获取设置项
#     # PREFETCH_COUNT = get_setting(settings, 'PREFETCH_COUNT', None)
#     settings = DotMap(settings)
#     return settings
#
#
# if __name__ == "__main__":
#     final_settings()



import sys
import importlib.util
from pathlib import Path
from typing import Optional
from dotmap import DotMap

class SettingsManager:
    _instance = None
    _settings = None

    def __new__(cls, custom_settings: Optional[dict] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(custom_settings)
        # if custom_settings is not None:
        #     cls._instance._initialize(custom_settings)
        return cls._instance

    def _initialize(self, custom_settings: Optional[dict]):
        """初始化设置"""
        # 获取项目根目录
        script_path = Path(sys.argv[0]).resolve()

        project_root = self.get_setting_root(script_path)

        # 动态加载 settings.py
        settings_file = project_root / 'settings.py'
        try:
            settings = self.load_settings(settings_file)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return

        # 获取所有设置项
        settings = self.get_all_settings(settings)

        if custom_settings:
            settings = self.update_settings(settings, custom_settings)

        self._settings = DotMap(settings)

    def load_settings(self, settings_file: Path):
        """动态加载 settings 模块"""
        if not settings_file.is_file():
            raise FileNotFoundError(f"Settings file '{settings_file}' not found!")

        spec = importlib.util.spec_from_file_location("settings", str(settings_file))
        settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings)

        return settings

    def get_all_settings(self, settings):
        """获取 settings 中的所有参数并返回为字典"""
        return {key: value for key, value in vars(settings).items() if not key.startswith("__")}

    def get_setting(self, setting_name, default=None):
        """获取设置项，若不存在则返回默认值"""
        return getattr(self._settings, setting_name, default)

    def update_settings(self, settings, custom_settings: Optional[dict] = None):
        """更新设置项"""
        settings.update(custom_settings)
        return settings

    def get_setting_root(self, current_path: Optional[Path] = None):
        """获取项目根目录"""
        while current_path != current_path.parent:  # 一直递归到根目录
            if (current_path / 'settings.py').exists():  # 如果标志文件存在
                return current_path
            current_path = current_path.parent
        raise FileNotFoundError(f"Could not find 'settings.py' in any parent directories.")

    def get_settings(self):
        """获取加载后的设置"""
        return self._settings


if __name__ == "__main__":
    # 获取单例实例并访问设置
    settings_manager = SettingsManager()
    settings = settings_manager.get_settings()
    print(settings)
