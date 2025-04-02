# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QGroupBox, QScrollArea
from PyQt5.QtGui import QFont

from qfluentwidgets import InfoBar, InfoBarPosition, isDarkTheme

# 导入历史记录管理器
from game_history_manager import GameHistoryManager


class HomeInterface(QScrollArea):
    """ 主页界面 - 包含程序介绍 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        
        # 创建垂直布局
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        self.expandLayout.setContentsMargins(60, 20, 60, 20)
        self.expandLayout.setSpacing(28)
        
        # 创建一个标题标签
        self.titleLabel = QLabel("五子棋游戏", self)
        self.titleLabel.setObjectName("interfaceTitle")  # 设置统一的对象名，用于样式表选择
        self.titleLabel.setAlignment(Qt.AlignCenter)
        font = self.titleLabel.font()
        font.setPointSize(24)
        font.setBold(True)
        self.titleLabel.setFont(font)
        
        # 创建一个容器控件，用于应用统一的样式
        self.homeWidget = QWidget()
        self.homeWidget.setObjectName("homeWidget")
        homeLayout = QVBoxLayout(self.homeWidget)
        
        # 创建简介部分
        self.introGroup = QGroupBox("程序简介")
        self.introLayout = QVBoxLayout(self.introGroup)
        
        # 创建游戏介绍标签
        self.introLabel = QLabel(
            "欢迎使用五子棋游戏！\n\n"
            "本程序是一个简单的五子棋游戏实现，具有以下特点：\n"
            "• 简洁直观的用户界面\n"
            "• 支持黑白双方轮流落子\n"
            "• 自动判断胜负\n"
            "• 支持悔棋、重新开始等操作\n"
            "• 游戏自动保存，随时可查看历史记录\n\n"
            "通过左侧导航栏可以进入不同功能界面：\n"
            "• 五子棋游戏：进入游戏对局页面\n"
            "• 历史对局：查看和管理所有历史对局记录\n"
            "• 设置：调整游戏配置和历史记录保存路径\n"
        )
        self.introLabel.setWordWrap(True)
        introFont = self.introLabel.font()
        introFont.setPointSize(11)
        self.introLabel.setFont(introFont)
        
        self.introLayout.addWidget(self.introLabel)
        
        # 将introGroup添加到homeWidget的布局中
        homeLayout.addWidget(self.introGroup)
        
        # 设置标题位置
        self.titleLabel.move(60, 63)
        
        # 添加标题和内容到布局
        self.expandLayout.addWidget(self.homeWidget)
        
        # 设置滚动区域属性
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)  # 为标题腾出空间
        
        # 设置对象名
        self.setObjectName('Home-Interface')

    def updateStyle(self):
        """更新界面样式以适应主题变化"""
        # 刷新界面
        self.update()