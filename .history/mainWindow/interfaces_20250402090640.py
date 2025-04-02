# coding:utf-8
from PyQt5.QtWidgets import QWidget, QStackedWidget

# 导入界面组件
from home_interface import HomeInterface
from history_interface import HistoryInterface
from board_view import BoardWidget, BoardWindow

# 导入设置界面，替换原来的库界面
import sys
import os

# 添加settings文件夹到搜索路径
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings")
if settings_path not in sys.path:
    sys.path.append(settings_path)

# 导入设置界面
from setting_interface import SettingInterface

# 通用Widget类型
Widget = QWidget
StackedWidget = QStackedWidget  # 使用PyQt5的QStackedWidget代替

# 重新导出组件，使其可以通过interfaces模块访问
__all__ = ['Widget', 'StackedWidget', 'HomeInterface', 'SettingInterface', 'BoardWidget', 'BoardWindow', 'HistoryInterface']
