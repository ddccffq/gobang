# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QGridLayout
from PyQt5.QtGui import QFont, QPainter, QPen, QBrush, QColor

from qfluentwidgets import PushButton, RadioButton, ComboBox, RoundMenu, FluentIcon as FIF

class GameInterface(QWidget):
    """ 游戏界面 - 五子棋游戏主界面 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QHBoxLayout(self)
        
        # 游戏区域 - 左侧
        self.gameArea = QFrame(self)
        self.gameArea.setFrameShape(QFrame.StyledPanel)
        self.gameAreaLayout = QVBoxLayout(self.gameArea)
        
        # 棋盘
        self.boardWidget = ChessBoardWidget(self)
        self.boardWidget.setSizePolicy(QWidget.Policy.Expanding, QWidget.Policy.Expanding)
        
        # 游戏信息
        self.gameInfoWidget = QWidget(self)
        self.gameInfoLayout = QHBoxLayout(self.gameInfoWidget)
        
        self.currentPlayerLabel = QLabel("当前: 黑棋", self)
        self.currentPlayerLabel.setFont(QFont("微软雅黑", 12, QFont.Bold))
        
        self.timeLimitLabel = QLabel("剩余时间: 30秒", self)
        self.timeLimitLabel.setFont(QFont("微软雅黑", 12))
        
        self.gameInfoLayout.addWidget(self.currentPlayerLabel)
        self.gameInfoLayout.addStretch(1)
        self.gameInfoLayout.addWidget(self.timeLimitLabel)
        
        # 将组件添加到游戏区域布局
        self.gameAreaLayout.addWidget(self.boardWidget)
        self.gameAreaLayout.addWidget(self.gameInfoWidget)
        
        # 控制区域 - 右侧
        self.controlArea = QFrame(self)
        self.controlArea.setFrameShape(QFrame.StyledPanel)
        self.controlArea.setFixedWidth(200)
        self.controlAreaLayout = QVBoxLayout(self.controlArea)
        
        # 游戏控制
        self.gameControlLabel = QLabel("游戏控制", self)
        self.gameControlLabel.setFont(QFont("微软雅黑", 14, QFont.Bold))
        self.gameControlLabel.setAlignment(Qt.AlignCenter)
        
        # 按钮
        self.startButton = PushButton("开始游戏", self)
        self.restartButton = PushButton("重新开始", self)
        self.undoButton = PushButton("悔棋", self)
        self.surrenderButton = PushButton("认输", self)
        
        # 游戏设置
        self.settingsLabel = QLabel("游戏设置", self)
        self.settingsLabel.setFont(QFont("微软雅黑", 14, QFont.Bold))
        self.settingsLabel.setAlignment(Qt.AlignCenter)
        
        # 对手选择
        self.opponentWidget = QWidget(self)
        self.opponentLayout = QVBoxLayout(self.opponentWidget)
        
        self.opponentLabel = QLabel("选择对手:", self)
        self.opponentLabel.setFont(QFont("微软雅黑", 12))
        
        self.humanRadio = RadioButton("人类玩家", self)
        self.aiRadio = RadioButton("AI 对手", self)
        self.humanRadio.setChecked(True)
        
        self.opponentLayout.addWidget(self.opponentLabel)
        self.opponentLayout.addWidget(self.humanRadio)
        self.opponentLayout.addWidget(self.aiRadio)
        
        # AI 难度选择
        self.difficultyWidget = QWidget(self)
        self.difficultyLayout = QVBoxLayout(self.difficultyWidget)
        
        self.difficultyLabel = QLabel("AI 难度:", self)
        self.difficultyLabel.setFont(QFont("微软雅黑", 12))
        
        self.difficultyCombo = ComboBox(self)
        self.difficultyCombo.addItems(["简单", "中等", "困难"])
        self.difficultyCombo.setCurrentIndex(1)  # 默认中等难度
        
        self.difficultyLayout.addWidget(self.difficultyLabel)
        self.difficultyLayout.addWidget(self.difficultyCombo)
        
        # 将所有组件添加到控制区域布局
        self.controlAreaLayout.addWidget(self.gameControlLabel)
        self.controlAreaLayout.addWidget(self.startButton)
        self.controlAreaLayout.addWidget(self.restartButton)
        self.controlAreaLayout.addWidget(self.undoButton)
        self.controlAreaLayout.addWidget(self.surrenderButton)
        self.controlAreaLayout.addSpacing(20)
        self.controlAreaLayout.addWidget(self.settingsLabel)
        self.controlAreaLayout.addWidget(self.opponentWidget)
        self.controlAreaLayout.addWidget(self.difficultyWidget)
        self.controlAreaLayout.addStretch(1)
        
        # 将两个主要区域添加到主布局
        self.mainLayout.addWidget(self.gameArea, 1)
        self.mainLayout.addWidget(self.controlArea)
        
        # 设置间距
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(10)
        
        # 设置对象名
        self.setObjectName('Game-Interface')
        
        # 连接信号和槽
        self.connectSignalsToSlots()
        
        # 初始化设置
        self.updateDifficultyVisibility()
    
    def connectSignalsToSlots(self):
        """连接信号和槽"""
        self.aiRadio.toggled.connect(self.updateDifficultyVisibility)
        self.humanRadio.toggled.connect(self.updateDifficultyVisibility)
        
        self.startButton.clicked.connect(self.onStartButtonClicked)
        self.restartButton.clicked.connect(self.onRestartButtonClicked)
        self.undoButton.clicked.connect(self.onUndoButtonClicked)
        self.surrenderButton.clicked.connect(self.onSurrenderButtonClicked)
    
    def updateDifficultyVisibility(self):
        """根据对手选择更新难度选择的可见性"""
        self.difficultyWidget.setVisible(self.aiRadio.isChecked())
    
    def onStartButtonClicked(self):
        """开始游戏按钮点击事件"""
        print("开始游戏")
        # 在这里实现游戏开始逻辑
    
    def onRestartButtonClicked(self):
        """重新开始按钮点击事件"""
        print("重新开始游戏")
        # 在这里实现重新开始游戏逻辑
    
    def onUndoButtonClicked(self):
        """悔棋按钮点击事件"""
        print("悔棋")
        # 在这里实现悔棋逻辑
    
    def onSurrenderButtonClicked(self):
        """认输按钮点击事件"""
        print("认输")
        # 在这里实现认输逻辑

class ChessBoardWidget(QWidget):
    """棋盘控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.boardSize = 15  # 15×15的棋盘
        self.board = [[0 for _ in range(self.boardSize)] for _ in range(self.boardSize)]
        self.currentPlayer = 1  # 1表示黑棋，2表示白棋
        self.gameStarted = False
        
    def paintEvent(self, event):
        """绘制棋盘和棋子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算棋盘格子大小
        cellSize = min(self.width(), self.height()) / (self.boardSize + 1)
        margin = cellSize
        
        # 绘制棋盘背景
        painter.fillRect(self.rect(), QColor(240, 217, 181))  # 木色背景
        
        # 绘制网格线
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(1)
        painter.setPen(pen)
        
        for i in range(self.boardSize):
            # 横线
            painter.drawLine(
                margin, margin + i * cellSize,
                margin + (self.boardSize - 1) * cellSize, margin + i * cellSize
            )
            # 竖线
            painter.drawLine(
                margin + i * cellSize, margin,
                margin + i * cellSize, margin + (self.boardSize - 1) * cellSize
            )
        
        # 绘制棋盘中心和星位
        starPoints = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        pen.setWidth(3)
        painter.setPen(pen)
        
        for x, y in starPoints:
            painter.drawPoint(margin + x * cellSize, margin + y * cellSize)
        
        # 绘制棋子
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if self.board[i][j] == 1:  # 黑棋
                    painter.setBrush(QBrush(QColor(0, 0, 0)))
                    painter.drawEllipse(
                        margin + i * cellSize - cellSize * 0.4,
                        margin + j * cellSize - cellSize * 0.4,
                        cellSize * 0.8, cellSize * 0.8
                    )
                elif self.board[i][j] == 2:  # 白棋
                    painter.setBrush(QBrush(QColor(255, 255, 255)))
                    painter.drawEllipse(
                        margin + i * cellSize - cellSize * 0.4,
                        margin + j * cellSize - cellSize * 0.4,
                        cellSize * 0.8, cellSize * 0.8
                    )
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if not self.gameStarted:
            return
            
        # 计算棋盘格子大小
        cellSize = min(self.width(), self.height()) / (self.boardSize + 1)
        margin = cellSize
        
        # 计算点击的位置对应的棋盘坐标
        x = round((event.x() - margin) / cellSize)
        y = round((event.y() - margin) / cellSize)
        
        # 检查是否在有效范围内
        if 0 <= x < self.boardSize and 0 <= y < self.boardSize and self.board[x][y] == 0:
            # 放置棋子
            self.board[x][y] = self.currentPlayer
            
            # 切换玩家
            self.currentPlayer = 3 - self.currentPlayer  # 1变2，2变1
            
            # 更新棋盘显示
            self.update()
            
            # 通知父组件更新当前玩家信息
            if self.parent() and hasattr(self.parent(), 'currentPlayerLabel'):
                playerText = "黑棋" if self.currentPlayer == 1 else "白棋"
                self.parent().currentPlayerLabel.setText(f"当前: {playerText}")
            
            # TODO: 检查游戏是否结束（胜利条件）
