# coding:utf-8
from PyQt5.QtWidgets import QWidget, QStackedWidget

# 导入界面组件
from home_interface import HomeInterface
from library_interface import LibraryInterface
from history_interface import HistoryInterface  # 新增导入
from board_view import BoardWidget, BoardWindow

# 通用Widget类型
Widget = QWidget
StackedWidget = QStackedWidget  # 使用PyQt5的QStackedWidget代替

# 重新导出组件，使其可以通过interfaces模块访问
__all__ = ['Widget', 'StackedWidget', 'HomeInterface', 'LibraryInterface', 'BoardWidget', 'BoardWindow', 'HistoryInterface']
