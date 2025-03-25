# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont

from qfluentwidgets import PrimaryPushButton, PushButton, HorizontalFlipView, HorizontalPipsPager


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
        
        # 创建棋盘风格选择区域
        self.boardStyleWidget = QWidget()
        self.boardStyleLayout = QVBoxLayout(self.boardStyleWidget)
        
        # 棋盘风格标题
        self.boardStyleTitle = QLabel("选择棋盘风格")
        boardStyleFont = self.boardStyleTitle.font()
        boardStyleFont.setPointSize(16)
        boardStyleFont.setBold(True)
        self.boardStyleTitle.setFont(boardStyleFont)
        self.boardStyleTitle.setAlignment(Qt.AlignCenter)
        
        # 创建FlipView用于展示棋盘风格
        self.flipViewWidget = QWidget()
        self.flipViewLayout = QVBoxLayout(self.flipViewWidget)
        
        # 初始化FlipView和Pager
        self.flipView = HorizontalFlipView(self)
        self.pager = HorizontalPipsPager(self)
        
        # 设置FlipView的属性
        self.flipView.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.flipView.setFixedHeight(200)  # 设置一个合适的高度
        
        # 添加棋盘风格图片 (假设图片在这些路径)
        boardStyles = [
            "c:/Users/17657/Desktop/Bupt/人工智能/五子棋/resource/board_style1.png",
            "c:/Users/17657/Desktop/Bupt/人工智能/五子棋/resource/board_style2.png",
            "c:/Users/17657/Desktop/Bupt/人工智能/五子棋/resource/board_style3.png"
        ]
        
        # 尝试添加图片，如果路径不存在则显示提示
        try:
            self.flipView.addImages(boardStyles)
            self.pager.setPageNumber(self.flipView.count())
            
            # 连接翻页事件
            self.pager.currentIndexChanged.connect(self.flipView.setCurrentIndex)
            self.flipView.currentIndexChanged.connect(self.pager.setCurrentIndex)
        except Exception as e:
            errorLabel = QLabel(f"无法加载棋盘风格图片，请确保图片路径正确。\n您可以将棋盘图片放置在resource文件夹中。")
            errorLabel.setAlignment(Qt.AlignCenter)
            errorLabel.setWordWrap(True)
            self.flipViewLayout.addWidget(errorLabel)
        
        # 添加FlipView和Pager到布局
        self.flipViewLayout.addWidget(self.flipView, 0, Qt.AlignCenter)
        self.flipViewLayout.addWidget(self.pager, 0, Qt.AlignCenter)
        self.flipViewLayout.setSpacing(10)
        
        # 添加确认按钮
        self.confirmButtonWidget = QWidget()
        self.confirmButtonLayout = QHBoxLayout(self.confirmButtonWidget)
        
        self.confirmButton = PushButton("确认选择", self)
        self.confirmButton.setFixedWidth(150)
        
        self.confirmButtonLayout.addStretch(1)
        self.confirmButtonLayout.addWidget(self.confirmButton)
        self.confirmButtonLayout.addStretch(1)
        
        # 将风格选择组件添加到布局
        self.boardStyleLayout.addWidget(self.boardStyleTitle)
        self.boardStyleLayout.addWidget(self.flipViewWidget)
        self.boardStyleLayout.addWidget(self.confirmButtonWidget)
        
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
        self.mainLayout.addSpacing(10)
        self.mainLayout.addWidget(self.introLabel)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.boardStyleWidget)  # 添加棋盘风格选择区域
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.buttonWidget)
        self.mainLayout.addSpacing(20)
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
        self.confirmButton.clicked.connect(self.onConfirmButtonClicked)
    
    def onHistoryBtnClicked(self):
        """查看历史记录按钮点击事件"""
        # 切换到库页面显示历史记录
        parent = self.parent()
        if parent and hasattr(parent, 'libraryInterface'):
            parent.switchTo(parent.libraryInterface)
    
    def onStartGameBtnClicked(self):
        """开始游戏按钮点击事件"""
        # 导入棋盘视图
        from board_view import BoardWindow
        
        # 获取选择的棋盘风格
        style_index = self.flipView.currentIndex() if hasattr(self, 'flipView') else 0
        
        # 创建并显示游戏窗口
        self.game_window = BoardWindow(self, style_index=style_index)
        self.game_window.show()
        
        # 记录游戏启动
        print(f"游戏窗口已打开，选择的棋盘风格: {style_index}")
            
    def onConfirmButtonClicked(self):
        """确认棋盘风格选择按钮点击事件"""
        # 获取当前选择的风格索引
        currentStyleIndex = self.flipView.currentIndex()
        # 这里可以保存用户的选择，或者进行其他操作
        print(f"用户选择了风格索引: {currentStyleIndex}")