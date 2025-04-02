# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QGroupBox
from PyQt5.QtGui import QFont

from qfluentwidgets import InfoBar, InfoBarPosition, isDarkTheme

# 导入历史记录管理器
from game_history_manager import GameHistoryManager


class HomeInterface(QWidget):
    """ 主页界面 - 包含程序介绍 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QVBoxLayout(self)
        
        # 创建一个标题标签
        self.titleLabel = QLabel("五子棋游戏", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        font = self.titleLabel.font()
        font.setPointSize(24)
        font.setBold(True)
        self.titleLabel.setFont(font)
        
        # 创建一个容器控件，用于应用统一的样式
        self.homeWidget = QWidget(self)
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
        
        # 添加到主布局
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.homeWidget, 1)  # 1表示伸展因子，占用更多空间
        
        # 设置边距和间距
        self.mainLayout.setContentsMargins(40, 40, 40, 40)
        
        # 设置对象名
        self.setObjectName('Home-Interface')

    def updateStyle(self):
        """更新界面样式以适应主题变化"""
        # 更新标签和组件颜色
        if isDarkTheme():
            self.setStyleSheet("""
                QGroupBox { 
                    color: white;
                    background-color: #333333;
                    border: 1px solid #555555;
                }
                QLabel { color: white; }
            """)
        else:
            self.setStyleSheet("")
        
        # 刷新界面
        self.update()