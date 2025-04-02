# coding:utf-8
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QLabel, QHBoxLayout, QVBoxLayout, QWidget, QGroupBox, 
                            QGridLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QPixmap

from qfluentwidgets import (InfoBar, InfoBarPosition, isDarkTheme, CardWidget, 
                           ScrollArea, FluentIcon as FIF, IconWidget)

# 修改为绝对导入
from mainWindow.game_history_manager import GameHistoryManager


class HomeInterface(ScrollArea):
    """ 主页界面 - 包含程序介绍 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('Home-Interface')
        
        # 创建可滚动区域
        self.scrollWidget = QWidget()
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 创建主布局
        self.mainLayout = QVBoxLayout(self.scrollWidget)
        self.mainLayout.setContentsMargins(40, 40, 40, 40)
        self.mainLayout.setSpacing(30)
        
        # 创建标题区域
        self.setupTitleArea()
        
        # 创建三个卡片布局
        self.setupCardLayout()
        
        # 创建底部信息
        self.setupFooterArea()
        
        # 初始化界面样式
        self.updateStyle()

    def setupTitleArea(self):
        """设置标题区域"""
        # 创建标题区域容器
        titleContainer = QWidget()
        titleLayout = QHBoxLayout(titleContainer)
        
        # 创建图标和文本区域
        iconLabel = IconWidget(FIF.GAME, size=QSize(72, 72))
        
        # 创建标题和描述
        titleTextWidget = QWidget()
        titleTextLayout = QVBoxLayout(titleTextWidget)
        titleTextLayout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标题
        titleLabel = QLabel("五子棋游戏")
        titleFont = titleLabel.font()
        titleFont.setPointSize(28)
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        
        # 创建副标题
        subtitleLabel = QLabel("AI 课程项目作品")
        subtitleFont = subtitleLabel.font()
        subtitleFont.setPointSize(14)
        subtitleLabel.setFont(subtitleFont)
        subtitleLabel.setObjectName("subtitleLabel")
        
        # 添加到布局
        titleTextLayout.addWidget(titleLabel)
        titleTextLayout.addWidget(subtitleLabel)
        
        # 添加到标题容器
        titleLayout.addWidget(iconLabel)
        titleLayout.addWidget(titleTextWidget, 1)
        titleLayout.addStretch(2)
        
        # 添加到主布局
        self.mainLayout.addWidget(titleContainer)

    def setupCardLayout(self):
        """设置卡片布局"""
        # 创建网格布局，用于放置卡片
        gridLayout = QGridLayout()
        gridLayout.setSpacing(20)
        
        # 创建软件简介卡片
        introCard = self.createCard(
            "软件简介", 
            FIF.INFO,
            "本软件是北京邮电大学人工智能课程项目作品，是一个基于 PyQt5 开发的五子棋游戏。"
            "游戏采用经典的 15×15 棋盘，支持人机对战、历史记录查询等功能。"
            "界面设计采用 Fluent Design 风格，美观易用，支持深浅色主题切换。"
        )
        
        # 创建功能特点卡片
        featuresCard = self.createCard(
            "功能特点", 
            FIF.VIEW,
            "<b>· 经典五子棋玩法</b> — 黑白双方轮流落子，五子连珠获胜<br>"
            "<b>· 多主题棋盘</b> — 提供多种棋盘风格和主题，满足不同审美需求<br>"
            "<b>· 历史记录</b> — 自动保存每局游戏，随时查看或继续历史对局<br>"
            "<b>· 操作便捷</b> — 支持悔棋、重开、认输等操作，操作简单直观<br>"
            "<b>· 主题定制</b> — 支持浅色/深色主题，自定义主题颜色<br>"
        )
        
        # 创建使用指南卡片
        guideCard = self.createCard(
            "使用指南", 
            FIF.HELP,
            "<b>1. 开始游戏</b> — 点击左侧导航栏的\"五子棋游戏\"进入游戏界面<br>"
            "<b>2. 对弈操作</b> — 点击\"开始对局\"按钮，黑棋先行，点击棋盘落子<br>"
            "<b>3. 历史查询</b> — 在\"历史对局\"页面可查看、筛选和加载历史棋局<br>"
            "<b>4. 个性设置</b> — 在\"设置\"页面调整主题、语言等个性化选项<br>"
            "<b>5. 更多帮助</b> — 点击\"设置\"页面中的\"帮助\"链接获取详细指南<br>"
        )
        
        # 添加卡片到网格
        gridLayout.addWidget(introCard, 0, 0)
        gridLayout.addWidget(featuresCard, 0, 1)
        gridLayout.addWidget(guideCard, 1, 0, 1, 2)
        
        # 添加网格到主布局
        self.mainLayout.addLayout(gridLayout)

    def setupFooterArea(self):
        """设置底部信息区域"""
        # 创建底部信息
        footerLabel = QLabel("© 2023 北京邮电大学 AI课程五子棋小组 - 版本 1.0.0")
        footerLabel.setAlignment(Qt.AlignCenter)
        footerFont = footerLabel.font()
        footerFont.setPointSize(9)
        footerLabel.setFont(footerFont)
        footerLabel.setObjectName("footerLabel")
        
        # 添加到主布局
        self.mainLayout.addStretch(1)  # 添加弹性空间使footer固定在底部
        self.mainLayout.addWidget(footerLabel)

    def createCard(self, title, icon, content):
        """创建信息卡片"""
        # 创建卡片
        card = CardWidget()
        cardLayout = QVBoxLayout(card)
        
        # 创建标题区域
        titleWidget = QWidget()
        titleLayout = QHBoxLayout(titleWidget)
        titleLayout.setContentsMargins(0, 0, 0, 0)
        
        # 创建图标
        iconWidget = IconWidget(icon, size=QSize(24, 24))
        
        # 创建标题
        titleLabel = QLabel(title)
        titleFont = titleLabel.font()
        titleFont.setPointSize(14)
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        
        # 添加到标题布局
        titleLayout.addWidget(iconWidget)
        titleLayout.addWidget(titleLabel)
        titleLayout.addStretch(1)
        
        # 创建内容标签
        contentLabel = QLabel(content)
        contentLabel.setWordWrap(True)
        contentLabel.setTextFormat(Qt.RichText)
        contentFont = contentLabel.font()
        contentFont.setPointSize(11)
        contentLabel.setFont(contentFont)
        
        # 添加到卡片布局
        cardLayout.addWidget(titleWidget)
        cardLayout.addWidget(contentLabel, 1)
        
        return card

    def updateStyle(self):
        """更新界面样式以适应主题变化"""
        # 基本样式
        styleSheet = """
            QLabel#subtitleLabel {
                color: gray;
            }
            
            QLabel#footerLabel {
                color: gray;
            }
        """
        
        # 根据主题设置不同的样式
        if isDarkTheme():
            styleSheet += """
                CardWidget {
                    background-color: #3c3c3c;
                    border: 1px solid #505050;
                    border-radius: 8px;
                }
                
                QLabel {
                    color: white;
                }
            """
        else:
            styleSheet += """
                CardWidget {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
                
                QLabel {
                    color: black;
                }
            """
        
        self.setStyleSheet(styleSheet)