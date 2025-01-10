# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2024/12/30 18:42
# @Version: 1.0.0
# @Description: '创建项目工具所用到的配置文件'
from colorama import Fore, init, Style

init(autoreset=True)  # autoreset=True意味着每次打印后颜色都会重置

green_text = Fore.GREEN
red_text = Fore.RED
blue_text = Fore.BLUE
yellow_text = Fore.YELLOW
purple_text = Fore.MAGENTA
white_text = Fore.WHITE + Style.BRIGHT
reset_all = Style.RESET_ALL

# 自定义高亮样式
custom_style = {
    'questionmark': '#ff9d00',  # 问题的颜色
    'input': '#18e4ed',  # 输入文本时的颜色
    'pointer': '#3fed18',  # 被选中的项的颜色
    'instruction': '#ffffff',  # 提示文字的颜色
    'answer': '#ff9d00',  # 回答文本的颜色
    'question': '#ffffff',  # 问题文本的颜色
}
