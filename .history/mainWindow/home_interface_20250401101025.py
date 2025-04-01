# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont

from qfluentwidgets import PrimaryPushButton, PushButton


class HomeInterface(QWidget):
    """ 主页界面 - 可定制的主页 """

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
        
        # 创建游戏介绍标签
        self.introLabel = QLabel(
            "欢迎来到五子棋游戏！\n"
            "五子棋是一种两人对弈的纯策略型棋类游戏，通常棋子分为黑白两色。\n"
            "游戏规则：双方轮流在棋盘上放置自己的棋子，先形成五子连线者获胜。"
        )
        self.introLabel.setAlignment(Qt.AlignCenter)
        self.introLabel.setWordWrap(True)
        introFont = self.introLabel.font()
        introFont.setPointSize(12)
        self.introLabel.setFont(introFont)
        
        # 创建按钮区域
        self.buttonWidget = QWidget()
        self.buttonLayout = QHBoxLayout(self.buttonWidget)
        
        # 添加按钮：开始游戏、查看历史等
        self.startGameBtn = PrimaryPushButton("开始游戏")
        self.startGameBtn.setFixedWidth(180)
        self.startGameBtn.setFixedHeight(40)
        
        self.historyBtn = PushButton("查看历史记录")
        self.historyBtn.setFixedWidth(180)
        self.historyBtn.setFixedHeight(40)
        
        # 将按钮添加到布局中
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.startGameBtn)
        self.buttonLayout.addSpacing(20)
        self.buttonLayout.addWidget(self.historyBtn)
        self.buttonLayout.addStretch(1)
        
        # 创建最近游戏区域
        self.recentGamesWidget = QWidget()
        self.recentGamesLayout = QVBoxLayout(self.recentGamesWidget)
        
        # 最近游戏标题
        self.recentTitle = QLabel("最近游戏")
        recentTitleFont = self.recentTitle.font()
        recentTitleFont.setPointSize(16)
        recentTitleFont.setBold(True)
        self.recentTitle.setFont(recentTitleFont)
        self.recentTitle.setAlignment(Qt.AlignCenter)
        
        # 最近游戏内容
        self.recentGamesContent = QWidget()
        self.recentGamesContentLayout = QVBoxLayout(self.recentGamesContent)
        
        # 添加一些示例的最近游戏记录
        recentGames = [
            "黑棋胜 - 小明 vs 小红 (2023-11-10 14:30)",
            "白棋胜 - 小张 vs 小李 (2023-11-09 10:00)",
            "黑棋胜 - 王五 vs 赵六 (2023-11-08 17:10)"
        ]
        
        for game in recentGames:
            gameLabel = QLabel(game)
            gameLabel.setAlignment(Qt.AlignCenter)
            self.recentGamesContentLayout.addWidget(gameLabel)
        
        # 将最近游戏标题和内容添加到最近游戏区域
        self.recentGamesLayout.addWidget(self.recentTitle)
        self.recentGamesLayout.addWidget(self.recentGamesContent)
        
        # 设置整体布局
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.introLabel)
        self.mainLayout.addSpacing(30)
        self.mainLayout.addWidget(self.buttonWidget)
        self.mainLayout.addSpacing(30)
        self.mainLayout.addWidget(self.recentGamesWidget)
        
        # 设置边距和间距
        self.mainLayout.setContentsMargins(40, 40, 40, 40)
        
        # 设置对象名
        self.setObjectName('Home-Interface')
        
        # 连接信号和槽
        self.connectSignalsToSlots()
    
    def connectSignalsToSlots(self):
        """连接信号和槽"""
        # 连接按钮点击事件
        self.historyBtn.clicked.connect(self.onHistoryBtnClicked)
        self.startGameBtn.clicked.connect(self.onStartGameBtnClicked)
    
    def onHistoryBtnClicked(self):
        """查看历史记录按钮点击事件"""
        # 切换到库页面显示历史记录
        parent = self.parent()
        if parent and hasattr(parent, 'libraryInterface'):
            parent.switchTo(parent.libraryInterface)
    
    def onStartGameBtnClicked(self):
        """开始游戏按钮点击事件"""
        # 从interfaces导入棋盘视图
        from interfaces import BoardWindow
        
        # 创建并显示游戏窗口，使用None作为父窗口参数使其成为独立窗口
        self.game_window = BoardWindow(None, style_index=0)
        # 设置窗口标志，确保其为独立窗口
        self.game_window.setWindowFlags(Qt.Window)
        self.game_window.show()
        
        # 记录游戏启动
        print(f"游戏窗口已打开，使用默认棋盘风格")