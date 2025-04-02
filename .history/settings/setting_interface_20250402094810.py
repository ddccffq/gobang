# coding:utf-8
import os
from config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, 
                            OptionsSettingCard, PushSettingCard,
                            ScrollArea, ComboBoxSettingCard, ExpandLayout, 
                            Theme, InfoBar, setTheme, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QApplication

# 添加导入历史记录管理器
from game_history_manager import GameHistoryManager


class SettingInterface(ScrollArea):
    """ 设置界面 """

    minimizeToTrayChanged = pyqtSignal(bool)
    historyDirChanged = pyqtSignal(str)  # 添加历史目录改变信号

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # 初始化历史记录管理器
        self.history_manager = GameHistoryManager()

        # 设置标签 - 直接使用中文
        self.settingLabel = QLabel("设置", self)

        # 游戏设置组
        self.gameSettingsGroup = SettingCardGroup("游戏设置", self.scrollWidget)
        self.historyDirCard = PushSettingCard(
            "选择文件夹",
            FIF.FOLDER,
            "历史记录保存路径",
            self.history_manager.history_dir,
            self.gameSettingsGroup
        )

        # 个性化组
        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "应用主题",
            "调整你的应用外观",
            texts=[
                "浅色", "深色", "跟随系统设置"
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            "语言",
            "选择界面所使用的语言",
            texts=["简体中文", "繁體中文", "English", "跟随系统设置"],
            parent=self.personalGroup
        )

        # 主面板
        self.mainPanelGroup = SettingCardGroup("主面板", self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            "关闭后最小化到托盘",
            "应用将在后台继续运行",
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # 初始化样式表
        self.__setQss()

        # 初始化布局
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 63)

        # 添加卡片到组
        self.gameSettingsGroup.addSettingCard(self.historyDirCard)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)

        # 添加设置卡片组到布局
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.gameSettingsGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 使用绝对路径加载样式表
        qss_path = os.path.join(current_dir, f'resource/qss/{theme}/setting_interface.qss')
        
        # 检查文件是否存在
        if os.path.exists(qss_path):
            with open(qss_path, encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            # 文件不存在时，尝试使用备用路径
            alternate_paths = [
                os.path.join(current_dir, f'resource/qss/{theme}/setting_interface.qss'),
                os.path.join(os.path.dirname(os.path.dirname(current_dir)), f'settings/resource/qss/{theme}/setting_interface.qss'),
                os.path.join(os.path.dirname(current_dir), f'resource/qss/{theme}/setting_interface.qss')
            ]
            
            for path in alternate_paths:
                if os.path.exists(path):
                    with open(path, encoding='utf-8') as f:
                        self.setStyleSheet(f.read())
                    break
            else:
                print(f"警告: 样式表文件未找到，使用内联样式")
                # 设置一个基本的内联样式
                self.setStyleSheet("""
                    #settingLabel {
                        font: 33px 'Microsoft YaHei Light';
                        background-color: transparent;
                    }
                """)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            '配置将在重启后生效',
            parent=self.window()
        )

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)
        
        # 让主题变化全局生效 - 应用到整个应用程序
        app = QApplication.instance()
        palette = app.palette()
        if theme == Theme.DARK:
            palette.setColor(QPalette.Window, QColor(32, 32, 32))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(42, 42, 42))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(52, 52, 52))
            palette.setColor(QPalette.ButtonText, Qt.white)
        else:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, Qt.white)
            palette.setColor(QPalette.ButtonText, Qt.black)
        app.setPalette(palette)
        
        # 更新设置界面样式
        self.__setQss()

    def __onHistoryDirClicked(self):
        """历史记录目录卡片点击事件"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择历史记录保存路径", 
            self.history_manager.history_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not directory:
            return
            
        # 尝试创建目录并更新设置
        try:
            os.makedirs(directory, exist_ok=True)
            self.history_manager.set_history_dir(directory)
            self.history_manager.save_settings()
            self.historyDirCard.setContent(directory)
            
            # 发出信号
            self.historyDirChanged.emit(directory)
            
            InfoBar.success(
                title='设置已更新',
                content="历史记录保存路径已更新",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,  # 修复：使用正确的 InfoBarPosition 常量
                duration=3000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title='路径错误',
                content=f"无法设置目录: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,  # 修复：使用正确的 InfoBarPosition 常量
                duration=3000,
                parent=self
            )

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # 历史记录目录
        self.historyDirCard.clicked.connect(self.__onHistoryDirClicked)

        # 主面板
        self.minimizeToTrayCard.checkedChanged.connect(
            self.minimizeToTrayChanged)
