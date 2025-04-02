# coding:utf-8
from PyQt5.QtWidgets import QWidget, QStackedWidget

# 导入界面组件
from .home_interface import HomeInterface
from .history_interface import HistoryInterface
from .board_view import BoardWidget, BoardWindow
from .setting_interface import SettingInterface

# 通用Widget类型
Widget = QWidget
StackedWidget = QStackedWidget

# 重新导出组件，使其可以通过interfaces模块访问
__all__ = ['Widget', 'StackedWidget', 'HomeInterface', 'SettingInterface', 'BoardWidget', 'BoardWindow', 'HistoryInterface']
