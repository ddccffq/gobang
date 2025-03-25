# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QTableWidgetItem, QSizePolicy, QHeaderView

from qfluentwidgets import PopUpAniStackedWidget, TableWidget, FlipView, StandardButton, ImageLabel, InfoBar


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
        self.titleLabel = QLabel("五子棋游戏主页", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        font = self.titleLabel.font()
        font.setPointSize(16)
        self.titleLabel.setFont(font)
        
        # 创建一个内容区域的widget，稍后可以在这里添加更多内容
        self.contentWidget = QWidget(self)
        self.contentLayout = QVBoxLayout(self.contentWidget)
        
        # 设置布局
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.contentWidget)
        
        # 设置边距和间距
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.contentLayout.setContentsMargins(10, 10, 10, 10)
        
        # 设置对象名
        self.setObjectName('Home-Interface')
        
    def getContentWidget(self):
        """获取内容区域的widget，方便后续添加内容"""
        return self.contentWidget
        
    def getContentLayout(self):
        """获取内容区域的布局，方便后续添加内容"""
        return self.contentLayout


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
