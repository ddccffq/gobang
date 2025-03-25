# coding:utf-8
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication

from qfluentwidgets import (NavigationBar, NavigationItemPosition, MessageBox,
                           isDarkTheme, FluentIcon as FIF)
from qframelesswindow import FramelessWindow, TitleBar

from interfaces import Widget, AppInterface, StackedWidget, LibraryInterface, HomeInterface


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

        # ���һ��������������ť�Ƶ��Ҳ�
        self.hBoxLayout.addStretch(1)

        # ������Ӵ��ڿ��ư�ť���Ҳ�
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(0)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setAlignment(Qt.AlignTop)
        self.buttonLayout.addWidget(self.minBtn)
        self.buttonLayout.addWidget(self.maxBtn)
        self.buttonLayout.addWidget(self.closeBtn)
        self.hBoxLayout.addLayout(self.buttonLayout)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))


class Window(FramelessWindow):
    """ ������ """

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
        self.homeInterface = HomeInterface(self)  # ʹ���µ�HomeInterface
        self.appInterface = Widget('App Interface', self)
        self.libraryInterface = LibraryInterface(self)  # ʹ���µ�LibraryInterface

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
        self.addSubInterface(self.homeInterface, FIF.HOME, '��ҳ', selectedIcon=FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.APPLICATION, 'Ӧ��')

        self.addSubInterface(self.libraryInterface, FIF.BOOK_SHELF, '��', NavigationItemPosition.BOTTOM, FIF.LIBRARY_FILL)
        
        # ��������ť�޸�Ϊ�޲���
        self.navigationBar.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='����',
            onClick=lambda: None,  # �޲�������������
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
        
        # ����ļ��Ƿ����
        if os.path.exists(qss_file):
            with open(qss_file, encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"��ʽ���ļ�������: {qss_file}")
            # ��������һ��Ĭ�ϵ�������ʽ
            self.setStyleSheet("")

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox(
            '֧������?',
            '���˿������ף���������Ŀ���������������Կ��������ߺ�һƿ����ˮ?������֧�־������߿�����ά����Ŀ�Ķ���?',
            self
        )
        w.yesButton.setText('�����ϵ�')
        w.cancelButton.setText('�´�һ��')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))