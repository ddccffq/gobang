# coding:utf-8
"""
该文件负责将settings文件夹中的config模块与主应用程序连接起来
"""

import os
import sys

# 添加settings文件夹到搜索路径
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings")
if settings_path not in sys.path:
    sys.path.append(settings_path)

# 从settings导入配置
from config import cfg, AUTHOR, VERSION, YEAR, HELP_URL, FEEDBACK_URL, RELEASE_URL

# 自定义主题功能和设置
# 修改游戏相关配置
GAME_YEAR = 2023
GAME_AUTHOR = "BUPT AI课程五子棋小组"
GAME_VERSION = "1.0.0"
GAME_HELP_URL = "https://bupt.edu.cn"
GAME_FEEDBACK_URL = "https://github.com/your-username/Gomoku"

# 重写全局配置
cfg.themeColor = "游戏配置"
