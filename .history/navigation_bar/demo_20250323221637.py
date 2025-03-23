# coding:utf-8
import sys
import os
from enum import Enum

from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl, QPropertyAnimation, QPoint, QRect, QEvent, QSize
from PyQt5.QtGui import QIcon, QDesktopServices, QPainter, QPen, QColor, QFont, QCursor, QMouseEvent, QPixmap
from PyQt5.QtWidgets import (QLabel, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget,
                            QPushButton, QStackedWidget, QGraphicsOpacityEffect, QLineEdit,
                            QDialog, QDialogButtonBox, QSizePolicy, QToolButton)


# 定义图标枚举作为替代
class FluentIcon(Enum):
    HOME = "home"
    HOME_FILL = "home_fill"
    APPLICATION = "application"
    VIDEO = "video"
    BOOK_SHELF = "book_shelf"
    LIBRARY_FILL = "library_fill"
    HELP = "help"
    
    def path(self):
        # 实际应用中，你需要创建一个resource/icons目录并放入相应图标
        return f"resource/icons/{self.value}.png"


# 定义导航项位置枚举
class NavigationItemPosition(Enum):
    TOP = 0
    BOTTOM = 1


class Widget(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class PopUpAniStackedWidget(QStackedWidget):
    """ 自定义带动画的堆叠窗口 """
    currentChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(1)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        
    def setCurrentWidget(self, widget, popOut=False, fade=True, duration=200, easing=QEasingCurve.OutCubic):
        """ 带动画切换当前窗口 """
        if self.currentWidget() == widget:
            return
            
        if fade:
            self.animation.setDuration(duration)
            self.animation.setEasingCurve(easing)
            self.animation.setStartValue(0)
            self.animation.setEndValue(1)
            
            # 先设置窗口，然后播放动画
            super().setCurrentWidget(widget)
            self.animation.start()
        else:
            super().setCurrentWidget(widget)
            
        self.currentChanged.emit(self.currentIndex())


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


class NavigationButton(QPushButton):
    """ 导航按钮 """
    def __init__(self, icon, text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        
        # 加载图标
        if isinstance(icon, FluentIcon):
            self.icon_path = icon.path()
            self.selected_icon_path = icon.path()  # 可以设置不同的选中图标
            self.setIcon(QIcon(self.icon_path))
        else:
            self.icon_path = ""
            self.selected_icon_path = ""
            
        # 设置属性
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setIconSize(QSize(20, 20))
        self.setCursor(Qt.PointingHandCursor)
        
        # 样式
        self.setStyleSheet("""
            NavigationButton {
                border: none;
                padding: 5px 10px;
                text-align: left;
                border-radius: 4px;
            }
            NavigationButton:checked {
                background-color: #e6e6e6;
            }
            NavigationButton:hover:!checked {
                background-color: #f0f0f0;
            }
        """)


class NavigationBar(QFrame):
    """ 导航栏 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setObjectName("navigationBar")
        
        # 创建布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        self.vBoxLayout.setSpacing(5)
        
        # 顶部和底部区域
        self.topLayout = QVBoxLayout()
        self.bottomLayout = QVBoxLayout()
        
        # 设置布局
        self.vBoxLayout.addLayout(self.topLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addLayout(self.bottomLayout)
        
        # 存储按钮
        self.buttons = {}
        self.current_item = None
        
        # 样式
        self.setStyleSheet("""
            #navigationBar {
                background-color: #f5f5f5;
                border-right: 1px solid #e0e0e0;
            }
        """)
        
    def addItem(self, routeKey, icon, text, onClick=None, selectedIcon=None, position=NavigationItemPosition.TOP, selectable=True):
        """ 添加导航项 """
        button = NavigationButton(icon, text, self)
        button.setObjectName(routeKey)
        
        if onClick:
            button.clicked.connect(onClick)
            
        if not selectable:
            button.setCheckable(False)
            
        # 根据位置添加到相应布局
        if position == NavigationItemPosition.TOP:
            self.topLayout.addWidget(button)
        else:
            self.bottomLayout.addWidget(button)
            
        self.buttons[routeKey] = button
        
    def setCurrentItem(self, routeKey):
        """ 设置当前项 """
        if routeKey in self.buttons and self.current_item != routeKey:
            if self.current_item and self.current_item in self.buttons:
                self.buttons[self.current_item].setChecked(False)
                
            self.buttons[routeKey].setChecked(True)
            self.current_item = routeKey


class SearchLineEdit(QLineEdit):
    """ 自定义搜索框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setClearButtonEnabled(True)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px 25px 4px 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)


class TitleBar(QWidget):
    """ 标题栏基类 """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.moving = False
        self.mousePos = None
        
        # 设置布局
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(0)
        
        # 最小化、最大化、关闭按钮
        self.minBtn = QPushButton("—", self)
        self.maxBtn = QPushButton("□", self)
        self.closeBtn = QPushButton("✕", self)
        
        # 样式设置
        self.minBtn.setFixedSize(45, 30)
        self.maxBtn.setFixedSize(45, 30)
        self.closeBtn.setFixedSize(45, 30)
        
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.minBtn)
        self.hBoxLayout.addWidget(self.maxBtn)
        self.hBoxLayout.addWidget(self.closeBtn)
        
        # 绑定信号
        self.minBtn.clicked.connect(self.parent.showMinimized)
        self.maxBtn.clicked.connect(self.toggleMaximize)
        self.closeBtn.clicked.connect(self.parent.close)
        
        # 样式
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QPushButton#closeBtn:hover {
                background-color: red;
                color: white;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.mousePos = event.globalPos() - self.parent.pos()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if self.moving and event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self.mousePos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self.moving = False
        
    def toggleMaximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()


class CustomTitleBar(TitleBar):
    """ 自定义标题栏 """
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.hBoxLayout.removeWidget(self.minBtn)
        self.hBoxLayout.removeWidget(self.maxBtn)
        self.hBoxLayout.removeWidget(self.closeBtn)

        # 添加窗口图标
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 20)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.window().windowIconChanged.connect(self.setIcon)

        # 添加标题标签
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

        # 添加搜索框
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
        if isinstance(icon, QIcon):
            self.iconLabel.setPixmap(icon.pixmap(18, 18))

    def resizeEvent(self, e):
        self.searchLineEdit.move((self.width() - self.searchLineEdit.width()) //2, 8)


class FramelessWindow(QWidget):
    """ 无边框窗口 """
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 主布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        
        # 默认标题栏
        self._titleBar = TitleBar(self)
        self.mainLayout.addWidget(self._titleBar)
        
        # 内容容器
        self.contentWidget = QWidget(self)
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.contentWidget)
        
        # 边框样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
            }
        """)
        
    def setTitleBar(self, titleBar):
        """ 设置自定义标题栏 """
        if self._titleBar:
            self.mainLayout.removeWidget(self._titleBar)
            self._titleBar.deleteLater()
            
        self._titleBar = titleBar
        self.mainLayout.insertWidget(0, titleBar)


class MessageBox(QDialog):
    """ 消息对话框 """
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 消息文本
        self.messageLabel = QLabel(text)
        self.messageLabel.setWordWrap(True)
        layout.addWidget(self.messageLabel)
        
        # 按钮
        self.buttonBox = QDialogButtonBox()
        self.yesButton = self.buttonBox.addButton("确定", QDialogButtonBox.YesRole)
        self.cancelButton = self.buttonBox.addButton("取消", QDialogButtonBox.NoRole)
        
        self.yesButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        layout.addWidget(self.buttonBox)
        
        # 样式
        self.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        self.hBoxLayout = QHBoxLayout(self.contentWidget)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)

        # 创建子界面
        self.homeInterface = Widget('Home Interface', self)
        self.appInterface = Widget('Application Interface', self)
        self.videoInterface = Widget('Video Interface', self)
        self.libraryInterface = Widget('library Interface', self)

        # 初始化布局
        self.initLayout()

        # 添加导航项
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FluentIcon.HOME, '主页', selectedIcon=FluentIcon.HOME_FILL)
        self.addSubInterface(self.appInterface, FluentIcon.APPLICATION, '应用')
        self.addSubInterface(self.videoInterface, FluentIcon.VIDEO, '视频')

        self.addSubInterface(self.libraryInterface, FluentIcon.BOOK_SHELF, '库', 
                           NavigationItemPosition.BOTTOM, FluentIcon.LIBRARY_FILL)
        self.navigationBar.addItem(
            routeKey='Help',
            icon=FluentIcon.HELP,
            text='帮助',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowTitle('PyQt5 Navigation Demo')
        
        # 只设置后备图标
        icon_path = os.path.join(os.path.dirname(__file__), "resource/icons/logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
        """ 添加子界面 """
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            selectedIcon=selectedIcon,
            position=position,
        )

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
