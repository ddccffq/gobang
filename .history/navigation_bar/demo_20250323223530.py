# coding:utf-8
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl, QModelIndex
from PyQt5.QtGui import QIcon, QDesktopServices, QPalette
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget, QTableWidgetItem, QStyleOptionViewItem, QSizePolicy

from qfluentwidgets import (NavigationBar, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor, SearchLineEdit,
                            PopUpAniStackedWidget, getFont, TableWidget, TableItemDelegate)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar


class CustomTableItemDelegate(TableItemDelegate):
    """ Custom table item delegate """

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        if index.column() != 1:
            return

        if isDarkTheme():
            option.palette.setColor(QPalette.Text, Qt.white)
            option.palette.setColor(QPalette.HighlightedText, Qt.white)
        else:
            option.palette.setColor(QPalette.Text, Qt.red)
            option.palette.setColor(QPalette.HighlightedText, Qt.red)


class Widget(QWidget):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class AppInterface(QWidget):
    """ 应用界面 - 包含表格视图 """

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
        
        # 减小边距使表格更好地填充容器
        self.hBoxLayout.setContentsMargins(10, 10, 10, 10)
        self.hBoxLayout.addWidget(self.tableView)
        
        # 让表格填充所有可用空间
        self.tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 设置对象名，用于导航
        self.setObjectName('Application-Interface')
    
    def setupTable(self):
        """ 设置表格内容 """
        self.tableView.setRowCount(30)
        self.tableView.setColumnCount(5)
        
        # 表格数据
        songInfos = [
            ['かばん', 'aiko', 'かばん', '2004', '5:04'],
            ['爱你', '王心凌', '爱你', '2004', '3:39'],
            ['星のない世界', 'aiko', '星のない世界/横顔', '2007', '5:30'],
            ['横顔', 'aiko', '星のない世界/横顔', '2007', '5:06'],
            ['秘密', 'aiko', '秘密', '2008', '6:27'],
            ['シアワセ', 'aiko', '秘密', '2008', '5:25'],
            ['二人', 'aiko', '二人', '2008', '5:00'],
            ['スパークル', 'RADWIMPS', '君の名は。', '2016', '8:54'],
            ['なんでもないや', 'RADWIMPS', '君の名は。', '2016', '3:16'],
            ['前前前世', 'RADWIMPS', '人間開花', '2016', '4:35'],
            ['恋をしたのは', 'aiko', '恋をしたのは', '2016', '6:02'],
            ['夏バテ', 'aiko', '恋をしたのは', '2016', '4:41'],
            ['もっと', 'aiko', 'もっと', '2016', '4:50'],
            ['問題集', 'aiko', 'もっと', '2016', '4:18'],
            ['半袖', 'aiko', 'もっと', '2016', '5:50'],
        ]
        
        # 添加额外数据行填充表格
        songInfos *= 2
        
        # 填充表格
        for i, songInfo in enumerate(songInfos):
            for j in range(5):
                self.tableView.setItem(i, j, QTableWidgetItem(songInfo[j]))
        
        # 设置表头
        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(['歌曲名', '艺术家', '专辑', '年份', '时长'])
        
        # 调整列宽适应内容
        self.tableView.resizeColumnsToContents()


class StackedWidget(QFrame):
    """ Stacked widget """

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


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.hBoxLayout.removeWidget(self.minBtn)
        self.hBoxLayout.removeWidget(self.maxBtn)
        self.hBoxLayout.removeWidget(self.closeBtn)

        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 20)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

        # add search line edit
        self.searchLineEdit = SearchLineEdit(self)
        self.searchLineEdit.setPlaceholderText('搜索应用、游戏、电影、设备等')
        self.searchLineEdit.setFixedWidth(400)
        self.searchLineEdit.setClearButtonEnabled(True)

        self.vBoxLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(0)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setAlignment(Qt.AlignTop)
        self.buttonLayout.addWidget(self.minBtn)
        self.buttonLayout.addWidget(self.maxBtn)
        self.buttonLayout.addWidget(self.closeBtn)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.vBoxLayout.addStretch(1)
        self.hBoxLayout.addLayout(self.vBoxLayout, 0)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))

    def resizeEvent(self, e):
        self.searchLineEdit.move((self.width() - self.searchLineEdit.width()) //2, 8)



class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        # use dark theme mode
        # setTheme(Theme.DARK)

        # change the theme color
        # setThemeColor('#0078d4')

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)

        # create sub interface
        self.homeInterface = Widget('Home Interface', self)
        self.appInterface = AppInterface(self)  # 使用新的AppInterface替代原来的Widget
        self.videoInterface = Widget('Video Interface', self)
        self.libraryInterface = Widget('library Interface', self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', selectedIcon=FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.APPLICATION, '应用')
        self.addSubInterface(self.videoInterface, FIF.VIDEO, '视频')

        self.addSubInterface(self.libraryInterface, FIF.BOOK_SHELF, '库', NavigationItemPosition.BOTTOM, FIF.LIBRARY_FILL)
        
        # 将帮助按钮修改为无操作
        self.navigationBar.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='帮助',
            onClick=lambda: None,  # 无操作的匿名函数
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            selectedIcon=selectedIcon,
            position=position,
        )

    def setQss(self):
        import os
        color = 'dark' if isDarkTheme() else 'light'
        qss_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'resource/{color}/demo.qss')
        
        # 检查文件是否存在
        if os.path.exists(qss_file):
            with open(qss_file, encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式表文件不存在: {qss_file}")
            # 可以设置一个默认的内联样式
            self.setStyleSheet("")

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
