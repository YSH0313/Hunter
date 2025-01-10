# -*- coding: utf-8 -*-
import sys
import logging
import inspect
import logging.handlers
from pathlib import Path
from colorama import Fore, init, Style

init(autoreset=True)  # autoreset=True意味着每次打印后颜色都会重置

from .singletonbase import SingletonBase
from hunterx.utils.reload_settings import SettingsManager


"""
format参数值说明：
%(name)s：   打印Logger的名字
%(levelno)s: 打印日志级别的数值
%(levelname)s: 打印日志级别名称
%(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
%(filename)s: 打印当前执行程序的文件名
%(module)s: 打印日志来自哪个模块
%(funcName)s: 打印日志的当前函数
%(lineno)d:  打印日志的当前行号
%(asctime)s: 打印日志的时间
%(thread)d: 打印线程ID
%(threadName)s: 打印线程名称
%(process)d: 打印进程ID
%(message)s: 打印日志信息
"""

logging.getLogger("root").setLevel(logging.WARNING)

green_text = Fore.GREEN
red_text = Fore.RED
yellow_text = Fore.YELLOW
reset_all = Style.RESET_ALL

level_colors = {
    'DEBUG': Fore.BLUE,
    'INFO': Fore.CYAN,
    'WARNING': Fore.RED,
    'ERROR': Fore.RED,
    'CRITICAL': Fore.RED + Style.BRIGHT
}

level_map = {
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        super().format(record)
        asctime = record.asctime
        name = record.name
        levelname = record.levelname
        if levelname != 'ERROR':
            message = record.message
            levecolor = level_colors[levelname]
            # 根据级别给日志的 levelname 和 message 部分上色
            return f'{yellow_text}{asctime}{reset_all} {green_text}[{name}]{reset_all} {levecolor}{levelname}: {message}{reset_all}'
        else:
            return record

class LogCaptor(SingletonBase):

    def __init__(self):
        super().__init__()
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.path_name = Path(sys.argv[0]).stem  # 使用 pathlib 获取文件名无扩展名

        self.no_console = [sys.argv[idx] for idx in [1] if 0 <= idx < len(sys.argv)]

        __settings = SettingsManager().get_settings()
        self.log_path, self.log_level = __settings.LOG_PATH, __settings.LOG_LEVEL

        self.loggers = {}

        self.logger = logging.getLogger(__name__)

        self.logger.setLevel(level_map[self.log_level])  # 设置屏幕日志级别

        format_file = logging.Formatter(
            '%(asctime)s [%(name)s] %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S"
        )  # 设置日志格式

        if not self.no_console and sys.platform != 'linux':
            # console = logging.StreamHandler()  # 往屏幕上输出
            #
            # console.setFormatter(
            #     ColoredFormatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
            # )  # 设置屏幕上显示的格式

            self.console_formatter = ColoredFormatter(
                '%(asctime)s [%(name)s] %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S"
            )

            # self.logger.addHandler(console)  # 把屏幕对象加到logger里

        if self.log_path:
            log_dir = Path(self.log_path)
            log_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在

            log_file = log_dir / f'{self.path_name}.log'

            self.file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file, mode='w', encoding='utf-8',
                maxBytes=100 * 1024 * 1024, backupCount=1
            )

            self.file_handler.setFormatter(format_file)  # 设置文件里写入的格式
            # self.logger.addHandler(self.file_handler)  # 把对象加到logger里
        else:
            self.file_handler = None

    def my_hook(self, d):
        if d['status'] == 'finished':
            self.logger.info('Done downloading, now converting ...')

    def func(self):
        self.logger.info("Start print log")
        self.logger.info('这是一个测试')
        self.logger.debug("Do something")
        self.logger.warning("Something maybe fail.")
        self.logger.info("Finish")

    def get_logger(self):
        # 获取调用者模块的完整路径
        frame = inspect.stack()[1]  # 获取调用 get_module_logger 的上一帧
        module = inspect.getmodule(frame[0])  # 获取调用模块
        module_name = module.__name__ if module else "unknown"

        # 如果已经存在该模块的 Logger，直接返回
        if module_name in self.loggers:
            return self.loggers[module_name]

        # 创建新的 Logger 实例
        logger = logging.getLogger(module_name)
        logger.setLevel(level_map[self.log_level])

        # 添加屏幕日志处理器
        if not self.no_console and sys.platform != 'linux':
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.console_formatter)
            logger.addHandler(console_handler)

        # 添加文件日志处理器
        if self.file_handler:
            logger.addHandler(self.file_handler)

        # 缓存 Logger
        self.loggers[module_name] = logger
        return logger


# logcaptor = LogCaptor()
