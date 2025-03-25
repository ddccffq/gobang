# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve, QSize
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QTableWidgetItem, QSizePolicy, QHeaderView
from PyQt5.QtGui import QFont

from qfluentwidgets import PopUpAniStackedWidget, TableWidget, PrimaryPushButton, PushButton, HorizontalFlipView, HorizontalPipsPager, StandardButton


class Widget(QWidget):
    """ 基础通用界面 """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class AppInterface(QWidget):
    """ 应用界面 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.setObjectName('Application-Interface')


class LibraryInterface(QWidget):
    """ 库界面 - 包含表格视图，用于显示五子棋历史记录 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.tableView = TableWidget(self)

        # 启用表格边框
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)

        # 设置表格内容
        self.setupTable()
        
        # 完全消除边距使表格贴合外围
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.tableView)
        
        # 让表格填充所有可用空间
        self.tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 设置对象名，用于导航
        self.setObjectName('Library-Interface')
    
    def setupTable(self):
        """ 设置表格内容为五子棋历史记录 """
        # 设置4列：序号，时间，胜负，具体对局
        self.tableView.setColumnCount(4)
        
        # 示例历史数据
        gameHistory = [
            ['1', '2023-11-01 15:30', '黑棋胜', '黑棋：小明 vs 白棋：小红'],
            ['2', '2023-11-02 10:15', '白棋胜', '黑棋：小张 vs 白棋：小李'],
            ['3', '2023-11-03 14:20', '黑棋胜', '黑棋：小王 vs 白棋：小赵'],
            ['4', '2023-11-04 16:45', '白棋胜', '黑棋：张三 vs 白棋：李四'],
            ['5', '2023-11-05 09:30', '和棋', '黑棋：王五 vs 白棋：赵六'],
            ['6', '2023-11-06 11:20', '黑棋胜', '黑棋：刘一 vs 白棋：陈二'],
            ['7', '2023-11-07 13:40', '白棋胜', '黑棋：张三 vs 白棋：李四'],
            ['8', '2023-11-08 17:10', '黑棋胜', '黑棋：王五 vs 白棋：赵六'],
            ['9', '2023-11-09 10:00', '白棋胜', '黑棋：小明 vs 白棋：小红'],
            ['10', '2023-11-10 14:30', '黑棋胜', '黑棋：小张 vs 白棋：小李'],
        ]
        
        # 设置足够的行数
        self.tableView.setRowCount(len(gameHistory))
        
        # 填充表格
        for i, game in enumerate(gameHistory):
            for j in range(4):
                item = QTableWidgetItem(game[j])
                # 使序号和时间列居中对齐
                if j <= 1:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableView.setItem(i, j, item)
        
        # 设置表头
        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(['序号', '时间', '胜负', '具体对局'])
        
        # 获取表格的水平表头
        header = self.tableView.horizontalHeader()
        
        # 调整列宽 - 设置序号列较窄，具体对局列较宽
        self.tableView.setColumnWidth(0, 60)   # 序号列宽
        self.tableView.setColumnWidth(1, 150)  # 时间列宽
        self.tableView.setColumnWidth(2, 100)  # 胜负列宽
        
        # 固定前三列的宽度，不允许用户调整
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 序号列固定
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 时间列固定
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 胜负列固定
        
        # 设置最后一列自动扩展以填充剩余空间
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 具体对局列自适应剩余宽度

        # 设置表格可选中整行
        self.tableView.setSelectionBehavior(TableWidget.SelectRows)


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
        
        self.confirmButton = StandardButton("确认选择", self)
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
        # 切换到游戏页面
        parent = self.parent()
        if parent and hasattr(parent, 'appInterface'):
            parent.switchTo(parent.appInterface)
            
    def onConfirmButtonClicked(self):
        """确认棋盘风格选择按钮点击事件"""
        # 获取当前选择的风格索引
        currentStyleIndex = self.flipView.currentIndex()
        # 这里可以保存用户的选择，或者进行其他操作
        print(f"用户选择了风格索引: {currentStyleIndex}")


class StackedWidget(QFrame):
    """ 堆叠式窗口组件 """

    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget):
        """ add widget to view """
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def setCurrentWidget(self, widget, popOut=False):
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(
                widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)
