# coding:utf-8
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import StackedWidget

# 导入界面组件
from home_interface import HomeInterface
from library_interface import LibraryInterface
from board_view import BoardWidget, BoardWindow

# 通用Widget类型
Widget = QWidget

# 重新导出组件，使其可以通过interfaces模块访问
__all__ = ['Widget', 'StackedWidget', 'HomeInterface', 'LibraryInterface', 'BoardWidget', 'BoardWindow']
