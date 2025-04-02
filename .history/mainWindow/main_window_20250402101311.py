# coding:utf-8
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices, QColor
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QStackedWidget, QSystemTrayIcon, QMenu, QAction

from qfluentwidgets import (NavigationBar, NavigationItemPosition, MessageBox,
                           isDarkTheme, FluentIcon as FIF)
from qframelesswindow import FramelessWindow, TitleBar

# 修改为基于包结构的导入
from mainWindow.interfaces import Widget, HomeInterface, SettingInterface, HistoryInterface, BoardWidget
from mainWindow.config import cfg


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

        # 创建系统托盘图标
        self.trayIcon = None
        self.setupTrayIcon()

        # 获取配置模块并连接主题变更信号和托盘设置变更信号
        cfg.themeChanged.connect(self.onThemeChanged)
        
        # 连接设置界面的托盘设置信号
        self.settingInterface.minimizeToTrayChanged.connect(self.onMinimizeToTrayChanged)

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
        self.resize(1000, 800)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('五子棋游戏')
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
        """加载并应用全局样式表"""
        import os
        
        # 创建一个资源目录列表，从多个位置查找样式表
        resource_dirs = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'settings', 'resource')
        ]
        
        # 根据当前主题选择样式表目录
        theme_folder = 'dark' if isDarkTheme() else 'light'
        
        # 首先加载通用样式表
        common_qss = ""
        for dir_path in resource_dirs:
            test_path = os.path.join(dir_path, f'qss/{theme_folder}/common.qss')
            if os.path.exists(test_path):
                with open(test_path, encoding='utf-8') as f:
                    common_qss = f.read()
                break
        
        # 然后加载特定界面样式表
        demo_qss = ""
        for dir_path in resource_dirs:
            test_path = os.path.join(dir_path, f'qss/{theme_folder}/demo.qss')
            if os.path.exists(test_path):
                with open(test_path, encoding='utf-8') as f:
                    demo_qss = f.read()
                break
        
        # 应用样式表 - 先应用通用样式，再应用特定样式
        if common_qss or demo_qss:
            self.setStyleSheet(common_qss + "\n" + demo_qss)
        else:
            print(f"警告: 样式表文件未找到")
            # 设置一个默认内联样式
            self.setStyleSheet("")

        # 将样式应用到所有子界面
        for interface in [self.homeInterface, self.appInterface, self.historyInterface, self.settingInterface]:
            if hasattr(interface, 'setStyleSheet'):
                interface.setStyleSheet(common_qss)

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

    def setupTrayIcon(self):
        """设置系统托盘图标"""
        # 创建托盘图标
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(':/qfluentwidgets/images/logo.png'))  
        self.trayIcon.setToolTip('五子棋游戏')
        
        # 创建托盘菜单
        trayMenu = QMenu()
        
        # 添加显示窗口操作
        showAction = QAction('显示主窗口', self)
        showAction.triggered.connect(self.showNormal)
        trayMenu.addAction(showAction)
        
        # 添加分隔线
        trayMenu.addSeparator()
        
        # 添加退出操作
        quitAction = QAction('退出', self)
        quitAction.triggered.connect(self.quitApplication)
        trayMenu.addAction(quitAction)
        
        # 设置托盘菜单
        self.trayIcon.setContextMenu(trayMenu)
        
        # 托盘图标双击显示窗口
        self.trayIcon.activated.connect(self.onTrayIconActivated)
        
        # 根据配置决定是否启用托盘图标
        if cfg.get(cfg.minimizeToTray):
            self.trayIcon.show()

    def onMinimizeToTrayChanged(self, enable):
        """响应最小化到托盘设置变更"""
        if enable and self.trayIcon:
            self.trayIcon.show()
        elif self.trayIcon:
            self.trayIcon.hide()

    def onTrayIconActivated(self, reason):
        """响应托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def quitApplication(self):
        """完全退出应用程序"""
        # 隐藏托盘图标，避免图标残留
        if self.trayIcon:
            self.trayIcon.hide()
        # 调用应用程序的quit方法
        QApplication.quit()

    def closeEvent(self, event):
        """重写关闭事件，实现最小化到托盘"""
        if cfg.get(cfg.minimizeToTray) and self.trayIcon and self.trayIcon.isVisible():
            event.ignore()  # 忽略关闭事件
            
            # 显示托盘提示
            self.trayIcon.showMessage(
                '五子棋游戏', 
                '程序已最小化到系统托盘，双击托盘图标可再次打开窗口', 
                QSystemTrayIcon.Information, 
                2000
            )
            
            # 隐藏主窗口
            self.hide()
        else:
            # 不使用托盘则正常关闭
            super().closeEvent(event)