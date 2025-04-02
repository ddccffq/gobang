# coding:utf-8
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices, QColor
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QStackedWidget

from qfluentwidgets import (NavigationBar, NavigationItemPosition, MessageBox,
                           isDarkTheme, FluentIcon as FIF)
from qframelesswindow import FramelessWindow, TitleBar

from interfaces import Widget, HomeInterface, SettingInterface, HistoryInterface
from board_view import BoardWidget


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

        # 添加一个伸缩器，将按钮推到右侧
        self.hBoxLayout.addStretch(1)

        # 重新添加窗口控制按钮到右侧
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
    """ 主窗口 """

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        # use dark theme mode
        # setTheme(Theme.DARK)

        # change the theme color
        # setThemeColor('#0078d4')

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = QStackedWidget(self)

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.appInterface = BoardWidget(self)
        self.historyInterface = HistoryInterface(self)
        self.settingInterface = SettingInterface(self)  # 使用设置界面替代库界面

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

        # 设置支持亚克力效果
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # 检查是否应该启用亚克力效果
        from config import cfg
        if cfg.get(cfg.enableAcrylicBackground):
            self.enableAcrylicEffect()

        # 获取配置模块并连接主题变更信号到全局刷新方法
        cfg.themeChanged.connect(self.onThemeChanged)

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', selectedIcon=FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.GAME, '五子棋游戏')
        self.addSubInterface(self.historyInterface, FIF.HISTORY, '历史对局')

        # 替换原本的库界面为设置界面
        self.addSubInterface(
            self.settingInterface, 
            FIF.SETTING, 
            '设置', 
            NavigationItemPosition.BOTTOM
        )
        
        # 帮助按钮
        self.navigationBar.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='帮助',
            onClick=lambda: None,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(1000, 800)  # 从900x700增加到1000x800
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('五子棋游戏')  # 更改窗口标题
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
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
        
        # 创建一个资源目录列表，从多个位置查找样式表
        resource_dirs = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'settings', 'resource')
        ]
        
        color = 'dark' if isDarkTheme() else 'light'
        qss_file = None
        
        # 尝试从不同位置找到样式表
        for dir_path in resource_dirs:
            test_path = os.path.join(dir_path, f'{color}/demo.qss')
            if os.path.exists(test_path):
                qss_file = test_path
                break
        
        # 如果找到样式表，则应用它
        if qss_file:
            with open(qss_file, encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"样式表文件未找到")
            # 设置一个默认内联样式
            self.setStyleSheet("")

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    def onThemeChanged(self, theme):
        """响应主题变更，更新所有界面样式"""
        # 更新主窗口样式
        self.setQss()
        
        # 更新各个子界面样式
        for interface in [self.homeInterface, self.appInterface, self.historyInterface, self.settingInterface]:
            if hasattr(interface, 'updateStyle'):
                interface.updateStyle()
            
        # 刷新全部界面
        self.update()
        
        # 通知用户主题已更改
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.success(
            title='主题已更改',
            content=f"已切换至{'深色' if isDarkTheme() else '浅色'}主题",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def enableAcrylicEffect(self):
        """启用模拟亚克力效果（不使用AcrylicBrush）"""
        try:
            # 根据当前主题选择合适的效果颜色
            if isDarkTheme():
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setStyleSheet("""
                    QMainWindow {
                        background-color: rgba(32, 32, 32, 200);
                    }
                """)
            else:
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setStyleSheet("""
                    QMainWindow {
                        background-color: rgba(245, 245, 245, 220);
                    }
                """)
            
        except Exception as e:
            print(f"无法启用半透明效果: {e}")
            
    def disableAcrylicEffect(self):
        """禁用半透明效果"""
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        if isDarkTheme():
            self.setStyleSheet("background-color: rgb(32, 32, 32);")
        else:
            self.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.update()

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